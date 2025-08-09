"""
Battle system diagnostics - test the battle simulator and check for issues
"""
import json
from battle_simulator import BattleSimulator
from data_fetcher import fetch_pokemon_data
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_battle():
    """Test a basic battle with manual Pokemon data"""
    print("=== Testing Basic Battle Mechanics ===\n")
    
    # Create test Pokemon with known stats
    pikachu_data = {
        "name": "pikachu",
        "types": ["electric"],
        "hp": 35,
        "max_hp": 35,
        "attack": 55,
        "defense": 40,
        "speed": 90,
        "available_moves": ["thunder-shock", "quick-attack", "tackle"],
        "status": None
    }
    
    bulbasaur_data = {
        "name": "bulbasaur", 
        "types": ["grass", "poison"],
        "hp": 45,
        "max_hp": 45,
        "attack": 49,
        "defense": 49,
        "speed": 45,
        "available_moves": ["vine-whip", "tackle", "growl"],
        "status": None
    }
    
    # Create simulator
    simulator = BattleSimulator(pikachu_data, bulbasaur_data)
    
    print(f"P1 (Pikachu): HP={simulator.p1.hp}, Attack={simulator.p1.attack}, Defense={simulator.p1.defense}")
    print(f"P1 Moves: {simulator.p1.available_moves}")
    print(f"P1 Status: {simulator.p1.status} (type: {type(simulator.p1.status)})")
    
    print(f"\nP2 (Bulbasaur): HP={simulator.p2.hp}, Attack={simulator.p2.attack}, Defense={simulator.p2.defense}")
    print(f"P2 Moves: {simulator.p2.available_moves}")
    print(f"P2 Status: {simulator.p2.status} (type: {type(simulator.p2.status)})")
    
    # Test single turn
    print(f"\n=== Turn 1: Thunder Shock vs Vine Whip ===")
    turn_log = simulator.execute_turn("thunder-shock", "vine-whip")
    
    print("\nTurn Log:")
    for event in turn_log:
        print(f"  {event}")
    
    print(f"\nAfter Turn 1:")
    print(f"  Pikachu HP: {simulator.p1.hp} (Status: {simulator.p1.status})")
    print(f"  Bulbasaur HP: {simulator.p2.hp} (Status: {simulator.p2.status})")
    
    # Check type effectiveness
    print(f"\n=== Type Effectiveness Check ===")
    electric_vs_grass = simulator.calculate_type_effectiveness("electric", ["grass", "poison"])
    print(f"Electric vs Grass/Poison: {electric_vs_grass}x")
    
    grass_vs_electric = simulator.calculate_type_effectiveness("grass", ["electric"])
    print(f"Grass vs Electric: {grass_vs_electric}x")
    
    # Test damage calculation
    print(f"\n=== Damage Calculation Test ===")
    thunder_shock_damage = simulator.calculate_damage(simulator.p1, simulator.p2, "thunder-shock")
    vine_whip_damage = simulator.calculate_damage(simulator.p2, simulator.p1, "vine-whip")
    
    print(f"Thunder Shock damage: {thunder_shock_damage}")
    print(f"Vine Whip damage: {vine_whip_damage}")

def test_status_serialization():
    """Test how status values are being serialized"""
    print(f"\n=== Status Serialization Test ===")
    
    from models.battle import PokemonBattleState
    
    # Test with None status
    pokemon_none = PokemonBattleState(
        name="test",
        types=["normal"],
        hp=50,
        max_hp=50,
        attack=50,
        defense=50,
        speed=50,
        available_moves=["tackle"],
        status=None
    )
    
    print(f"Pokemon with None status:")
    print(f"  status value: {pokemon_none.status}")
    print(f"  status type: {type(pokemon_none.status)}")
    print(f"  dict representation: {pokemon_none.dict()['status']}")
    print(f"  JSON: {json.dumps(pokemon_none.dict()['status'])}")
    
    # Test with string status
    pokemon_burn = PokemonBattleState(
        name="test",
        types=["normal"],
        hp=50,
        max_hp=50,
        attack=50,
        defense=50,
        speed=50,
        available_moves=["tackle"],
        status="burn"
    )
    
    print(f"\nPokemon with burn status:")
    print(f"  status value: {pokemon_burn.status}")
    print(f"  status type: {type(pokemon_burn.status)}")
    print(f"  dict representation: {pokemon_burn.dict()['status']}")
    print(f"  JSON: {json.dumps(pokemon_burn.dict()['status'])}")

async def test_api_pokemon_moves():
    """Test what moves Pokemon actually get from the API"""
    print(f"\n=== API Pokemon Moves Test ===")
    
    try:
        pikachu = await fetch_pokemon_data("pikachu")
        if pikachu:
            print(f"Pikachu from API:")
            print(f"  Types: {pikachu.types}")
            print(f"  First 10 moves: {pikachu.moves[:10]}")
            print(f"  Has surf? {'surf' in pikachu.moves}")
            print(f"  Has thunder-shock? {'thunder-shock' in pikachu.moves}")
            print(f"  Has thunderbolt? {'thunderbolt' in pikachu.moves}")
        
        bulbasaur = await fetch_pokemon_data("bulbasaur")
        if bulbasaur:
            print(f"\nBulbasaur from API:")
            print(f"  Types: {bulbasaur.types}")
            print(f"  First 10 moves: {bulbasaur.moves[:10]}")
            print(f"  Has vine-whip? {'vine-whip' in bulbasaur.moves}")
            print(f"  Has razor-leaf? {'razor-leaf' in bulbasaur.moves}")
    except Exception as e:
        print(f"Error fetching Pokemon data: {e}")

def test_move_filtering():
    """Test the move filtering logic in battle.py"""
    print(f"\n=== Move Filtering Test ===")
    
    from services.battle_simulator import BattleSimulator
    
    # Create test data
    pikachu_data = {
        "name": "pikachu",
        "types": ["electric"], 
        "hp": 35,
        "attack": 55,
        "defense": 40,
        "speed": 90,
        "available_moves": ["surf", "thunder-shock", "tackle", "quick-attack"],
        "status": None
    }
    
    bulbasaur_data = {
        "name": "bulbasaur",
        "types": ["grass", "poison"],
        "hp": 45,
        "attack": 49, 
        "defense": 49,
        "speed": 45,
        "available_moves": ["vine-whip", "tackle", "sleep-powder"],
        "status": None
    }
    
    simulator = BattleSimulator(pikachu_data, bulbasaur_data)
    
    # Test damaging move detection
    print("Testing damaging move detection:")
    for move in pikachu_data["available_moves"]:
        is_damaging = simulator.is_damaging_move(simulator.p1, simulator.p2, move)
        move_data = simulator.move_data.get(move, {})
        power = move_data.get("power", 0)
        print(f"  {move}: damaging={is_damaging}, power={power}")

async def main():
    """Run all diagnostic tests"""
    print("🔍 Battle System Diagnostics\n")
    
    test_basic_battle()
    test_status_serialization() 
    await test_api_pokemon_moves()
    test_move_filtering()
    
    print(f"\n✅ Diagnostics complete!")

if __name__ == "__main__":
    asyncio.run(main())