import asyncio
import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from typing import Dict, Any, Optional
from models.battle import PokemonBattleState
from services.battle_simulator import BattleSimulator
from dependencies import get_agent  # optional: returns AI agent or None
from ai.rl_agent import QLearningAgent
import random

router = APIRouter()

# In-memory runtime store
# battles_runtime[battle_id] = {
#   "players": { "client_id": websocket },
#   "states": {"player": PokemonBattleState.dict(), "ai": ...},
#   "queue": asyncio.Queue(),
#   "lock": asyncio.Lock(),
#   "sim": BattleSimulator(...),
#   "mode": "pvp" or "pve",
#   "pending_moves": {"player": move, "ai": move}  # Better move tracking
# }
battles_runtime: Dict[str, Dict[str, Any]] = {}


async def send_json_safe(ws: WebSocket, data: dict):
    try:
        await ws.send_text(json.dumps(data))
    except Exception:
        # ignore send errors (client gone)
        pass


@router.websocket("/ws/play/{battle_id}")
async def websocket_play(websocket: WebSocket, battle_id: str):
    """
    WebSocket endpoint for real-time play.
    Client should send on connect:
      {"type": "join", "role": "player"|"spectator"|"ai", "name": "alice"}
    Then to play:
      {"type": "action", "move": "ember"}
    Server messages:
      {"type":"state","player": {...},"ai": {...}}
      {"type":"turn","turn_log": [...], "player": {...}, "ai": {...}}
      {"type":"error","detail":"..."}
      {"type":"info","msg":"..."}
    """
    await websocket.accept()
    client_id = None
    
    try:
        # First message must be join
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=20)
        msg = json.loads(raw)
        if msg.get("type") != "join":
            await send_json_safe(websocket, {"type": "error", "detail": "first message must be join"})
            await websocket.close()
            return
    except Exception:
        await send_json_safe(websocket, {"type": "error", "detail": "no join received"})
        await websocket.close()
        return

    role = msg.get("role", "player")
    name = msg.get("name", "unknown")

    # Create or fetch runtime battle
    runtime = battles_runtime.get(battle_id)
    if not runtime:
        # create new battle (player will be "player")
        # expected msg may include player_info optionally
        p_info = msg.get("pokemon") or {
            "name": "charizard",
            "types": ["fire", "flying"],
            "hp": 78,
            "attack": 84,
            "defense": 78,
            "speed": 100,
            "available_moves": ["ember", "wing attack", "slash"]
        }
        # choose AI candidate if specified
        ai_info = msg.get("ai_pokemon") or {
            "name": "blastoise",
            "types": ["water"],
            "hp": 79,
            "attack": 83,
            "defense": 100,
            "speed": 78,
            "available_moves": ["water gun", "tackle", "bite"],
        }

        sim = BattleSimulator(p_info, ai_info)
        queue = asyncio.Queue()
        lock = asyncio.Lock()
        runtime = {
            "players": {},
            "sim": sim,
            "queue": queue,
            "lock": lock,
            "mode": "pve",  # default player vs ai
            "ai_info": ai_info,
            "player_info": p_info,
            "roles": {},  # client_id -> role mapping
            "ai_agent": None,  # can be set to QLearningAgent
            "pending_moves": {},  # Better move tracking
        }
        # set states (pydantic)
        runtime["states"] = {
            "player": PokemonBattleState.from_pokemon_info(p_info).dict(),
            "ai": PokemonBattleState.from_pokemon_info(ai_info).dict()
        }
        battles_runtime[battle_id] = runtime

    # Register websocket with unique client ID
    client_id = f"{role}_{uuid.uuid4().hex[:6]}"
    runtime["players"][client_id] = websocket
    runtime["roles"][client_id] = role

    # If user wants AI agent loaded globally, try to get
    try:
        agent = get_agent()
        if isinstance(agent, QLearningAgent):
            runtime["ai_agent"] = agent
    except Exception:
        # no agent available
        runtime["ai_agent"] = None

    # send initial state
    await send_json_safe(websocket, {
        "type": "state", 
        "player": runtime["states"]["player"], 
        "ai": runtime["states"]["ai"], 
        "battle_id": battle_id,
        "client_id": client_id
    })

    # If this is the first player and mode pve, start the battle loop for that runtime
    if "loop_task" not in runtime:
        runtime["loop_task"] = asyncio.create_task(battle_loop(battle_id))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                await send_json_safe(websocket, {"type": "error", "detail": "invalid json"})
                continue

            if msg.get("type") == "action":
                move = msg.get("move")
                # Better move tracking by role, not client
                client_role = runtime["roles"].get(client_id, "player")
                await runtime["queue"].put({"from": client_role, "move": move, "client_id": client_id})
            elif msg.get("type") == "ping":
                await send_json_safe(websocket, {"type": "pong"})
            else:
                await send_json_safe(websocket, {"type": "error", "detail": "unknown message type"})
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await send_json_safe(websocket, {"type": "error", "detail": f"Connection error: {e}"})
    finally:
        # Clean up client
        if client_id and client_id in runtime.get("players", {}):
            runtime["players"].pop(client_id, None)
            runtime["roles"].pop(client_id, None)


async def battle_loop(battle_id: str):
    """
    Main loop that waits for actions and resolves turns.
    Better handling of player vs AI moves with proper synchronization.
    """
    runtime = battles_runtime.get(battle_id)
    if not runtime:
        return
        
    sim: BattleSimulator = runtime["sim"]
    queue: asyncio.Queue = runtime["queue"]
    lock: asyncio.Lock = runtime["lock"]

    while True:
        try:
            # Wait for player's action with timeout (10s)
            try:
                player_action = await asyncio.wait_for(queue.get(), timeout=10.0)
            except asyncio.TimeoutError:
                player_action = None

            # Determine player move
            if player_action and player_action.get("move") and player_action.get("from") == "player":
                p_move = player_action["move"]
            else:
                # Fallback: random move from available moves
                p_state = runtime["states"]["player"]
                available = p_state.get("available_moves", ["ember"])
                p_move = random.choice(available)

            # Always use AI for second move in PvE mode
            mode = runtime.get("mode", "pve")
            if mode == "pve":
                # AI chooses move
                ai_agent: Optional[QLearningAgent] = runtime.get("ai_agent")
                ai_state = runtime["states"]["ai"]
                
                if ai_agent and ai_state.get("available_moves"):
                    try:
                        # Update agent actions to current available moves
                        ai_agent.actions = ai_state["available_moves"]
                        # Convert state for agent (make it hashable)
                        hashable_state = {k: tuple(v) if isinstance(v, list) else v 
                                        for k, v in ai_state.items()}
                        ai_move = ai_agent.choose_action(hashable_state)
                        if ai_move not in ai_state.get("available_moves", []):
                            ai_move = random.choice(ai_state["available_moves"])
                    except Exception:
                        ai_move = random.choice(ai_state.get("available_moves", ["water gun"]))
                else:
                    # Heuristic AI move selection
                    available = ai_state.get("available_moves", ["water gun"])
                    ai_move = random.choice(available)
                
                p2_move = ai_move
            else:
                # PvP mode - wait for second player (not implemented fully, fallback to AI)
                p2_move = random.choice(runtime["states"]["ai"].get("available_moves", ["water gun"]))

            # Now resolve turn with proper synchronization
            async with lock:
                # Ensure sim uses current runtime states
                try:
                    sim.p1 = PokemonBattleState(**runtime["states"]["player"])
                    sim.p2 = PokemonBattleState(**runtime["states"]["ai"])
                except Exception as e:
                    await broadcast(battle_id, {"type": "error", "detail": f"Invalid battle state: {e}"})
                    cleanup_runtime(battle_id)
                    return

                # Use the proper execute_turn method
                try:
                    turn_log = sim.execute_turn(p_move, p2_move)
                except Exception as e:
                    await broadcast(battle_id, {"type": "error", "detail": f"Turn execution error: {e}"})
                    # Try to continue with empty log
                    turn_log = [{"error": str(e)}]

                # Save updated states back
                runtime["states"]["player"] = sim.p1.dict()
                runtime["states"]["ai"] = sim.p2.dict()

                message = {
                    "type": "turn",
                    "turn_log": turn_log,
                    "player": runtime["states"]["player"],
                    "ai": runtime["states"]["ai"],
                    "battle_id": battle_id,
                    "mode": mode,
                    "moves": {"player": p_move, "ai": p2_move}
                }

                await broadcast(battle_id, message)

                # Check if battle ended
                winner = sim.get_winner()
                if winner is not None:
                    await broadcast(battle_id, {
                        "type": "end", 
                        "winner": winner, 
                        "player": runtime["states"]["player"], 
                        "ai": runtime["states"]["ai"]
                    })
                    cleanup_runtime(battle_id)
                    return

        except Exception as ex:
            await broadcast(battle_id, {"type": "error", "detail": f"Battle loop error: {ex}"})
            cleanup_runtime(battle_id)
            return


async def broadcast(battle_id: str, message: dict):
    """Send message to all connected clients for this battle."""
    runtime = battles_runtime.get(battle_id)
    if not runtime:
        return
        
    dead_clients = []
    for client_id, ws in list(runtime["players"].items()):
        try:
            await send_json_safe(ws, message)
        except Exception:
            dead_clients.append(client_id)
    
    # Clean up dead connections
    for client_id in dead_clients:
        runtime["players"].pop(client_id, None)
        runtime["roles"].pop(client_id, None)


def cleanup_runtime(battle_id: str):
    """Clean up battle runtime and cancel tasks."""
    runtime = battles_runtime.pop(battle_id, None)
    if not runtime:
        return
    
    # Cancel loop task if exists
    task = runtime.get("loop_task")
    if task and not task.done():
        task.cancel()
    
    # Close any remaining websockets
    for client_id, ws in runtime.get("players", {}).items():
        try:
            asyncio.create_task(ws.close())
        except:
            pass