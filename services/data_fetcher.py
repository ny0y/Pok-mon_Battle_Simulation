import httpx
from models.pokemon import PokemonInfo, EvolutionChain

POKEAPI_BASE = "https://pokeapi.co/api/v2"

async def fetch_pokemon_data(name: str) -> PokemonInfo | None:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{POKEAPI_BASE}/pokemon/{name.lower()}")
        if resp.status_code != 200:
            return None
        data = resp.json()  # No await here
        return PokemonInfo.from_pokeapi(data)

async def fetch_species_data(name: str) -> EvolutionChain | None:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{POKEAPI_BASE}/pokemon-species/{name.lower()}")
        if resp.status_code != 200:
            return None
        species = resp.json()  
        evo_url = species["evolution_chain"]["url"]
        evo_resp = await client.get(evo_url)
        if evo_resp.status_code != 200:
            return None
        evo_data = evo_resp.json()  
        return EvolutionChain.from_pokeapi(evo_data)
