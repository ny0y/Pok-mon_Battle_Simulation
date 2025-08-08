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

    def as_hashable_state(self) -> tuple:
        """
        Canonical, hashable snapshot for Q-learning keys.
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