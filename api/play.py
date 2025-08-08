from __future__ import annotations

import random
import uuid
from typing import List, Dict, Any, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field

from ai.rl_agent import QLearningAgent
from dependencies import get_agent
from api import battle_api
from models.battle import PokemonBattleState
from services.battle_simulator import BattleSimulator

router = APIRouter()

# =========================
# Config: Heuristic control
# =========================
# Make the AI deterministic and strong by default.
HEURISTIC_EPSILON: float = 0.0   # 0.25 previously — now no random exploration in heuristic
HEURISTIC_WEIGHT:  float = 1.0   # 0.7 previously — now always favor heuristic over RL

# =========================
# Minimal type chart & moves
# =========================
TYPE_EFFECTIVENESS: Dict[str, Dict[str, float]] = {
    "fire":    {"grass": 2.0, "water": 0.5, "fire": 0.5},
    "water":   {"fire": 2.0, "grass": 0.5, "water": 0.5, "rock": 2.0, "ground": 2.0},
    "grass":   {"water": 2.0, "fire": 0.5, "grass": 0.5, "rock": 2.0, "ground": 2.0},
    "psychic": {"fighting": 2.0, "poison": 2.0},
    "flying":  {"grass": 2.0, "fighting": 2.0, "bug": 2.0, "rock": 0.5, "electric": 0.5},
    "dark":    {"psychic": 2.0, "ghost": 2.0},
    "normal":  {},
}

# move_name -> (type, base_power)
MOVE_BOOK: Dict[str, Tuple[str, int]] = {
    "water gun": ("water", 40),
    "tackle": ("normal", 40),
    "bite": ("dark", 60),

    "vine whip": ("grass", 45),
    "razor leaf": ("grass", 55),
    "sleep powder": ("grass", 0),  # status-only

    "psybeam": ("psychic", 65),
    "confusion": ("psychic", 50),
    "recover": ("psychic", 0),     # status/heal

    "ember": ("fire", 40),
    "wing attack": ("flying", 60),
    "slash": ("normal", 70),
}

# =========================
# AI roster candidates
# =========================
AI_POKEMON_POOL: List[Dict[str, Any]] = [
    {
        "name": "blastoise",
        "types": ["water"],
        "hp": 79, "attack": 83, "defense": 100, "speed": 78,
        "available_moves": ["water gun", "tackle", "bite"],
    },
    {
        "name": "venusaur",
        "types": ["grass", "poison"],
        "hp": 80, "attack": 82, "defense": 83, "speed": 80,
        "available_moves": ["vine whip", "razor leaf", "sleep powder"],
    },
    {
        "name": "alakazam",
        "types": ["psychic"],
        "hp": 55, "attack": 50, "defense": 45, "speed": 120,
        "available_moves": ["psybeam", "confusion", "recover"],
    },
]

# =========================
# Request models
# =========================
class PlayerPokemonIn(BaseModel):
    name: str
    types: List[str]
    hp: float
    attack: int
    defense: int
    speed: int
    available_moves: List[str] = Field(default_factory=list)
    status: Optional[str] = None


# =========================
# Helper functions
# =========================
def type_multiplier(move_type: str, defender_types: List[str]) -> float:
    mult = 1.0
    for t in defender_types:
        mult *= TYPE_EFFECTIVENESS.get(move_type, {}).get(t, 1.0)
    return mult


# Better AI pokemon selection considering both offense and defense
def choose_best_ai_pokemon(player_types: List[str]) -> Dict[str, Any]:
    """
    Pick an AI Pokémon with good type matchup vs the player.
    Consider both offensive advantage (AI attacks player) and defensive advantage (resisting player attacks).
    """
    best = None
    best_score = -1.0
    
    for cand in AI_POKEMON_POOL:
        offensive_score = 1.0
        defensive_score = 1.0
        
        # Calculate offensive advantage (AI attacking player)
        for ai_type in cand["types"]:
            for pt in player_types:
                offensive_score *= TYPE_EFFECTIVENESS.get(ai_type, {}).get(pt, 1.0)
        
        # Calculate defensive advantage (player attacking AI)
        # We want LOW multipliers here (resistance), so we invert the score
        for pt in player_types:
            for ai_type in cand["types"]:
                player_effectiveness = TYPE_EFFECTIVENESS.get(pt, {}).get(ai_type, 1.0)
                # Invert: 2x becomes 0.5, 0.5x becomes 2, 1x stays 1
                if player_effectiveness > 1.0:
                    defensive_score *= 0.5  # We're weak to player
                elif player_effectiveness < 1.0:
                    defensive_score *= 2.0  # We resist player
        
        # Combined score (both offense and defense matter)
        total_score = offensive_score * defensive_score
        
        if total_score > best_score:
            best = cand
            best_score = total_score
            
    return best or random.choice(AI_POKEMON_POOL)


def choose_ai_move_epsilon_greedy(
    ai_state: PokemonBattleState,
    opp_types: List[str],
    epsilon: float = HEURISTIC_EPSILON
) -> str:
    """
    Heuristic move selection with optional epsilon exploration.
    Adds STAB and a small bias for higher-power moves.
    Deterministic when epsilon=0.0.
    """
    legal = ai_state.available_moves or []
    if not legal:
        return "tackle"

    if random.random() < epsilon:
        return random.choice(legal)

    best_move, best_score = None, float("-inf")
    for m in legal:
        mtype, mpower = MOVE_BOOK.get(m, ("normal", 40))
        score = mpower * type_multiplier(mtype, opp_types)

        # STAB: same-type attack bonus
        if mtype in ai_state.types:
            score *= 1.5

        # Slight bias toward higher power (proxy for KO-bias without accuracy data)
        if mpower >= 60:
            score *= 1.05

        if score > best_score:
            best_move, best_score = m, score

    return best_move or random.choice(legal)


def canonicalize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make a dict stable for hashing by the agent's Q-table keys by turning lists/dicts into tuples.
    Added error handling for non-comparable values.
    """
    out: Dict[str, Any] = {}
    for k, v in state.items():
        try:
            if isinstance(v, list):
                out[k] = tuple(v)
            elif isinstance(v, dict):
                # Only sort if all values are comparable
                try:
                    out[k] = tuple(sorted(v.items()))
                except TypeError:
                    # If values aren't comparable, just use items() without sorting
                    out[k] = tuple(v.items())
            else:
                out[k] = v
        except (TypeError, ValueError):
            # If anything fails, convert to string as fallback
            out[k] = str(v)
    return out


# =========================
# Routes
# =========================
@router.post("/start")
def start_battle(
    player: PlayerPokemonIn = Body(description="Player Pokémon as JSON")
):
    """
    Start a battle by sending the player's Pokémon JSON.

    Example body:
    {
      "name":"charizard", "types":["fire","flying"],
      "hp":78, "attack":84, "defense":78, "speed":100,
      "available_moves":["ember","wing attack","slash"]
    }
    """
    battle_id = str(uuid.uuid4())

    ai_pick = choose_best_ai_pokemon(player.types)

    player_state = PokemonBattleState.from_pokemon_info(player.model_dump())
    ai_state = PokemonBattleState.from_pokemon_info(ai_pick)

    battle_api.battles[battle_id] = {
        "player": player_state.dict(),
        "ai": ai_state.dict(),
    }

    return {
        "battle_id": battle_id,
        "ai_selected": ai_pick["name"],
        "player": player_state.dict(),
        "ai": ai_state.dict(),
    }


@router.post("/{battle_id}/move")
def make_move(
    battle_id: str,
    player_move: str = Query(..., description="Move chosen by the player"),
    agent: QLearningAgent = Depends(get_agent),
):
    """
    Play one turn:
      - Loads current battle state
      - Chooses AI move (deterministic heuristic by default)
      - Runs a one-turn simulation (status, type, STAB included)
      - Persists updated HP/status
    """
    if agent is None:
        raise HTTPException(status_code=500, detail="AI agent not loaded.")
    if battle_id not in battle_api.battles:
        raise HTTPException(status_code=404, detail="Battle not found.")

    current = battle_api.battles[battle_id]
    try:
        player_state = PokemonBattleState(**current["player"])
        ai_state = PokemonBattleState(**current["ai"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid stored state: {e}")

    if player_state.is_fainted() or ai_state.is_fainted():
        winner = "ai" if player_state.is_fainted() else "player"
        return {"message": "Battle already ended.", "winner": winner}

    # Build one-turn simulator from current state snapshot
    sim = BattleSimulator(player_state.dict(), ai_state.dict())

    # Ensure RL agent has valid moves matching available moves
    sim_legal = sim.p2.available_moves or ["tackle"]
    if sim_legal:
        # Update agent actions to match current legal moves
        agent.actions = sim_legal

    # RL proposal (unused if HEURISTIC_WEIGHT==1, but kept for future toggling)
    rl_choice = None
    try:
        rl_state = canonicalize_state(sim.p2.dict())
        rl_choice = agent.choose_action(rl_state)
        if rl_choice not in sim_legal and sim_legal:
            rl_choice = random.choice(sim_legal)
    except Exception:
        if sim_legal:
            rl_choice = random.choice(sim_legal)

    # Heuristic proposal (deterministic with epsilon=0)
    heuristic_choice = choose_ai_move_epsilon_greedy(sim.p2, sim.p1.types, epsilon=HEURISTIC_EPSILON)

    # Blend: with HEURISTIC_WEIGHT=1.0 this always selects heuristic_choice
    if random.random() < HEURISTIC_WEIGHT or rl_choice is None:
        ai_move = heuristic_choice
        policy = "heuristic"
    else:
        ai_move = rl_choice
        policy = "rl"

    # Use the proper execute_turn method that returns structured log
    try:
        turn_log = sim.execute_turn(player_move, ai_move)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Battle execution error: {e}")

    # Pull back updated states from simulator
    player_state = sim.p1
    ai_state = sim.p2

    # Persist
    battle_api.battles[battle_id] = {
        "player": player_state.dict(),
        "ai": ai_state.dict(),
    }

    return {
        "battle_id": battle_id,
        "turn_log": turn_log,
        "player": player_state.dict(),
        "ai": ai_state.dict(),
        "ai_reasoning": {
            "policy": policy,
            "epsilon": HEURISTIC_EPSILON,
            "heuristic_weight": HEURISTIC_WEIGHT,
            "note": "Deterministic heuristic with STAB and type effectiveness" if policy == "heuristic" else "RL fallback",
        },
    }