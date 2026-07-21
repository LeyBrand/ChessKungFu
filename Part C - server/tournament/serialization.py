"""
Explicit JSON (de)serialization - NOT pickle, NOT dump.

Why not pickle (per the instructor's note):
1. Security: pickle.loads() on data coming from the network (i.e. from
   the client) can execute arbitrary code. Never deserialize untrusted
   pickle input.
2. Coupling: pickle ties the wire format to Python's exact internal
   class layout. JSON is a plain, language-agnostic contract - the
   client doesn't need to be Python, and internal refactors don't
   silently break old messages.

Every function here is explicit about which fields go over the wire,
so the "contract" between layers is visible and reviewable - not an
accident of whatever attributes a class happens to have.
"""

import json


def snapshot_to_json(snapshot: dict) -> str:
    return json.dumps(snapshot)


def snapshot_from_json(raw: str) -> dict:
    return json.loads(raw)


def move_request_from_json(raw: str) -> dict:
    data = json.loads(raw)
    if "x" not in data or "y" not in data:
        raise ValueError("Invalid move message: missing 'x'/'y'")
    return data


def move_request_to_json(room_id: str, player_id: str, x: int, y: int) -> str:
    return json.dumps({"type": "MOVE", "room_id": room_id, "player_id": player_id, "x": x, "y": y})
