# Pokémon Battle API - Complete Documentation

## � API Endpoint Summary

| Category         | Method | Endpoint                        | Description                                 |
|------------------|--------|----------------------------------|---------------------------------------------|
| Auth             | POST   | /register                        | Register a new user                         |
| Auth             | POST   | /login                           | Login and get JWT token                     |
| Auth             | GET    | /protected-route                 | Test authentication (requires token)        |
| Pokémon Data     | GET    | /pokemon/index                   | List/search Pokémon                         |
| Battle           | POST   | /battle/simulate                 | Simulate a battle between two Pokémon       |
| Interactive Play | POST   | /play/create                     | Create a new interactive battle             |
| Interactive Play | POST   | /play/{battle_id}/move           | Make a move in an interactive battle        |
| AI               | POST   | /ai/train                        | Train the RL agent                          |
| AI               | POST   | /predict_move                    | Predict a move using the AI                 |
| AI               | POST   | /ai/ai_move                      | Get AI's move for a given state             |
| System           | GET    | /health                          | Health check/status                         |

---

## �🚀 Base URL
```
http://127.0.0.1:8000
```

## 🔐 Authentication

All API endpoints (except `/register`, `/login`, `/health`) require Bearer token authentication.

### Headers Required:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Authentication Endpoints

### Register User
```http
POST /register
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "string"
}
```

### Login
```http
POST /login
```

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_string",
  "token_type": "bearer",
  "user_id": 1
}
```

### Protected Route (Test Authentication)
```http
GET /protected-route
```

**Response:**
```json
{
  "message": "Hello username, you are authorized.",
  "user_id": 1
}
```

---

## 🐾 Pokémon Data Endpoints

### Get Pokémon Index
```http
GET /pokemon/index
```

**Query Parameters:**
- `type` (optional): Filter by Pokémon type
- `name` (optional): Search by name (partial match)
- `page` (default: 1): Page number
- `page_size` (default: 10, max: 50): Results per page
- `including_evolution` (default: false): Include evolution chain

**Response:**
```json
{
  "count": 1010,
  "page": 1,
  "page_size": 10,
  "results": [
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
      "moves": ["ember", "wing-attack", "slash"],
      "evolution_chain": [
        {
          "species": "charmander",
          "min_level": null,
          "trigger": null
        },
        {
          "species": "charmeleon",
          "min_level": 16,
          "trigger": "level-up"
        }
      ]
    }
  ]
}
```

---

## ⚔️ Battle Simulation Endpoints

### Simulate Battle
```http
POST /battle/simulate
```

**Query Parameters:**
- `pokemon1`: Name of first Pokémon
- `pokemon2`: Name of second Pokémon

**Response:**
```json
{
  "battle_log": [
    {
      "turn": 1,
      "player1": "charizard",
      "player2": "blastoise",
      "p1_move": "ember",
      "p2_move": "water gun",
      "p1_hp": 65.0,
      "p2_hp": 71.0,
      "damage_done": 8,
      "damage_taken": 13,
      "p1_status": null,
      "p2_status": null
    }
  ],
  "players": {
    "player1": "charizard",
    "player2": "blastoise"
  },
  "winner": "blastoise"
}
```

---

## 🎮 Interactive Battle Endpoints

### Create Battle
```http
POST /play/create
```

**Request Body:**
```json
{
  "name": "charizard",
  "types": ["fire", "flying"],
  "hp": 78,
  "attack": 84,
  "defense": 78,
  "speed": 100,
  "available_moves": ["ember", "wing attack", "slash"],
  "status": null
}
```

**Response:**
```json
{
  "battle_id": "uuid-string",
  "user_id": "user_object",
  "player": {
    "name": "charizard",
    "types": ["fire", "flying"],
    "hp": 78.0,
    "max_hp": 78.0,
    "attack": 84,
    "defense": 78,
    "speed": 100,
    "available_moves": ["ember", "wing attack", "slash"],
    "status": null,
    "status_turns": 0
  },
  "ai": {
    "name": "blastoise",
    "types": ["water"],
    "hp": 79.0,
    "max_hp": 79.0,
    "attack": 83,
    "defense": 100,
    "speed": 78,
    "available_moves": ["water gun", "tackle", "bite"],
    "status": null,
    "status_turns": 0
  }
}
```

### Make Move
```http
POST /play/{battle_id}/move
```

**Query Parameters:**
- `player_move`: Move chosen by the player (e.g., "ember")

**Response:**
```json
{
  "battle_id": "uuid-string",
  "turn_log": [
    {
      "event": "turn_start",
      "turn": 1,
      "p1_move": "ember",
      "p2_move": "water gun"
    },
    {
      "event": "damage",
      "attacker": "charizard",
      "defender": "blastoise",
      "move": "ember",
      "damage": 15,
      "remaining_hp": 64.0,
      "effectiveness": 0.5,
      "message": "It's not very effective..."
    },
    {
      "event": "damage",
      "attacker": "blastoise",
      "defender": "charizard",
      "move": "water gun",
      "damage": 20,
      "remaining_hp": 58.0,
      "effectiveness": 2.0,
      "message": "It's super effective!"
    }
  ],
  "player": {
    "name": "charizard",
    "hp": 58.0,
    "status": null
  },
  "ai": {
    "name": "blastoise",
    "hp": 64.0,
    "status": null
  },
  "ai_reasoning": {
    "policy": "heuristic",
    "epsilon": 0.0,
    "heuristic_weight": 1.0,
    "note": "Deterministic heuristic with STAB and type effectiveness"
  }
}
```

---

## 🤖 AI Training Endpoints

### Train RL Agent
```http
POST /ai/train
```

**Response:**
```json
{
  "message": "Training completed",
  "total_episodes": 10000,
  "win_rate": 0.45,
  "final_win_count": 4500,
  "episode_rewards": [/* array of reward values */],
  "epsilon_history": [/* array of epsilon decay values */]
}
```

### Predict Move
```http
POST /predict_move
```

**Request Body:**
```json
{
  "hp": 50,
  "attack": 70,
  "defense": 60,
  "speed": 80,
  "status": []
}
```

**Response:**
```json
{
  "action": "ember",
  "state_processed": true,
  "user_id": 1
}
```

### Get AI Move
```http
POST /ai/ai_move
```

**Request Body:**
```json
{
  "ai_pokemon": {
    "name": "blastoise",
    "types": ["water"]
  },
  "player_pokemon": {
    "name": "charizard",
    "types": ["fire", "flying"]
  },
  "available_moves": ["water gun", "tackle", "bite"]
}
```

**Response:**
```json
{
  "selected_move": "water gun"
}
```

---

## 🏥 System Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "ai_agent_loaded": true,
  "database_connected": true
}
```

---

## 📊 Response Schemas

### PokemonBattleState
```json
{
  "name": "string",
  "types": ["string"],
  "hp": 0.0,
  "max_hp": 0.0,
  "attack": 0,
  "defense": 0,
  "speed": 0,
  "available_moves": ["string"],
  "status": "string|null",
  "status_turns": 0
}
```

### Battle Event Types
- `turn_start` - Turn initialization
- `damage` - Damage dealt
- `heal` - HP recovery
- `status_inflict` - Status condition applied
- `status_damage` - Damage from status effects
- `status_end` - Status condition removed
- `faint` - Pokémon faints
- `flinch` - Pokémon flinches

### Status Conditions
- `burn` - Deals 1/16 max HP damage per turn
- `poison` - Deals 1/8 max HP damage per turn
- `sleep` - Prevents action for 1-3 turns
- `paralyze` - 25% chance to skip turn, reduces speed
- `freeze` - Prevents action, 20% chance to thaw per turn

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "error": "Username already registered",
  "status_code": 400,
  "path": "/register"
}
```

### 401 Unauthorized
```json
{
  "error": "Incorrect username or password",
  "status_code": 401,
  "path": "/login"
}
```

### 404 Not Found
```json
{
  "error": "Battle not found",
  "status_code": 404,
  "path": "/play/invalid-id/move"
}
```

### 500 Internal Server Error
```json
{
  "error": "AI agent not loaded",
  "status_code": 500,
  "path": "/predict_move"
}
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./test.db
```

### CORS Configuration
- Allowed Origins: `http://localhost:3000`, `http://localhost:8080`
- Allowed Methods: `GET`, `POST`, `PUT`, `DELETE`
- Allows Credentials: `true`

---

## 🚀 Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Server:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Access API Docs:**
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

4. **Test Flow:**
   ```bash
   # 1. Register
   curl -X POST "http://127.0.0.1:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "trainer", "password": "password123"}'
   
   # 2. Login
   curl -X POST "http://127.0.0.1:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "trainer", "password": "password123"}'
   
   # 3. Use token for authenticated requests
   curl -X GET "http://127.0.0.1:8000/pokemon/index" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```