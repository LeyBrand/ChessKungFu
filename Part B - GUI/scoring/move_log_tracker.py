class MoveLogTracker:
    """
    Reactive move log: subscribes to MOVE_MADE instead of reading
    board_snapshot["move_history"] every frame. Each event payload is
    already shaped exactly like the move dicts frame_renderer expects
    (from, to, piece_id, color, kind, captured, time_ms, and is_jump for
    jumps) - so nothing downstream (_format_move_san, _format_time) needs
    to change.
    """

    def __init__(self, event_bus=None):
        self.moves = []

        if event_bus is not None:
            event_bus.subscribe("MOVE_MADE", self._on_move_made)

    def _on_move_made(self, **move):
        self.moves.append(move)

    def get_moves(self):
        return list(self.moves)