from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, List
import random
from models.battle import PokemonBattleState  
from services.data_fetcher import fetch_pokemon_data
from services.battle_simulator import BattleSimulator
import dependencies 

router = APIRouter()

def flatten_pokemon_info(info: Dict[str, Any]) -> Dict[str, Any]:
    stats = info.get("stats", {})
    return {
        "name": info.get("name"),
        "types": info.get("types", []),
        "hp": stats.get("hp"),
        "max_hp": stats.get("hp"),
        "attack": stats.get("attack"),
        "defense": stats.get("defense"),
        "speed": stats.get("speed"),
        "available_moves": info.get("moves", []),
        "status": info.get("status"),
    }

def filter_damaging_moves(moves, simulator, player):
    if player == "p1":
        attacker = simulator.p1
        defender = simulator.p2
    else:
        attacker = simulator.p2
        defender = simulator.p1

    damaging = [move for move in moves if simulator.is_damaging_move(attacker, defender, move)]
    return damaging if damaging else moves

@router.post("/simulate", response_model=Dict)
async def simulate_battle_with_ai(
    pokemon1: str = Query(..., description="Name of the first Pokémon"),
    pokemon2: str = Query(..., description="Name of the second Pokémon"),
):
    # Fetch Pokémon data asynchronously
    p1_info_raw = await fetch_pokemon_data(pokemon1)
    p2_info_raw = await fetch_pokemon_data(pokemon2)

    if not p1_info_raw or not p2_info_raw:
        raise HTTPException(status_code=404, detail="One or both Pokémon not found")

    # Convert to dict and flatten stats for BattleSimulator
    p1_info = flatten_pokemon_info(p1_info_raw.dict())
    p2_info = flatten_pokemon_info(p2_info_raw.dict())

    # Initialize simulator
    simulator = BattleSimulator(p1_info, p2_info)

    battle_log = []
    max_turns = 20
    winner = None

    # Get AI agents for both players
    agent1 = dependencies.agent_instance
    agent2 = dependencies.agent_instance  

    if agent1 is None:
        raise HTTPException(status_code=500, detail="AI agent for player 1 not loaded.")
    if agent2 is None:
        print("AI agent for player 2 not loaded; using random moves.")

    for turn in range(max_turns):
        # Prepare state for AI (expand as needed)
        state_for_ai = {
            "p1_hp": simulator.p1.hp,
            "p1_status": simulator.p1.status,
            "p2_hp": simulator.p2.hp,
            "p2_status": simulator.p2.status,
            # Add more features your AI needs
        }

        # Filter damaging moves for both players
        p1_moves = filter_damaging_moves(simulator.p1.available_moves, simulator, 'p1')
        p2_moves = filter_damaging_moves(simulator.p2.available_moves, simulator, 'p2')

        # Player 1 move
        p1_move = agent1.choose_action(state_for_ai)
        if p1_move not in p1_moves:
            p1_move = random.choice(p1_moves)

        # Player 2 move
        if agent2:
            p2_move = agent2.choose_action(state_for_ai)
            if p2_move not in p2_moves:
                p2_move = random.choice(p2_moves)
        else:
            p2_move = random.choice(p2_moves)

        # Execute turn
        damage_done, damage_taken = simulator.execute_turn_with_moves(p1_move, p2_move)

        # Log full details
        battle_log.append({
            "turn": turn + 1,
            "player1": simulator.p1.name,
            "player2": simulator.p2.name,
            "p1_move": p1_move,
            "p2_move": p2_move,
            "p1_hp": simulator.p1.hp,
            "p2_hp": simulator.p2.hp,
            "damage_done": damage_done,
            "damage_taken": damage_taken,
            "p1_status": simulator.p1.status,
            "p2_status": simulator.p2.status,
        })

        winner = simulator.get_winner()
        if winner is not None:
            break

    return {
        "battle_log": battle_log,
        "players": {
            "player1": simulator.p1.name,
            "player2": simulator.p2.name,
        },
        "winner": winner
    }
