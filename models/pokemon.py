import requests
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class PokemonInfo(BaseModel):
    name: str
    types: List[str]
    abilities: List[str]
    stats: Dict[str, int]
    moves: List[str]

    @classmethod
    def from_pokeapi(cls, data: dict):
        return cls(
            name=data["name"],
            types=[t["type"]["name"] for t in data["types"]],
            abilities=[a["ability"]["name"] for a in data["abilities"]],
            stats={stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]},
            moves=[m["move"]["name"] for m in data["moves"][:15]],
        )

class EvolutionChain(BaseModel):
    chain: dict

    @classmethod
    def from_pokeapi(cls, data: dict):
        return cls(chain=data.get("chain", {}))

# NEW FUNCTION
def get_pokemon_data(name: str) -> PokemonInfo:
    """Fetch Pokémon info from PokéAPI."""
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    resp = requests.get(url)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Pokémon '{name}' not found.")

    data = resp.json()
    return PokemonInfo.from_pokeapi(data)
