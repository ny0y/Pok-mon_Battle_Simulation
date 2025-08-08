from fastapi import FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
import threading
from fastapi.middleware.cors import CORSMiddleware
from api import pokemon, battle, battle_api, play
from ai.rl_agent import load_agent
import dependencies

lock = threading.Lock()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load agent with default actions, but allow dynamic updates
    try:
        # Start with common moves, but actions will be updated dynamically per battle
        default_actions = ["tackle", "water gun", "bite", "ember", "wing attack", "slash"]
        dependencies.agent_instance = load_agent(filename="qtable.pkl", actions=default_actions)
        print("Q-learning agent loaded with default actions. Actions will be updated dynamically per battle.")
    except Exception as e:
        print(f"Agent load failed (will still run heuristic AI): {e}")
        dependencies.agent_instance = None
    yield
    print("Server shutting down...")

app = FastAPI(title="Pokémon MCP Server", lifespan=lifespan)

@app.post("/predict_move")
def predict_move(state: dict):
    agent = dependencies.agent_instance
    if agent is None:
        raise HTTPException(status_code=500, detail="AI agent not loaded.")
    # Better error handling and state validation
    try:
        # Canonicalize state for agent
        clean_state = {k: tuple(v) if isinstance(v, list) else v for k, v in state.items()}
        action = agent.choose_action(clean_state)
        return {"action": action, "state_processed": True}
    except Exception as e:
        return {"action": "tackle", "error": str(e), "state_processed": False}

# Enable CORS so browser JS can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(pokemon.router, prefix="/pokemon", tags=["Pokemon Data"])
app.include_router(battle.router,  prefix="/battle",  tags=["Battle Simulator"])
app.include_router(battle_api.router, prefix="/ai",   tags=["AI Training"])
app.include_router(play.router,     prefix="/play",   tags=["Playable Battles"])