from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GameSnapshot:
    board_width: int
    board_height: int
    pieces: list
    selected_cell: tuple | None
    game_over: bool
    timestamp: int
    move_history: list = field(default_factory=list)

@dataclass
class MotionSnapshot:
    from_cell: tuple
    to_cell: tuple
    progress: float

    def to_dict(self):
        return {"from": self.from_cell, "to": self.to_cell, "progress": self.progress}
    
    @classmethod
    def from_dict(cls, data):
        return cls(from_cell=tuple(data["from"]), to_cell=tuple(data["to"]), progress=data["progress"])
    
@dataclass
class PieceSnapshot:
    id: str
    kind: str
    color: str
    position: tuple
    motion: Optional[MotionSnapshot]
    state: str

    def to_dict(self):
        return {
            "id": self.id, "kind": self.kind, "color": self.color,
            "position": self.position,
            "motion": self.motion.to_dict() if self.motion else None,
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"], kind=data["kind"], color=data["color"],
            position=tuple(data["position"]),
            motion=MotionSnapshot.from_dict(data["motion"]) if data.get("motion") else None,
            state=data["state"],
        )
    
@dataclass
class BoardSnapshot:
    pieces: list
    selected_cell: Optional[tuple]
    is_game_over: bool
    timestamp_ms: int
    move_history: list = field(default_factory=list)
    scores: dict = field(default_factory=lambda: {"white": 0, "black": 0})

    def to_dict(self):
        return {
            "pieces": [p.to_dict() for p in self.pieces],
            "selected_cell": self.selected_cell,
            "is_game_over": self.is_game_over,
            "timestamp_ms": self.timestamp_ms,
            "move_history": self.move_history,
            "scores": self.scores,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            pieces=[PieceSnapshot.from_dict(p) for p in data["pieces"]],
            selected_cell=tuple(data["selected_cell"]) if data.get("selected_cell") else None,
            is_game_over=data["is_game_over"],
            timestamp_ms=data["timestamp_ms"],
            move_history=data.get("move_history", []),
            scores=data.get("scores", {"white": 0, "black": 0}),
        )