import json

def snapshot_to_json(snapshot: dict) -> str:
    return json.dumps(snapshot)

def move_request_from_json(raw: str) -> dict:
    data = json.loads(raw)
    if "x" not in data or "y" not in data:
        raise ValueError("Invalid nove message")
    return data