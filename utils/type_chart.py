import json
from pathlib import Path

def load_type_chart() -> dict:
    path = Path(__file__).parent.parent / "data" / "type_chart.json"
    with open(path, "r") as f:
        return json.load(f)

TYPE_EFFECTIVENESS = load_type_chart()
