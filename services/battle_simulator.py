import random
import json
from models.battle import PokemonBattleState

class BattleSimulator:
    def __init__(self, p1_info, p2_info):
        self.p1 = PokemonBattleState.from_pokemon_info(p1_info)
        self.p2 = PokemonBattleState.from_pokemon_info(p2_info)

        with open("data/type_chart.json") as f:
            self.type_chart = json.load(f)

        # You can still override these from caller; these are defaults
        if not self.p1.available_moves:
            self.p1.available_moves = ["ember", "wing attack", "slash"]
        if not self.p2.available_moves:
            self.p2.available_moves = ["tackle", "quick attack", "water gun"]

        # === Completed move data with secondaries ===
        self.move_data = {
            # Fire moves
            "ember":         {"power": 40, "type": "fire", "status_inflict": {"burn": 0.10}},
            "flamethrower":  {"power": 90, "type": "fire", "status_inflict": {"burn": 0.10}},
            "fire blast":    {"power": 110, "type": "fire", "status_inflict": {"burn": 0.30}},
            "will-o-wisp":   {"power": 0, "type": "fire", "set_status": "burn"},

            # Flying moves
            "wing attack":   {"power": 60, "type": "flying"},
            "air slash":     {"power": 75, "type": "flying", "flinch": 0.30},

            # Normal moves
            "slash":         {"power": 70, "type": "normal", "crit_rate": 0.125},
            "tackle":        {"power": 40, "type": "normal"},
            "quick attack":  {"power": 40, "type": "normal", "priority": 1},
            "hyper beam":    {"power": 150, "type": "normal", "recharge": True},

            # Water moves
            "water gun":     {"power": 40, "type": "water"},
            "surf":          {"power": 90, "type": "water"},
            "hydro pump":    {"power": 110, "type": "water", "accuracy": 0.80},

            # Grass moves
            "vine whip":     {"power": 45, "type": "grass"},
            "razor leaf":    {"power": 55, "type": "grass", "crit_rate": 0.125},
            "leaf storm":    {"power": 130, "type": "grass", "self_stat_drop": {"sp_attack": -2}},
            "sleep powder":  {"power": 0,  "type": "grass", "set_status": "sleep", "accuracy": 0.75},

            # Psychic moves
            "psybeam":       {"power": 65, "type": "psychic", "confuse": 0.10},
            "confusion":     {"power": 50, "type": "psychic", "confuse": 0.10},
            "psychic":       {"power": 90, "type": "psychic", "stat_drop": {"sp_defense": -1, "chance": 0.10}},
            "recover":       {"power": 0, "type": "psychic", "heal_frac": 0.5},

            # Dark moves
            "bite":          {"power": 60, "type": "dark", "flinch": 0.30},
            "crunch":        {"power": 80, "type": "dark", "stat_drop": {"defense": -1, "chance": 0.20}},

            # Electric moves
            "thunder shock": {"power": 40, "type": "electric", "status_inflict": {"paralyze": 0.10}},
            "thunderbolt":   {"power": 90, "type": "electric", "status_inflict": {"paralyze": 0.10}},
            "thunder":       {"power": 110, "type": "electric", "status_inflict": {"paralyze": 0.30}},

            # Ice moves
            "ice beam":      {"power": 90, "type": "ice", "status_inflict": {"freeze": 0.10}},
            "blizzard":      {"power": 110, "type": "ice", "status_inflict": {"freeze": 0.10}},

            # Status / Buff moves
            "swords dance":  {"power": 0, "type": "normal", "self_stat_boost": {"attack": +2}},
            "agility":       {"power": 0, "type": "psychic", "self_stat_boost": {"speed": +2}},
            "defense curl":  {"power": 0, "type": "normal", "self_stat_boost": {"defense": +1}},
        }

    def execute_turn_with_moves(self, p1_move, p2_move):
        # Determine move order by speed (with priority check)
        p1_priority = self.move_data.get(p1_move, {}).get("priority", 0)
        p2_priority = self.move_data.get(p2_move, {}).get("priority", 0)
        
        # First by priority, then by speed
        if p1_priority > p2_priority or (p1_priority == p2_priority and self.p1.speed >= self.p2.speed):
            first, second = self.p1, self.p2
            first_move, second_move = p1_move, p2_move
        else:
            first, second = self.p2, self.p1
            first_move, second_move = p2_move, p1_move

        damage_done = 0
        damage_taken = 0

        # First Pokemon attacks
        damage_first = self.calculate_damage(first, second, first_move)
        second.hp = max(second.hp - damage_first, 0)

        # If defender fainted, no second attack
        if second.hp == 0:
            if first == self.p1:
                damage_done = damage_first
                damage_taken = 0
            else:
                damage_taken = damage_first
                damage_done = 0
            return damage_done, damage_taken

        # Second Pokemon attacks
        damage_second = self.calculate_damage(second, first, second_move)
        first.hp = max(first.hp - damage_second, 0)

        if first == self.p1:
            damage_done = damage_first
            damage_taken = damage_second
        else:
            damage_done = damage_second
            damage_taken = damage_first

        return damage_done, damage_taken
    
    # ---------- Core helpers ----------
    def calculate_type_effectiveness(self, move_type, defender_types):
        m = 1.0
        for d in defender_types:
            m *= self.type_chart.get(move_type, {}).get(d, 1.0)
        return m

    def calculate_damage(self, attacker, defender, move_name):
        move = self.move_data.get(move_name)
        if not move or move.get("power", 0) <= 0:
            return 0
        power = move["power"]
        move_type = move["type"]
        level = 50
        atk = attacker.attack
        df  = max(1, defender.defense)
        base = (((2 * level / 5 + 2) * power * (atk / df)) / 50) + 2

        # STAB
        if move_type in [t.lower() for t in attacker.types]:
            base *= 1.5

        # Type effectiveness
        base *= self.calculate_type_effectiveness(move_type, [t.lower() for t in defender.types])

        # Random variance
        base *= random.uniform(0.85, 1.0)
        return max(1, round(base))

    # Start-of-turn effects. Return False to skip action.
    def apply_status_start_of_turn(self, mon, log):
        if not mon.status:
            return True

        st = mon.status.lower()

        if st == "burn":
            chip = max(1, int(round(mon.max_hp * 0.0625)))    # ~1/16
            mon.hp = max(0, mon.hp - chip)
            log.append({"status_tick": "burn", "target": mon.name, "damage": chip})
            return mon.hp > 0

        if st == "sleep":
            if mon.status_turns <= 0:
                # wake up this turn
                mon.status = None
                mon.status_turns = 0
                log.append({"wake_up": True, "target": mon.name})
                return True
            else:
                mon.status_turns -= 1
                log.append({"skip": "sleep", "target": mon.name, "turns_left": mon.status_turns})
                return False

        # (Paralysis/poison/etc. can be added here later)
        return True

    def immune_to_status(self, defender, status_name, move_name):
        status_name = status_name.lower()
        dtypes = [t.lower() for t in defender.types]

        # Simple, practical immunities
        if status_name == "burn" and "fire" in dtypes:
            return True
        # Grass is immune to powder moves (keep it simple: just Sleep Powder)
        if status_name == "sleep" and move_name == "sleep powder" and "grass" in dtypes:
            return True
        return False

    def roll(self, p):
        return random.random() < p

    def perform_move(self, attacker, defender, move_name, log, can_flinch_target=False):
        """
        Executes a single move, handling heals, damage, status infliction, and flinch.
        Returns a dict: {"damage": int, "flinch_target": bool}
        """
        move = self.move_data.get(move_name, {})
        result = {"damage": 0, "flinch_target": False}

        # Healing moves (e.g., Recover)
        if move.get("heal_frac"):
            heal = int(round(attacker.max_hp * move["heal_frac"]))
            old = attacker.hp
            attacker.hp = min(attacker.max_hp, attacker.hp + heal)
            log.append({"attacker": attacker.name, "move": move_name, "heal": attacker.hp - old})
            return result

        # Accuracy gate (only for moves that define accuracy; default = always hits)
        acc = move.get("accuracy", 1.0)
        if acc < 1.0 and not self.roll(acc):
            log.append({"attacker": attacker.name, "move": move_name, "miss": True})
            return result

        # Damage phase
        dmg = self.calculate_damage(attacker, defender, move_name)
        defender.hp = max(0, defender.hp - dmg)
        result["damage"] = dmg
        log.append({"attacker": attacker.name, "move": move_name, "damage": dmg})

        # Secondary: status_inflict (probabilistic: {"burn": 0.10}, etc.)
        if "status_inflict" in move and defender.hp > 0 and not defender.status:
            for status_name, chance in move["status_inflict"].items():
                if not self.immune_to_status(defender, status_name, move_name) and self.roll(chance):
                    defender.status = status_name
                    # Sleep uses a turn counter
                    if status_name == "sleep":
                        defender.status_turns = random.randint(1, 3)
                    log.append({"inflict": status_name, "target": defender.name, "from": move_name})
                    break  # only one status per move

        # Secondary: set_status (guaranteed if immune check passes & accuracy already handled)
        if "set_status" in move and defender.hp > 0 and not defender.status:
            status_name = move["set_status"]
            if not self.immune_to_status(defender, status_name, move_name):
                defender.status = status_name
                if status_name == "sleep":
                    defender.status_turns = random.randint(1, 3)
                log.append({"inflict": status_name, "target": defender.name, "from": move_name})

        # Volatile: flinch (only matters if target hasn't moved yet)
        if can_flinch_target and "flinch" in move and defender.hp > 0:
            if self.roll(move["flinch"]):
                result["flinch_target"] = True
                log.append({"volatile": "flinch", "target": defender.name, "from": move_name})

        return result

    # Proper execute_turn implementation that returns structured log
    def execute_turn(self, p1_move, p2_move):
        """
        Execute a complete turn with proper status handling, flinch mechanics, and structured logging.
        Returns a list of battle events/log entries.
        """
        log = []
        
        # Determine move order (priority first, then speed)
        p1_priority = self.move_data.get(p1_move, {}).get("priority", 0)
        p2_priority = self.move_data.get(p2_move, {}).get("priority", 0)
        
        if p1_priority > p2_priority or (p1_priority == p2_priority and self.p1.speed >= self.p2.speed):
            first, second = self.p1, self.p2
            first_move, second_move = p1_move, p2_move
        else:
            first, second = self.p2, self.p1
            first_move, second_move = p2_move, p1_move

        # FIRST Pokémon's turn
        can_act = self.apply_status_start_of_turn(first, log)
        flinch_second = False
        
        if can_act and first.hp > 0:
            outcome = self.perform_move(first, second, first_move, log, can_flinch_target=True)
            flinch_second = outcome.get("flinch_target", False)

        # Check if battle ended
        if second.hp == 0:
            return log

        # SECOND Pokémon's turn
        if flinch_second:
            log.append({"skip": "flinch", "target": second.name})
        else:
            can_act2 = self.apply_status_start_of_turn(second, log)
            if can_act2 and second.hp > 0:
                self.perform_move(second, first, second_move, log, can_flinch_target=False)

        return log

    def get_winner(self):
        if self.p1.hp <= 0 and self.p2.hp <= 0: return "draw"
        if self.p1.hp <= 0: return self.p2.name
        if self.p2.hp <= 0: return self.p1.name
        return None

    def reset_battle(self):
        self.p1.hp = self.p1.max_hp
        self.p2.hp = self.p2.max_hp
        self.p1.status = None; self.p1.status_turns = 0
        self.p2.status = None; self.p2.status_turns = 0