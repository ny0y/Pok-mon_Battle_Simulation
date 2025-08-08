from api.play import AI_POKEMON_POOL, TYPE_EFFECTIVENESS
import random

def get_type_advantage_score(attacker_types, defender_types):
    score = 0
    for a_type in attacker_types:
        for d_type in defender_types:
            score += TYPE_EFFECTIVENESS.get(a_type, {}).get(d_type, 1.0)
    return score

def select_ai_pokemon(player_types):
    best_pokemon = None
    best_score = -1

    for poke in AI_POKEMON_POOL:
        score = get_type_advantage_score(poke["types"], player_types)
        if score > best_score:
            best_score = score
            best_pokemon = poke

    if best_pokemon is None:
        best_pokemon = random.choice(AI_POKEMON_POOL)

    return best_pokemon
