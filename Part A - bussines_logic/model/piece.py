class PieceState:
    IDLE = "idle"
    MOVING = "moving"
    JUMPING = "jumping"
    CAPTURED = "captured"

class Piece:
    def __init__(self, id, color, kind, position):
        self.id = id
        self.color = color
        self.kind = kind
        self.position = position
        self.state = PieceState.IDLE
        self.start_position = position if kind == "P" else None
    
    def move_to(self, new_position):
        self.position = new_position

    def set_state(self, new_state):
        self.state = new_state

    def is_available(self):
        return self.state == PieceState.IDLE