from dataclasses import dataclass, field

@dataclass
class GameSnapshot:
    board_width: int
    board_height: int
    pieces: list
    selected_cell: tuple | None
    game_over: bool
    timestamp: int
    move_history: list = field(default_factory=list)