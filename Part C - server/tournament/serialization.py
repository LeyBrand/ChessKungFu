import json

def snapshot_to_json(snapshot: dict) -> str:
    return json.dumps(snapshot)

def move_request_from_json(raw: str) -> dict:
    data = json.loads(raw)
    if "x" not in data or "y" not in data:
        raise ValueError("Invalid nove message")
    return data

def snapshot_from_json(raw: str) -> dict:
    return json.loads(raw)

def move_request_to_json(room_id: str, player_id: str, x: int, y: int) -> str:
    return json.dumps({"type": "MOVE", "room_id": room_id, "player_id": player_id, "x": x, "y": y})
