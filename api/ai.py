from fastapi import APIRouter
from fastapi.responses import JSONResponse
from train import train_agent 
from typing import Tuple, Dict, List
from models.battle import PokemonBattleState
from ai.ai_selection import select_ai_pokemon
from models.pokemon import get_pokemon_data

router = APIRouter()

@router.post("/train")
def train_rl_agent():
    # Handle all 3 return values from train_agent
    episode_rewards, epsilon_history, win_count = train_agent()
    return {
        "message": "Training completed",
        "total_episodes": len(episode_rewards),
        "win_rate": win_count / len(episode_rewards) if episode_rewards else 0,
        "final_win_count": win_count,
        "episode_rewards": episode_rewards,
        "epsilon_history": epsilon_history
    }

# Stores active battles
battles: Dict[str, Dict[str, dict]] = {}

def get_battle_state(battle_id: str) -> dict:
    """Retrieve the battle state for the given battle_id."""
    return battles.get(battle_id)

def apply_moves(battle_id: str, player_move: str, ai_move: str) -> Tuple[PokemonBattleState, PokemonBattleState, List[dict]]:
    """
    Apply both moves to the battle state with basic damage logic.
    """
    battle = battles[battle_id]

    player = PokemonBattleState(**battle["player"])
    ai = PokemonBattleState(**battle["ai"])

    turn_log = []

    # Very basic damage calculation — you could hook your utils/damage.py here
    def calculate_damage(attacker: PokemonBattleState, defender: PokemonBattleState) -> float:
        base_damage = attacker.attack - (defender.defense * 0.5)
        return max(1, base_damage)  # Ensure at least 1 damage

    # Player attacks AI
    damage_to_ai = calculate_damage(player, ai)
    ai.hp -= damage_to_ai
    turn_log.append({
        "attacker": player.name,
        "defender": ai.name,
        "move": player_move,
        "damage": damage_to_ai
    })

    # AI attacks Player (if still alive)
    if not ai.is_fainted():
        damage_to_player = calculate_damage(ai, player)
        player.hp -= damage_to_player
        turn_log.append({
            "attacker": ai.name,
            "defender": player.name,
            "move": ai_move,
            "damage": damage_to_player
        })

    # Save updated state back to memory
    battles[battle_id] = {
        "player": player.dict(),
        "ai": ai.dict()
    }

    return player, ai, turn_log

@router.post("/ai_move")
async def get_ai_move(data: dict):
    ai_pokemon = get_pokemon_data(**data['ai_pokemon'])
    player_pokemon = get_pokemon_data(**data['player_pokemon'])
    available_moves = data['available_moves']
    
    selected_move = select_ai_pokemon(ai_pokemon, player_pokemon, available_moves)
    return {"selected_move": selected_move}