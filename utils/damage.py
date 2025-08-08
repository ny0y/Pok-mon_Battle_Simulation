from utils.type_chart import TYPE_EFFECTIVENESS

# Full type effectiveness chart simplified for brevity
TYPE_EFFECTIVENESS = {
    "normal": {"rock": 0.5, "ghost": 0, "steel": 0.5},
    "fire": {"grass": 2, "water": 0.5, "fire": 0.5, "rock": 0.5, "bug": 2, "ice": 2, "steel": 2},
    "water": {"fire": 2, "water": 0.5, "grass": 0.5, "ground": 2, "rock": 2, "dragon": 0.5},
    "grass": {"water": 2, "fire": 0.5, "grass": 0.5, "poison": 0.5, "ground": 2, "flying": 0.5, "bug": 0.5, "rock": 2, "dragon": 0.5, "steel": 0.5},
    "electric": {"water": 2, "electric": 0.5, "grass": 0.5, "ground": 0, "flying": 2, "dragon": 0.5},
    # ... fill in rest as needed
}


def calculate_damage(attack: int, defense: int, power: int, multiplier: float) -> float:
    base = (((2 * 50 / 5 + 2) * power * attack / defense) / 50) + 2
    return base * multiplier
