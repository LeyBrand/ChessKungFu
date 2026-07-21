from scoring.piece_values import value_of


class ScoreTracker:
    def __init__(self, event_bus=None):
        self.scores = {"white": 0, "black": 0}

        if event_bus is not None:
            event_bus.subscribe("PIECE_CAPTURED", self._on_piece_captured)

    def _on_piece_captured(self, piece_id, kind, color, captured_by, time_ms):
        self.scores[captured_by] += value_of(kind)

    def get_scores(self):
        return dict(self.scores)
