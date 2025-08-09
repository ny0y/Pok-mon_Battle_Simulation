from fastapi import APIRouter, HTTPException, Query
import httpx

router = APIRouter()

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"

async def fetch_evolution_chain(client: httpx.AsyncClient, name: str):
    # Step 1: Get species data
    species_resp = await client.get(f"{POKEAPI_BASE_URL}/pokemon-species/{name.lower()}")
    if species_resp.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Species not found for {name}")
    species_data = species_resp.json()

    # Step 2: Get evolution chain URL
    evo_chain_url = species_data.get("evolution_chain", {}).get("url")
    if not evo_chain_url:
        return None

    evo_resp = await client.get(evo_chain_url)
    if evo_resp.status_code != 200:
        raise HTTPException(status_code=404, detail="Evolution chain not found")
    evo_chain_data = evo_resp.json().get("chain")

    # Step 3: Parse evolution chain recursively
    def parse_chain(chain_node):
        evo_list = []

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

    return parse_chain(evo_chain_data)

@router.get("/index")
async def pokemon_index(
    type: str = Query(None, description="Filter by Pokémon type"),
    name: str = Query(None, description="Search Pokémon by name (partial match)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Number of results per page"),
    including_evolution: bool = Query(False, alias="including_evolution", description="Include evolution chain info")
):
    async with httpx.AsyncClient() as client:
        # Step 1: Get Pokémon list based on type or all
        if type:
            type_resp = await client.get(f"{POKEAPI_BASE_URL}/type/{type.lower()}")
            if type_resp.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Type '{type}' not found")
            data = type_resp.json()
            pokemon_list = [p["pokemon"]["name"] for p in data["pokemon"]]
        else:
            all_resp = await client.get(f"{POKEAPI_BASE_URL}/pokemon?limit=2000")
            if all_resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to get Pokémon list")
            all_data = all_resp.json()
            pokemon_list = [p["name"] for p in all_data["results"]]

        # Step 2: Filter by name if provided (case-insensitive partial match)
        if name:
            pokemon_list = [p for p in pokemon_list if name.lower() in p.lower()]

        total_count = len(pokemon_list)

        # Step 3: Pagination bounds
        max_page = max(1, (total_count + page_size - 1) // page_size)
        if page > max_page:
            page = max_page

        start = (page - 1) * page_size
        end = start + page_size
        paginated_list = pokemon_list[start:end]

        results = []
        # Step 4: Fetch full details for each Pokémon on current page
        for p_name in paginated_list:
            p_resp = await client.get(f"{POKEAPI_BASE_URL}/pokemon/{p_name}")
            if p_resp.status_code != 200:
                continue  # skip failed
            p_data = p_resp.json()
            entry = {
                "name": p_data["name"],
                "types": [t["type"]["name"] for t in p_data["types"]],
                "abilities": [a["ability"]["name"] for a in p_data["abilities"]],
                "stats": {s["stat"]["name"]: s["base_stat"] for s in p_data["stats"]},
                "moves": [m["move"]["name"] for m in p_data["moves"]],
            }
            # Optionally include evolution chain
            if including_evolution:
                try:
                    evolution_chain = await fetch_evolution_chain(client, p_name)
                    entry["evolution_chain"] = evolution_chain
                except HTTPException:
                    entry["evolution_chain"] = None

            results.append(entry)

        return {
            "count": total_count,
            "page": page,
            "page_size": page_size,
            "results": results
        }
