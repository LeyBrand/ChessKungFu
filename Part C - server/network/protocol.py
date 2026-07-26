import json
from dataclasses import dataclass, asdict

@dataclass
class SnapshotMessage:
    data: dict
    type: str = "SNAPSHOT"

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class MatchFoundMessage:
    room_id: str
    color: str
    type: str = "MATCH_FOUND"

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class MatchNotFoundMessage:
    type: str = "MATCH_NOT_FOUND"

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class ErrorMessage:
    reason: str
    type: str = "ERROR"

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class OpponentDisconnectedMessage:
    seconds_remaining: int
    type: str = "OPPONENT_DISCONNECTED"

    def to_json(self) -> str:
        return json.dumps(asdict(self))

@dataclass
class OpponentReconnectedMessage:
    type: str = "OPPONENT_RECONNECTED"

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    

VALID_INCOMING_TYPES = {"JOIN_ROOM", "MOVE", "JUMP", "PLAY", "CANCEL_SEEK"}


def parse_incoming(raw: str) -> dict:
    data = json.loads(raw)
    if "type" not in data:
        raise ValueError("Message missing 'type'")
    if data["type"] not in VALID_INCOMING_TYPES:
        raise ValueError(f"Unknown message type: {data['type']}")
    return data