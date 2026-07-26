import json
from dataclasses import dataclass, asdict

from constants import MessageType

@dataclass
class SnapshotMessage:
    data: dict
    type: MessageType = MessageType.SNAPSHOT

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class MatchFoundMessage:
    room_id: str
    color: str
    type: MessageType = MessageType.MATCH_FOUND

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class MatchNotFoundMessage:
    type: MessageType = MessageType.MATCH_NOT_FOUND

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class ErrorMessage:
    reason: str
    type: MessageType = MessageType.ERROR

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class OpponentDisconnectedMessage:
    seconds_remaining: int
    type: MessageType = MessageType.OPPONENT_DISCONNECTED

    def to_json(self) -> str:
        return json.dumps(asdict(self))

@dataclass
class OpponentReconnectedMessage:
    type: MessageType = MessageType.OPPONENT_RECONNECTED

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class LoginErrorMessage:
    reason: str
    type: MessageType = MessageType.LOGIN_ERROR

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
@dataclass
class LoginOkMessage:
    username: str
    rating: int
    type: MessageType = MessageType.LOGIN_OK

    def to_json(self) -> str:
        return json.dumps(asdict(self))
    
VALID_INCOMING_TYPES = {
    MessageType.JOIN_ROOM, MessageType.MOVE, MessageType.JUMP,
    MessageType.PLAY, MessageType.CANCEL_SEEK,
}

def parse_incoming(raw: str) -> dict:
    data = json.loads(raw)
    if "type" not in data:
        raise ValueError("Message missing 'type'")
    if data["type"] not in VALID_INCOMING_TYPES:
        raise ValueError(f"Unknown message type: {data['type']}")
    return data