import random
from services.battle_simulator import BattleSimulator

class PokemonBattleEnv:
    def __init__(self, pokemon1_info, pokemon2_info):
        self.p1_info = pokemon1_info
        self.p2_info = pokemon2_info
        self.simulator = BattleSimulator(self.p1_info, self.p2_info)
        self.done = False

    def reset(self):
        self.simulator = BattleSimulator(self.p1_info, self.p2_info)
        self.done = False
        return self.get_state()

    def get_state(self):
        # Simplified state dictionary to represent current battle
        return {
            "p1_hp": self.simulator.p1.hp / self.simulator.p1.max_hp,
            "p2_hp": self.simulator.p2.hp / self.simulator.p2.max_hp,
            "p1_status": self.simulator.p1.status or "none",
            "p2_status": self.simulator.p2.status or "none",
        }

    def step(self, p1_move):
        print(f"[ENV STEP] p1_move: {p1_move}")

        p2_move = random.choice(self.simulator.p2.available_moves)
        print(f"[ENV STEP] p2_move: {p2_move}")

        # Properly handle the result from execute_turn_with_moves
        try:
            result = self.simulator.execute_turn_with_moves(p1_move, p2_move)
            print(f"[ENV STEP] execute_turn_with_moves returned: {result}")

            # Result is a tuple (damage_done, damage_taken), not None
            if not isinstance(result, tuple) or len(result) != 2:
                print("[ENV STEP] ERROR: execute_turn_with_moves returned invalid result!")
                return self.get_state(), -10, True, {}

            damage_done, damage_taken = result
            print(f"[ENV STEP] damage_done: {damage_done}, damage_taken: {damage_taken}")

        except Exception as e:
            print(f"[ENV STEP] ERROR during battle execution: {e}")
            return self.get_state(), -10, True, {}

        next_state = self.get_state()
        winner = self.simulator.get_winner()
        reward = 0
        done = False
        
        # Better reward calculation
        if winner == self.simulator.p1.name:
            reward = 100 + damage_done - damage_taken  # Win bonus
            done = True
        elif winner == self.simulator.p2.name:
            reward = -100 + damage_done - damage_taken  # Loss penalty
            done = True
        else:
            reward = damage_done - damage_taken  # Ongoing battle reward

        print(f"[ENV STEP] reward: {reward}, done: {done}")
        return next_state, reward, done, {}