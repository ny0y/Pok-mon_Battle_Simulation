# Pokémon MCP Server

A FastAPI-based Pokémon battle server with AI integration using Q-learning. 
It allows you to fetch Pokémon data, simulate battles, and interact with an AI opponent.

## Features

- **Pokémon Data API**: Fetch Pokémon details from a local or external source.
- **Battle Simulation**: Create and simulate Pokémon battles.
- **AI Opponent**: Play against a Q-learning-trained AI agent.
- **Extendable Services**: Easily add more Pokémon, moves, or AI logic.

## Project Structure

```bash
pokemon-mcp-server/
├── ai/                  # AI and reinforcement learning modules
│   ├── battle_env.py    # Environment for Pokémon battles for RL
│   └── rl_agent.py      # Q-learning agent and related functions
├── api/                 # API route definitions
│   ├── pokemon.py       # Pokémon data routes
│   ├── battle.py        # Battle simulator routes
│   ├── battle_api.py    # AI battle training routes
│   └── play.py          # Interactive play mode routes
├── data/                # Static data
│   └── type_chart.bash  # Type effectiveness chart
├── models/              # Data models
│   ├── pokemon.py       # Pokémon Pydantic models
│   └── battle.py        # Battle state models
├── services/            # Core services
│   ├── data_fetcher.py  # Pokémon data fetching logic
│   └── battle_simulator.py # Core battle logic
├── utils/               # Utility functions
│   ├── damage.py        # Damage calculation helpers
│   └── type_chart.py    # Type chart loading/utilities
├── main.py              # Application entrypoint
├── requirements.txt     # Python dependencies
├── qtable.pkl           # Trained Q-learning agent data
├── train.py             # RL training script
└── README.md
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ny0y/pokemon-mcp-server.git
cd pokemon-mcp-server
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uvicorn main:app --reload
```

Server will start at: `http://127.0.0.1:8000`

## API Endpoints

### Pokémon Data

**GET** `/pokemon/{name}`  
Fetch details for a given Pokémon.

Example:
```bash
GET /pokemon/charizard
```

Response:
```bash
{
    "name": "charizard",
    "types": ["fire", "flying"],
    "abilities": ["blaze", "solar-power"],
    "stats": {
        "hp": 78,
        "attack": 84,
        "defense": 78,
        "special-attack": 109,
        "special-defense": 85,
        "speed": 100
    },
    "moves": ["ember", "wing attack", "slash"]
}
```

### Start a Battle

**POST** `/play/start`  
Starts a new battle and returns the battle ID.

Response:
```bash
{ "battle_id": "uuid-generated-id" }
```

### Make a Move

**GET** `/play/{battle_id}/move?player_move=ember`  
Submit a move for the player and let the AI respond.

Example response:
```bash
{
  "battle_id": "uuid",
  "turn_log": [
    {"attacker": "charizard", "move": "ember", "damage": 15},
    {"attacker": "blastoise", "move": "water gun", "damage": 10}
  ],
  "player": {...},
  "ai": {...}
}
```

### Predict Move (AI)

**POST** `/predict_move`  
Send a Pokémon state and receive the AI's predicted move.

Request:
```bash
{
  "hp": 50,
  "attack": 70,
  "defense": 60,
  "speed": 80,
  "status": []
}
```

Response:
```bash
{ "action": "ember" }
```

## AI System

The AI uses a **Q-learning** algorithm trained on battle simulations.  
- **`ai/rl_agent.py`** contains the agent logic.
- **`qtable.pkl`** stores the learned Q-values.
- Training is done using **`train.py`**.

## Extending the Project

- Add new Pokémon or moves to `data/`.
- Modify `battle_simulator.py` for different damage or battle rules.
- Train a new AI agent using `train.py`.

## License

MIT License © 2025 Eng. Ahmed Almalki
