from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Mapping, Any, Dict, Union


class PokemonBattleState(BaseModel):
    # Ignore unknown fields so you can safely pass richer dicts
    model_config = ConfigDict(extra="ignore")

    name: str
    types: List[str]
    hp: float
    max_hp: float
    attack: int
    defense: int
    speed: int
    available_moves: List[str] = Field(default_factory=list)
    status: Optional[str] = None  # e.g., "burn", "poison", "sleep", "paralysis", "freeze"
    status_turns: int = 0  # Added missing field for status duration

    def is_fainted(self) -> bool:
        return self.hp <= 0

    def apply_damage(self, amount: float) -> int:
        """Apply integer damage, clamp at 0, and return the actual damage dealt."""
        dmg = max(0, int(round(amount)))
        before = self.hp
        self.hp = max(0.0, self.hp - dmg)
        return int(before - self.hp)

    @staticmethod
    def _coerce_status(val: Any) -> Optional[str]:
        """Accept None/str/list for status; normalize to a single string or None."""
        if val is None or val == "":
            return None
        if isinstance(val, list):
            if not val:
                return None
            return ", ".join(str(x) for x in val)
        return str(val)

    @classmethod
    def from_pokemon_info(cls, info: Union[Mapping[str, Any], BaseModel, Any]) -> "PokemonBattleState":
        """
        Build a battle state from various shapes:
        - dict-like: {"name", "types", "hp", "attack", "defense", "speed", "available_moves", "status"}
        - dict-like: {"name", "types", "stats": {"hp", "attack", "defense", "speed"}, "moves":[...]}
        - pydantic model with .model_dump()
        """
        if hasattr(info, "model_dump"):  # pydantic v2 models
            d = info.model_dump()
        elif isinstance(info, Mapping):
            d = dict(info)
        else:
            # fallback: attribute scraping
            keys = ["name", "types", "hp", "attack", "defense", "speed",
                    "available_moves", "moves", "status", "stats", "status_turns"]
            d = {k: getattr(info, k, None) for k in keys if hasattr(info, k)}

        stats: Dict[str, Any] = d.get("stats") or {}
        hp = d.get("hp", stats.get("hp", 50))
        atk = d.get("attack", stats.get("attack", 50))
        df  = d.get("defense", stats.get("defense", 50))
        spd = d.get("speed", stats.get("speed", 50))

        types = d.get("types") or []
        if isinstance(types, str):
            types = [types]

        # Prefer available_moves, else accept raw moves from a data source
        moves = d.get("available_moves")
        if moves is None:
            moves = d.get("moves", [])
        if isinstance(moves, dict):  # if someone passes a dict accidentally
            moves = list(moves.keys())

        status = cls._coerce_status(d.get("status"))
        status_turns = d.get("status_turns", 0)

        return cls(
            name=d.get("name", "unknown"),
            types=list(types),
            hp=float(hp),
            max_hp=float(hp),
            attack=int(atk),
            defense=int(df),
            speed=int(spd),
            available_moves=list(moves) if moves else [],
            status=status,
            status_turns=int(status_turns),
        )

    def dict(self, **kwargs):
        """Override dict method to handle status display"""
        result = super().dict(**kwargs)
        # Convert None status to empty string for cleaner JSON
        if result.get('status') is None:
            result['status'] = ""
        return result

    @staticmethod
    def clean_battle_response(battle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up battle response for better display"""
        if isinstance(battle_data, dict):
            for key, value in battle_data.items():
                if key.endswith('_status') and value is None:
                    battle_data[key] = ""
                elif isinstance(value, dict):
                    PokemonBattleState.clean_battle_response(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            PokemonBattleState.clean_battle_response(item)
        return battle_data

    def as_hashable_state(self) -> tuple:
        """
        Canonical, hashable snapshot for Q-learning keys.
        (You can also use the canonicalization you wrote in play.py; this is a built-in alternative.)
        """
        return tuple(sorted({
            "name": self.name,
            "types": tuple(self.types),
            "hp": round(self.hp, 2),
            "max_hp": round(self.max_hp, 2),
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "available_moves": tuple(self.available_moves),
            "status": self.status or "",
            "status_turns": self.status_turns,
        }.items()))

    def validate_moves(self, move_database: Dict[str, Dict[str, Any]]) -> List[str]:
        """Validate that Pokemon has appropriate moves."""
        issues = []
        
        for move in self.available_moves:
            if move not in move_database:
                issues.append(f"{self.name} has unknown move: {move}")
                continue
            
            move_type = move_database[move]['type']
            is_stab = move_type.lower() in [t.lower() for t in self.types]
            is_normal = move_type.lower() == 'normal'
            
            if not is_stab and not is_normal:
                issues.append(f"{self.name} ({self.types}) has {move_type}-type move: {move}")
        
        return issues

    def get_move_info(self, move_database: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed information about Pokemon's moves."""
        move_info = []
        
        for move in self.available_moves:
            if move in move_database:
                move_data = move_database[move]
                move_type = move_data['type']
                is_stab = move_type.lower() in [t.lower() for t in self.types]
                
                move_info.append({
                    "move": move,
                    "type": move_type,
                    "power": move_data.get("power", 0),
                    "accuracy": move_data.get("accuracy", 1.0),
                    "stab": is_stab,
                    "appropriate": is_stab or move_type.lower() == 'normal'
                })
            else:
                move_info.append({
                    "move": move,
                    "type": "unknown",
                    "power": 0,
                    "accuracy": 0,
                    "stab": False,
                    "appropriate": False
                })
        
        return move_info

    def fix_inappropriate_moves(self, move_database: Dict[str, Dict[str, Any]], 
                              default_move_generator=None) -> List[str]:
        """Fix inappropriate moves for this Pokemon."""
        changes = []
        inappropriate_moves = []
        
        # Find inappropriate moves
        for move in self.available_moves:
            if move not in move_database:
                inappropriate_moves.append(move)
                continue
            
            move_type = move_database[move]['type']
            is_stab = move_type.lower() in [t.lower() for t in self.types]
            is_normal = move_type.lower() == 'normal'
            
            if not is_stab and not is_normal:
                inappropriate_moves.append(move)
        
        # Remove inappropriate moves
        for move in inappropriate_moves:
            self.available_moves.remove(move)
            changes.append(f"Removed inappropriate move: {move}")
        
        # Add appropriate moves if needed
        if len(self.available_moves) < 2 and default_move_generator:
            new_moves = default_move_generator(self.types)
            for move in new_moves:
                if move not in self.available_moves and len(self.available_moves) < 4:
                    self.available_moves.append(move)
                    changes.append(f"Added appropriate move: {move}")
        
        # Ensure at least tackle if no moves
        if not self.available_moves:
            self.available_moves.append("tackle")
            changes.append("Added default move: tackle")
        
        return changes