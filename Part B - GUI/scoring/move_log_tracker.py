class MoveLogTracker:
    def __init__(self, event_bus=None):
        self.moves = []

        if event_bus is not None:
            event_bus.subscribe("MOVE_MADE", self._on_move_made)

    def _on_move_made(self, **move):
        self.moves.append(move)

    def get_moves(self):
        return list(self.moves)