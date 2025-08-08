import random
import pickle

class QLearningAgent:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, epsilon=0.2):
        self.q_table = {}  # state-action values
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon

    def get_state_key(self, state):
        # Convert state dict to a hashable tuple key
        return tuple(sorted(state.items()))

    def choose_action(self, state):
        key = self.get_state_key(state)
        if random.random() < self.epsilon or key not in self.q_table:
            return random.choice(self.actions)
        else:
            return max(self.q_table[key], key=self.q_table[key].get)

    def learn(self, state, action, reward, next_state):
        key = self.get_state_key(state)
        next_key = self.get_state_key(next_state)

        self.q_table.setdefault(key, {a: 0 for a in self.actions})
        self.q_table.setdefault(next_key, {a: 0 for a in self.actions})

        predict = self.q_table[key][action]
        target = reward + self.gamma * max(self.q_table[next_key].values())

        self.q_table[key][action] += self.lr * (target - predict)

def save_agent(agent, filename='qtable.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(agent.q_table, f)

def load_agent(filename='qtable.pkl', actions=None):
    if actions is None:
        raise ValueError("Actions list must be provided")
    with open(filename, 'rb') as f:
        q_table = pickle.load(f)
    agent = QLearningAgent(actions=actions)
    agent.q_table = q_table
    return agent
