import random
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from models.battle import PokemonBattleState

class BattleSimulator:
    """Enhanced battle simulator with comprehensive move effects and status conditions."""
    def __init__(self, p1_info: Dict[str, Any], p2_info: Dict[str, Any], debug: bool = False):
        self.p1 = PokemonBattleState.from_pokemon_info(p1_info)
        self.p2 = PokemonBattleState.from_pokemon_info(p2_info)
        
        # Load type chart
        type_chart_path = Path(__file__).parent.parent / "data" / "type_chart.json"
        try:
            with open(type_chart_path, "r") as f:
                self.type_chart = json.load(f)
        except FileNotFoundError:
            if debug:
                print("Warning: type_chart.json not found, using simplified chart")
            self.type_chart = self._get_simplified_type_chart()

        # Comprehensive move database
        self.move_data = self._get_move_database()
        
        # Set default moves if none provided
        self._set_default_moves()
        
        # Battle state tracking
        self.turn_count = 0
        self.battle_history: List[Dict[str, Any]] = []
        
        # Debug initialization
        if debug:
            self._debug_initialization()

    def _debug_initialization(self):
        """Debug battle initialization."""
        print("=== BATTLE INITIALIZATION DEBUG ===")
        issues = self.validate_pokemon_moves(debug_mode=True)
        if issues:
            print("ISSUES FOUND:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("All moves validated successfully")

    def _get_simplified_type_chart(self) -> Dict[str, Dict[str, float]]:
        """Simplified type chart as fallback."""
        return {
            "fire": {"grass": 2.0, "water": 0.5, "fire": 0.5, "ice": 2.0, "bug": 2.0, "steel": 2.0},
            "water": {"fire": 2.0, "grass": 0.5, "water": 0.5, "rock": 2.0, "ground": 2.0},
            "grass": {"water": 2.0, "fire": 0.5, "grass": 0.5, "rock": 2.0, "ground": 2.0},
            "electric": {"water": 2.0, "flying": 2.0, "ground": 0.0, "electric": 0.5},
            "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0},
            "flying": {"grass": 2.0, "fighting": 2.0, "bug": 2.0, "rock": 0.5, "electric": 0.5},
            "normal": {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
            "fighting": {"normal": 2.0, "rock": 2.0, "steel": 2.0, "ice": 2.0, "dark": 2.0},
            "poison": {"grass": 2.0, "fairy": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0.0},
            "ground": {"fire": 2.0, "electric": 2.0, "poison": 2.0, "rock": 2.0, "steel": 2.0, "flying": 0.0},
            "rock": {"fire": 2.0, "ice": 2.0, "flying": 2.0, "bug": 2.0, "fighting": 0.5, "ground": 0.5, "steel": 0.5},
            "bug": {"grass": 2.0, "psychic": 2.0, "dark": 2.0, "fire": 0.5, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "ghost": 0.5, "steel": 0.5, "fairy": 0.5},
            "ghost": {"psychic": 2.0, "ghost": 2.0, "normal": 0.0, "dark": 0.5},
            "steel": {"ice": 2.0, "rock": 2.0, "fairy": 2.0, "fire": 0.5, "water": 0.5, "electric": 0.5, "steel": 0.5},
            "ice": {"grass": 2.0, "ground": 2.0, "flying": 2.0, "dragon": 2.0, "fire": 0.5, "water": 0.5, "ice": 0.5, "steel": 0.5},
            "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
            "dark": {"psychic": 2.0, "ghost": 2.0, "fighting": 0.5, "dark": 0.5, "fairy": 0.5},
            "fairy": {"fighting": 2.0, "dragon": 2.0, "dark": 2.0, "fire": 0.5, "poison": 0.5, "steel": 0.5}
        }

    def _set_default_moves(self):
        """Set default moves if none provided."""
        if not self.p1.available_moves:
            self.p1.available_moves = self._get_default_moves_for_types(self.p1.types)
        if not self.p2.available_moves:
            self.p2.available_moves = self._get_default_moves_for_types(self.p2.types)

    def _get_default_moves_for_types(self, types: List[str]) -> List[str]:
        """Get appropriate default moves based on Pokémon types."""
        default_moves = ["tackle"]  # Always include a basic move
        
        for poke_type in types:
            if poke_type.lower() == "fire":
                default_moves.extend(["ember", "flamethrower"])
            elif poke_type.lower() == "water":
                default_moves.extend(["water gun", "surf"])
            elif poke_type.lower() == "grass":
                default_moves.extend(["vine whip", "razor leaf"])
            elif poke_type.lower() == "electric":
                default_moves.extend(["thunder shock", "thunderbolt"])
            elif poke_type.lower() == "psychic":
                default_moves.extend(["confusion", "psybeam"])
            elif poke_type.lower() == "flying":
                default_moves.extend(["wing attack", "air slash"])
            elif poke_type.lower() == "dark":
                default_moves.extend(["bite", "crunch"])
        
        return list(set(default_moves))[:4]

    def _get_move_database(self) -> Dict[str, Dict[str, Any]]:
        """Comprehensive move database with all effects."""
        return {
            # Fire moves
            "ember": {"power": 40, "type": "fire", "accuracy": 1.0, "status_inflict": {"burn": 0.10}},
            "flamethrower": {"power": 90, "type": "fire", "accuracy": 1.0, "status_inflict": {"burn": 0.10}},
            "fire blast": {"power": 110, "type": "fire", "accuracy": 0.85, "status_inflict": {"burn": 0.30}},
            "will-o-wisp": {"power": 0, "type": "fire", "accuracy": 0.85, "set_status": "burn"},

            # Water moves
            "water gun": {"power": 40, "type": "water", "accuracy": 1.0},
            "surf": {"power": 90, "type": "water", "accuracy": 1.0},
            "hydro pump": {"power": 110, "type": "water", "accuracy": 0.80},
            "aqua ring": {"power": 0, "type": "water", "accuracy": 1.0, "heal_frac": 0.0625},

            # Grass moves
            "vine whip": {"power": 45, "type": "grass", "accuracy": 1.0},
            "razor leaf": {"power": 55, "type": "grass", "accuracy": 0.95, "crit_rate": 0.125},
            "leaf storm": {"power": 130, "type": "grass", "accuracy": 0.90, "self_stat_drop": {"sp_attack": -2}},
            "sleep powder": {"power": 0, "type": "grass", "accuracy": 0.75, "set_status": "sleep"},

            # Electric moves
            "thunder shock": {"power": 40, "type": "electric", "accuracy": 1.0, "status_inflict": {"paralyze": 0.10}},
            "thunderbolt": {"power": 90, "type": "electric", "accuracy": 1.0, "status_inflict": {"paralyze": 0.10}},
            "thunder": {"power": 110, "type": "electric", "accuracy": 0.70, "status_inflict": {"paralyze": 0.30}},

            # Normal moves
            "tackle": {"power": 40, "type": "normal", "accuracy": 1.0},
            "quick attack": {"power": 40, "type": "normal", "accuracy": 1.0, "priority": 1},
            "slash": {"power": 70, "type": "normal", "accuracy": 1.0, "crit_rate": 0.125},
            "hyper beam": {"power": 150, "type": "normal", "accuracy": 0.90, "recharge": True},

            # Psychic moves
            "confusion": {"power": 50, "type": "psychic", "accuracy": 1.0, "confuse": 0.10},
            "psybeam": {"power": 65, "type": "psychic", "accuracy": 1.0, "confuse": 0.10},
            "psychic": {"power": 90, "type": "psychic", "accuracy": 1.0, "stat_drop": {"sp_defense": -1, "chance": 0.10}},
            "recover": {"power": 0, "type": "psychic", "accuracy": 1.0, "heal_frac": 0.5},

            # Flying moves
            "wing attack": {"power": 60, "type": "flying", "accuracy": 1.0},
            "air slash": {"power": 75, "type": "flying", "accuracy": 0.95, "flinch": 0.30},

            # Dark moves
            "bite": {"power": 60, "type": "dark", "accuracy": 1.0, "flinch": 0.30},
            "crunch": {"power": 80, "type": "dark", "accuracy": 1.0, "stat_drop": {"defense": -1, "chance": 0.20}},

            # Ice moves
            "ice beam": {"power": 90, "type": "ice", "accuracy": 1.0, "status_inflict": {"freeze": 0.10}},
            "blizzard": {"power": 110, "type": "ice", "accuracy": 0.70, "status_inflict": {"freeze": 0.10}},

            # Status moves
            "swords dance": {"power": 0, "type": "normal", "accuracy": 1.0, "self_stat_boost": {"attack": 2}},
            "agility": {"power": 0, "type": "psychic", "accuracy": 1.0, "self_stat_boost": {"speed": 2}},
            "defense curl": {"power": 0, "type": "normal", "accuracy": 1.0, "self_stat_boost": {"defense": 1}},
        }

    def validate_pokemon_moves(self, debug_mode: bool = False):
        """Validate that Pokemon have appropriate moves and fix if needed."""
        issues_found = []
        
        for pokemon in [self.p1, self.p2]:
            if debug_mode:
                print(f"Validating {pokemon.name}")
                print(f"Types: {pokemon.types}")
                print(f"Current moves: {pokemon.available_moves}")
            
            # Use the Pokemon's own validation method
            pokemon_issues = pokemon.validate_moves(self.move_data)
            issues_found.extend(pokemon_issues)
            
            if debug_mode and pokemon_issues:
                for issue in pokemon_issues:
                    print(f"  WARNING: {issue}")
            
            # Auto-fix if needed
            if pokemon_issues:
                changes = pokemon.fix_inappropriate_moves(
                    self.move_data, 
                    self._get_default_moves_for_types
                )
                if debug_mode:
                    for change in changes:
                        print(f"  {change}")
        
        return issues_found

    def get_debug_info(self):
        """Get debug information about current battle state."""
        debug_info = {
            "p1": {
                "name": self.p1.name,
                "types": self.p1.types,
                "moves": self.p1.get_move_info(self.move_data)
            },
            "p2": {
                "name": self.p2.name,
                "types": self.p2.types,
                "moves": self.p2.get_move_info(self.move_data)
            },
            "issues": []
        }
        
        # Collect all issues
        p1_issues = self.p1.validate_moves(self.move_data)
        p2_issues = self.p2.validate_moves(self.move_data)
        debug_info["issues"] = p1_issues + p2_issues
        
        return debug_info

    def log_battle_debug(self):
        """Log debug info for battle."""
        debug_info = self.get_debug_info()
        
        print(f"P1: {debug_info['p1']['name']} {debug_info['p1']['types']} -> {[m['move'] for m in debug_info['p1']['moves']]}")
        print(f"P2: {debug_info['p2']['name']} {debug_info['p2']['types']} -> {[m['move'] for m in debug_info['p2']['moves']]}")
        
        if debug_info['issues']:
            print("ISSUES FOUND:")
            for issue in debug_info['issues']:
                print(f"  - {issue}")
        
        return debug_info

    @staticmethod
    def flatten_pokemon_info(info: Dict[str, Any]) -> Dict[str, Any]:
        """Basic flattening function for Pokemon info."""
        stats = info.get("stats", {})
        return {
            "name": info.get("name"),
            "types": info.get("types", []),
            "hp": stats.get("hp"),
            "max_hp": stats.get("hp"),
            "attack": stats.get("attack"),
            "defense": stats.get("defense"),
            "speed": stats.get("speed"),
            "available_moves": info.get("moves", [])[:4],  # Limit to first 4 moves from API
            "status": info.get("status"),
        }

    def is_damaging_move(self, attacker: PokemonBattleState, defender: PokemonBattleState, move_name: str) -> bool:
        """Check if a move deals damage."""
        move = self.move_data.get(move_name, {})
        return move.get("power", 0) > 0

    def calculate_type_effectiveness(self, move_type: str, defender_types: List[str]) -> float:
        """Calculate type effectiveness multiplier."""
        multiplier = 1.0
        for def_type in defender_types:
            multiplier *= self.type_chart.get(move_type.lower(), {}).get(def_type.lower(), 1.0)
        return multiplier

    def calculate_damage(self, attacker: PokemonBattleState, defender: PokemonBattleState, move_name: str) -> int:
        """Calculate damage dealt by a move."""
        move = self.move_data.get(move_name)
        if not move or move.get("power", 0) <= 0:
            return 0
        
        power = move["power"]
        move_type = move["type"]
        level = 50
        
        # Get stats
        attack = attacker.attack
        defense = max(1, defender.defense)
        
        # Base damage calculation
        base_damage = (((2 * level / 5 + 2) * power * (attack / defense)) / 50) + 2
        
        # Apply STAB (Same Type Attack Bonus)
        if move_type.lower() in [t.lower() for t in attacker.types]:
            base_damage *= 1.5
        
        # Apply type effectiveness
        type_multiplier = self.calculate_type_effectiveness(move_type, defender.types)
        base_damage *= type_multiplier
        
        # Critical hit check
        crit_rate = move.get("crit_rate", 0.0625)  # 1/16 base rate
        if random.random() < crit_rate:
            base_damage *= 2.0
        
        # Random variance (85-100%)
        base_damage *= random.uniform(0.85, 1.0)
        
        return max(1, int(round(base_damage)))

    def apply_status_start_of_turn(self, pokemon: PokemonBattleState, log: List[Dict[str, Any]]) -> bool:
        """Apply status effects at start of turn. Returns True if pokemon can act."""
        if not pokemon.status:
            return True
        
        status = pokemon.status.lower()
        
        if status == "burn":
            # Burn deals 1/16 max HP damage
            burn_damage = max(1, int(pokemon.max_hp * 0.0625))
            pokemon.hp = max(0, pokemon.hp - burn_damage)
            log.append({
                "event": "status_damage",
                "pokemon": pokemon.name,
                "status": "burn",
                "damage": burn_damage,
                "remaining_hp": pokemon.hp
            })
            return pokemon.hp > 0
        
        elif status == "poison":
            # Poison deals 1/8 max HP damage
            poison_damage = max(1, int(pokemon.max_hp * 0.125))
            pokemon.hp = max(0, pokemon.hp - poison_damage)
            log.append({
                "event": "status_damage",
                "pokemon": pokemon.name,
                "status": "poison",
                "damage": poison_damage,
                "remaining_hp": pokemon.hp
            })
            return pokemon.hp > 0
        
        elif status == "sleep":
            if pokemon.status_turns <= 0:
                # Wake up
                pokemon.status = None
                pokemon.status_turns = 0
                log.append({
                    "event": "status_end",
                    "pokemon": pokemon.name,
                    "status": "sleep",
                    "message": f"{pokemon.name} woke up!"
                })
                return True
            else:
                pokemon.status_turns -= 1
                log.append({
                    "event": "status_effect",
                    "pokemon": pokemon.name,
                    "status": "sleep",
                    "message": f"{pokemon.name} is fast asleep!",
                    "turns_remaining": pokemon.status_turns
                })
                return False
        
        elif status == "paralyze":
            # 25% chance to be fully paralyzed
            if random.random() < 0.25:
                log.append({
                    "event": "status_effect",
                    "pokemon": pokemon.name,
                    "status": "paralyze",
                    "message": f"{pokemon.name} is paralyzed and can't move!"
                })
                return False
        
        elif status == "freeze":
            # 20% chance to thaw out
            if random.random() < 0.20:
                pokemon.status = None
                log.append({
                    "event": "status_end",
                    "pokemon": pokemon.name,
                    "status": "freeze",
                    "message": f"{pokemon.name} thawed out!"
                })
                return True
            else:
                log.append({
                    "event": "status_effect",
                    "pokemon": pokemon.name,
                    "status": "freeze",
                    "message": f"{pokemon.name} is frozen solid!"
                })
                return False
        
        return True

    def is_immune_to_status(self, defender: PokemonBattleState, status_name: str, move_name: str) -> bool:
        """Check if a Pokémon is immune to a status condition."""
        status = status_name.lower()
        defender_types = [t.lower() for t in defender.types]
        
        # Type-based immunities
        if status == "burn" and "fire" in defender_types:
            return True
        if status == "freeze" and "ice" in defender_types:
            return True
        if status == "poison" and ("poison" in defender_types or "steel" in defender_types):
            return True
        if status == "paralyze" and "electric" in defender_types:
            return True
        
        # Move-specific immunities
        if move_name == "sleep powder" and "grass" in defender_types:
            return True
        
        return False

    def perform_move(self, attacker: PokemonBattleState, defender: PokemonBattleState, 
                    move_name: str, log: List[Dict[str, Any]], can_flinch: bool = False) -> Dict[str, Any]:
        """Execute a single move with all effects."""
        move = self.move_data.get(move_name, {})
        result = {"damage": 0, "flinch": False, "status_inflicted": None}

        # Debug logging for move and damage
        print(f"[DEBUG] {attacker.name} uses {move_name} on {defender.name}")
        print(f"[DEBUG] Move data: {move}")

        # Check accuracy
        accuracy = move.get("accuracy", 1.0)
        if random.random() > accuracy:
            log.append({
                "event": "move_miss",
                "attacker": attacker.name,
                "move": move_name,
                "message": f"{attacker.name}'s {move_name} missed!"
            })
            print(f"[DEBUG] {attacker.name}'s {move_name} missed!")
            return result

        # Handle healing moves
        if move.get("heal_frac"):
            heal_amount = int(attacker.max_hp * move["heal_frac"])
            old_hp = attacker.hp
            attacker.hp = min(attacker.max_hp, attacker.hp + heal_amount)
            actual_heal = attacker.hp - old_hp
            log.append({
                "event": "heal",
                "pokemon": attacker.name,
                "move": move_name,
                "heal_amount": actual_heal,
                "current_hp": attacker.hp
            })
            print(f"[DEBUG] {attacker.name} healed for {actual_heal}, current HP: {attacker.hp}")
            return result

        # Calculate and apply damage
        damage = self.calculate_damage(attacker, defender, move_name)
        print(f"[DEBUG] Calculated damage: {damage}")
        if damage > 0:
            defender.hp = max(0, defender.hp - damage)
            result["damage"] = damage

            # Determine effectiveness message
            move_type = move.get("type", "normal")
            effectiveness = self.calculate_type_effectiveness(move_type, defender.types)
            effectiveness_msg = ""
            if effectiveness > 1.5:
                effectiveness_msg = "It's super effective!"
            elif effectiveness < 0.75:
                effectiveness_msg = "It's not very effective..."
            elif effectiveness == 0:
                effectiveness_msg = "It has no effect!"

            log.append({
                "event": "damage",
                "attacker": attacker.name,
                "defender": defender.name,
                "move": move_name,
                "damage": damage,
                "remaining_hp": defender.hp,
                "effectiveness": effectiveness,
                "message": effectiveness_msg
            })
            print(f"[DEBUG] {defender.name} took {damage} damage, remaining HP: {defender.hp}")
        
        # Apply status effects (only if defender isn't fainted and doesn't have status)
        if defender.hp > 0 and not defender.status:
            # Guaranteed status (set_status)
            if "set_status" in move:
                status = move["set_status"]
                if not self.is_immune_to_status(defender, status, move_name):
                    defender.status = status
                    if status == "sleep":
                        defender.status_turns = random.randint(1, 3)
                    result["status_inflicted"] = status
                    log.append({
                        "event": "status_inflict",
                        "pokemon": defender.name,
                        "status": status,
                        "from_move": move_name
                    })
            
            # Chance-based status (status_inflict)
            elif "status_inflict" in move:
                for status, chance in move["status_inflict"].items():
                    if random.random() < chance and not self.is_immune_to_status(defender, status, move_name):
                        defender.status = status
                        if status == "sleep":
                            defender.status_turns = random.randint(1, 3)
                        result["status_inflicted"] = status
                        log.append({
                            "event": "status_inflict",
                            "pokemon": defender.name,
                            "status": status,
                            "from_move": move_name
                        })
                        break
        
        # Apply flinch (only if can_flinch is True and defender hasn't moved yet)
        if can_flinch and defender.hp > 0 and "flinch" in move:
            if random.random() < move["flinch"]:
                result["flinch"] = True
                log.append({
                    "event": "flinch",
                    "pokemon": defender.name,
                    "from_move": move_name
                })
        
        return result

    def execute_turn(self, p1_move: str, p2_move: str) -> List[Dict[str, Any]]:
        """Execute a complete battle turn with proper turn order and effects."""
        log = []
        self.turn_count += 1
        
        log.append({
            "event": "turn_start",
            "turn": self.turn_count,
            "p1_move": p1_move,
            "p2_move": p2_move
        })
        
        # Determine turn order (priority first, then speed)
        p1_priority = self.move_data.get(p1_move, {}).get("priority", 0)
        p2_priority = self.move_data.get(p2_move, {}).get("priority", 0)
        
        if p1_priority > p2_priority or (p1_priority == p2_priority and self.p1.speed >= self.p2.speed):
            first_pokemon, second_pokemon = self.p1, self.p2
            first_move, second_move = p1_move, p2_move
            first_goes_first = True
        else:
            first_pokemon, second_pokemon = self.p2, self.p1
            first_move, second_move = p2_move, p1_move
            first_goes_first = False
        
        # First Pokémon's turn
        can_act = self.apply_status_start_of_turn(first_pokemon, log)
        flinch_second = False
        
        if can_act and first_pokemon.hp > 0:
            move_result = self.perform_move(first_pokemon, second_pokemon, first_move, log, can_flinch=True)
            flinch_second = move_result.get("flinch", False)
        
        # Check if battle ended
        if second_pokemon.hp <= 0:
            log.append({
                "event": "faint",
                "pokemon": second_pokemon.name,
                "message": f"{second_pokemon.name} fainted!"
            })
            return log
        
        # Second Pokémon's turn
        if flinch_second:
            log.append({
                "event": "flinch_prevent",
                "pokemon": second_pokemon.name,
                "message": f"{second_pokemon.name} flinched and couldn't move!"
            })
        else:
            can_act = self.apply_status_start_of_turn(second_pokemon, log)
            if can_act and second_pokemon.hp > 0:
                self.perform_move(second_pokemon, first_pokemon, second_move, log, can_flinch=False)
        
        # Check if battle ended after second move
        if first_pokemon.hp <= 0:
            log.append({
                "event": "faint",
                "pokemon": first_pokemon.name,
                "message": f"{first_pokemon.name} fainted!"
            })
        
        self.battle_history.append({
            "turn": self.turn_count,
            "events": log.copy(),
            "p1_hp": self.p1.hp,
            "p2_hp": self.p2.hp
        })
        
        return log

    def execute_turn_with_moves(self, p1_move: str, p2_move: str) -> Tuple[float, float]:
        """Legacy method for backward compatibility - returns damage dealt/taken."""
        initial_p1_hp = self.p1.hp
        initial_p2_hp = self.p2.hp
        
        # Execute turn with full logging
        self.execute_turn(p1_move, p2_move)
        
        # Calculate damage dealt/taken from P1's perspective
        damage_done = initial_p2_hp - self.p2.hp
        damage_taken = initial_p1_hp - self.p1.hp
        
        return damage_done, damage_taken

    def get_winner(self) -> Optional[str]:
        """Determine the battle winner."""
        if self.p1.hp <= 0 and self.p2.hp <= 0:
            return "draw"
        elif self.p1.hp <= 0:
            return self.p2.name
        elif self.p2.hp <= 0:
            return self.p1.name
        return None

    def reset_battle(self):
        """Reset battle to initial state."""
        self.p1.hp = self.p1.max_hp
        self.p2.hp = self.p2.max_hp
        self.p1.status = None
        self.p1.status_turns = 0
        self.p2.status = None
        self.p2.status_turns = 0
        self.turn_count = 0
        self.battle_history.clear()

    def get_battle_state(self) -> Dict[str, Any]:
        """Get current battle state for saving/loading."""
        return {
            "p1": self.p1.dict(),
            "p2": self.p2.dict(),
            "turn_count": self.turn_count,
            "battle_history": self.battle_history,
            "winner": self.get_winner()
        }

    def get_valid_moves(self, pokemon: PokemonBattleState) -> List[str]:
        """Get list of valid moves for a Pokémon."""
        return [move for move in pokemon.available_moves if move in self.move_data]

    def get_move_info(self, move_name: str) -> Dict[str, Any]:
        """Get information about a specific move."""
        return self.move_data.get(move_name, {})

    def simulate_battle_outcome(self, p1_moves: List[str], p2_moves: List[str], 
                              max_turns: int = 50) -> Dict[str, Any]:
        """Simulate a full battle with given move sequences."""
        original_state = self.get_battle_state()
        self.reset_battle()
        
        full_log = []
        turn = 0
        
        while turn < max_turns and turn < min(len(p1_moves), len(p2_moves)):
            if self.get_winner():
                break
                
            turn_log = self.execute_turn(p1_moves[turn], p2_moves[turn])
            full_log.extend(turn_log)
            turn += 1
        
        result = {
            "winner": self.get_winner(),
            "turns": turn,
            "final_state": self.get_battle_state(),
            "full_log": full_log
        }
        
        # Restore original state
        self.p1 = PokemonBattleState(**original_state["p1"])
        self.p2 = PokemonBattleState(**original_state["p2"])
        self.turn_count = original_state["turn_count"]
        self.battle_history = original_state["battle_history"]
        
        return result