from fastapi import APIRouter, HTTPException
import httpx
from models.pokemon import PokemonInfo, EvolutionChain
from pydantic import BaseModel

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
router = APIRouter()

class PokemonNameRequest(BaseModel):
    name: str

@router.post("/info")
async def get_pokemon_info(req: PokemonNameRequest):
    """Fetch Pokémon info from PokeAPI via POST request."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{POKEAPI_BASE_URL}/pokemon/{req.name.lower()}")
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Pokémon not found")
        return resp.json()
    
@router.get("/{name}", response_model=PokemonInfo)
async def get_pokemon(name: str):
    """Fetch basic Pokémon info from PokeAPI."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{POKEAPI_BASE_URL}/pokemon/{name.lower()}")
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Pokemon not found")
        data = resp.json()
    return PokemonInfo.from_pokeapi(data)

@router.get("/{name}/evolution")
async def get_pokemon_evolution(name: str):
    """Fetch and clean the Pokémon evolution chain."""
    async with httpx.AsyncClient() as client:
        # Step 1: Get species data
        species_resp = await client.get(f"{POKEAPI_BASE_URL}/pokemon-species/{name.lower()}")
        if species_resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Species not found")
        species_data = species_resp.json()

        # Step 2: Get evolution chain data
        evo_chain_url = species_data["evolution_chain"]["url"]
        evo_resp = await client.get(evo_chain_url)
        if evo_resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Evolution chain not found")
        evo_chain_data = evo_resp.json()["chain"]

    # Step 3: Recursively parse the chain
    def parse_chain(chain_node):
        evo_list = []

        # Handle missing evolution details
        evo_details_list = chain_node.get("evolution_details", [])
        if evo_details_list and isinstance(evo_details_list, list):
            details = evo_details_list[0]
            min_level = details.get("min_level")
            trigger = details.get("trigger", {}).get("name") if details.get("trigger") else None
        else:
            min_level = None
            trigger = None

        evo_list.append({
            "species": chain_node["species"]["name"],
            "min_level": min_level,
            "trigger": trigger
        })

        for evo in chain_node.get("evolves_to", []):
            evo_list.extend(parse_chain(evo))

        return evo_list

    return {"evolution_chain": parse_chain(evo_chain_data)}



def get_pokemon_data(name: str) -> dict:
    """Synchronous helper to fetch Pokémon data."""
    import requests
    url = f"{POKEAPI_BASE_URL}/pokemon/{name.lower()}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError(f"Pokémon '{name}' not found.")
    data = resp.json()
    pokemon = PokemonInfo.from_pokeapi(data)
    return pokemon.dict()
