"""
The "language" spoken over the wire. JSON only (see tournament/serialization.py
for why pickle/dump are off the table). This is the one place that defines
what a valid incoming/outgoing message looks like.
"""

import json

VALID_INCOMING_TYPES = {"JOIN_ROOM", "MOVE", "JUMP"}


def parse_incoming(raw: str) -> dict:
    data = json.loads(raw)
    if "type" not in data:
        raise ValueError("Message missing 'type'")
    if data["type"] not in VALID_INCOMING_TYPES:
        raise ValueError(f"Unknown message type: {data['type']}")
    return data


def make_snapshot_message(snapshot: dict) -> str:
    return json.dumps({"type": "SNAPSHOT", "data": snapshot})


def make_error_message(reason: str) -> str:
    return json.dumps({"type": "ERROR", "reason": reason})
