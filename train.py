from ai.rl_agent import QLearningAgent, save_agent
from ai.battle_env import PokemonBattleEnv
import random
from collections import Counter
import matplotlib.pyplot as plt
from typing import Tuple, List

# Pokémon info 
p1_info = {
    "name": "charizard",
    "types": ["fire", "flying"],
    "hp": 78,
    "attack": 84,
    "defense": 78,
    "speed": 100,
    "status": [],
    "abilities": ["blaze"],
    "available_moves": ["ember", "wing attack", "slash"],
}

p2_info = {
    "name": "blastoise",
    "types": ["water"],
    "hp": 79,
    "attack": 83,
    "defense": 100,
    "speed": 78,
    "status": [],
    "abilities": ["torrent"],
    "available_moves": ["tackle", "quick attack", "water gun"],
}

def train_agent(episodes=1000) -> Tuple[List[float], List[float], int]:  #  Added proper type hints
    print("Starting training...")
    env = PokemonBattleEnv(p1_info, p2_info)
    agent = QLearningAgent(actions=p1_info["available_moves"])

    epsilon = 1.0
    epsilon_decay = 0.995
    min_epsilon = 0.1

    episode_rewards = []
    win_count = 0
    action_counter = Counter()
    epsilon_history = []

    for episode in range(episodes):
        state = env.reset()
        done = False
        total_reward = 0
        step_count = 0

        print(f"Episode {episode} started, epsilon={epsilon:.3f}")

        while not done and step_count < 100:
            if random.random() < epsilon:
                action = random.choice(agent.actions)
            else:
                action = agent.choose_action(state)

            action_counter[action] += 1

            next_state, reward, done, _ = env.step(action)
            agent.learn(state, action, reward, next_state)

            state = next_state
            total_reward += reward
            print(f" Step {step_count}: action={action}, reward={reward}, done={done}")

            step_count += 1

        epsilon = max(min_epsilon, epsilon * epsilon_decay)
        epsilon_history.append(epsilon)
        episode_rewards.append(total_reward)

        if total_reward > 0:
            win_count += 1

        print(f"Episode {episode} finished with total reward {total_reward:.2f}")

    print("Training completed")
    print(f"Total wins: {win_count} out of {episodes} episodes, Win rate: {win_count / episodes * 100:.2f}%")
    print("Action distribution:")
    for action, count in action_counter.items():
        print(f"  {action}: {count} times")

    # Save agent after training
    save_agent(agent)

    # Return consistent values
    return episode_rewards, epsilon_history, win_count

if __name__ == "__main__":
    episodes = 1000
    rewards, epsilons, wins = train_agent(episodes=episodes)  # Accept all 3 return values

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(rewards, label='Total Reward')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title('Training Progress: Rewards per Episode')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(epsilons, label='Epsilon (exploration rate)', color='orange')
    plt.xlabel('Episode')
    plt.ylabel('Epsilon')
    plt.title('Epsilon Decay Over Training')
    plt.legend()

    plt.tight_layout()
    plt.show()