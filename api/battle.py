from fastapi import APIRouter, Query, HTTPException
import random
from models.battle import PokemonBattleState
from services.data_fetcher import fetch_pokemon_data
from services.battle_simulator import BattleSimulator

router = APIRouter()

def flatten_pokemon_info(info: dict) -> dict:
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

@router.post("/", response_model=dict)
async def simulate_battle(
    pokemon1: str = Query(..., description="Name of the first Pokémon"),
    pokemon2: str = Query(..., description="Name of the second Pokémon"),
):
    # Fetch Pokémon data asynchronously
    p1_info = await fetch_pokemon_data(pokemon1)
    p2_info = await fetch_pokemon_data(pokemon2)

    if not p1_info or not p2_info:
        raise HTTPException(status_code=404, detail="One or both Pokémon not found")

    # Convert to dict and flatten stats for BattleSimulator
    p1_flat = flatten_pokemon_info(p1_info.dict())
    p2_flat = flatten_pokemon_info(p2_info.dict())

    # Initialize simulator
    simulator = BattleSimulator(p1_flat, p2_flat)

    battle_log = []
    max_turns = 20
    winner = None

    for turn in range(max_turns):
        # Choose moves randomly (replace with AI or user input as needed)
        p1_move = random.choice(simulator.p1.available_moves)
        p2_move = random.choice(simulator.p2.available_moves)

        damage_done, damage_taken = simulator.execute_turn_with_moves(p1_move, p2_move)

        battle_log.append({
            "turn": turn + 1,
            "p1_move": p1_move,
            "p2_move": p2_move,
            "p1_hp": simulator.p1.hp,
            "p2_hp": simulator.p2.hp,
            "damage_done": damage_done,
            "damage_taken": damage_taken,
        })

        winner = simulator.get_winner()
        if winner is not None:
            break

    return {
        "battle_log": battle_log,
        "winner": winner
    }
