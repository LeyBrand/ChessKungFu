from constants import MOVE_MS

class Motion:
    def __init__(self, piece, start_pos, end_pos, start_time):
        self.piece = piece
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.start_time = start_time

        distance = max(abs(end_pos.col - start_pos.col), abs(end_pos.row - start_pos.row))
        self.duration_ms = distance * MOVE_MS

    def is_complete(self, current_time):
        return current_time - self.start_time >= self.duration_ms