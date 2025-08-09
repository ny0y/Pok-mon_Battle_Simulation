import threading
from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

import database.auth as auth
import database.crud as crud
import database.models as models
import database.schemas as schemas
import database.database as database
from database.database import SessionLocal, engine

from api import ai, pokemon, battle, play
from ai.rl_agent import load_agent
import dependencies
import config

# Thread lock for thread safety
lock = threading.Lock()

# Lifespan handler to load AI agent on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        default_actions = ["tackle", "water gun", "bite", "ember", "wing attack", "slash"]
        dependencies.agent_instance = load_agent(filename="qtable.pkl", actions=default_actions)
        print("Q-learning agent loaded with default actions.")
    except Exception as e:
        print(f"Agent load failed: {e}")
        dependencies.agent_instance = None
    yield
    print("Server shutting down...")

# Create FastAPI app with lifespan event
app = FastAPI(
    title="Pokémon Battle API",
    description="A comprehensive Pokémon battle simulation API with AI training",
    version="1.0.0",
    lifespan=lifespan
)

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

# DB session dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication endpoints
@app.post("/register", response_model=schemas.UserOut, tags=["Authentication"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", tags=["Authentication"])
def login(user: schemas.UserCreate = Body(...), db: Session = Depends(get_db)):
    user_obj = auth.authenticate_user(db, user.username, user.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user_obj.username})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_obj.id}

@app.get("/protected-route", tags=["Authentication"])
def protected_route(current_user: models.User = Depends(auth.get_current_user)):
    return {"message": f"Hello {current_user.username}, you are authorized.", "user_id": current_user.id}

@app.post("/predict_move", tags=["AI"])
def predict_move(state: dict, current_user: models.User = Depends(auth.get_current_user)):
    agent = dependencies.agent_instance
    if agent is None:
        raise HTTPException(status_code=500, detail="AI agent not loaded.")
    try:
        # Canonicalize state for consistent hashing
        clean_state = {}
        for k, v in state.items():
            if isinstance(v, list):
                clean_state[k] = tuple(v)
            elif isinstance(v, dict):
                clean_state[k] = tuple(sorted(v.items()))
            else:
                clean_state[k] = v
        
        action = agent.choose_action(clean_state)
        return {"action": action, "state_processed": True, "user_id": current_user.id}
    except Exception as e:
        return {"action": "tackle", "error": str(e), "state_processed": False}

# Health check endpoint
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "ai_agent_loaded": dependencies.agent_instance is not None,
        "database_connected": True
    }

# Include routers with proper authentication
app.include_router(
    pokemon.router, 
    prefix="/pokemon", 
    tags=["Pokémon Data"],
    dependencies=[Depends(auth.get_current_user)]
)

app.include_router(
    battle.router, 
    prefix="/battle", 
    tags=["Battle Simulator"],
    dependencies=[Depends(auth.get_current_user)]
)

app.include_router(
    ai.router, 
    prefix="/ai", 
    tags=["AI Training"],
    dependencies=[Depends(auth.get_current_user)]
)

app.include_router(
    play.router, 
    prefix="/play", 
    tags=["Playable Battles"],
    dependencies=[Depends(auth.get_current_user)]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Fixed global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )