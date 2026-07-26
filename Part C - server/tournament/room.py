from constants import Color, value_of

class UnknownPlayerError(ValueError):
    pass # missing implement

class Room:
    def __init__(self, room_id, session, event_bus, player_ids=None):
        self.room_id = room_id
        self._session = session
        self.event_bus = event_bus
        self.player_ids = dict(player_ids or {})
        self.scores = {Color.WHITE: 0, Color.BLACK: 0}
        if self.event_bus is not None:
            self.event_bus.subscribe("PIECE_CAPTURED", self._on_piece_captured)

    def _on_piece_captured(self, piece_id, kind, color, captured_by, time_ms):
        self.scores[captured_by] = self.scores.get(captured_by, 0) + value_of(kind)

    def seat(self, color, player_id):
        if color not in (Color.WHITE, Color.BLACK):
            raise ValueError(f"Invalid color: {color}")
        if color in self.player_ids:
            raise ValueError(f"Color {color} already taken in room {self.room_id}")
        self.player_ids[color] = player_id

    def is_full(self):
        return Color.WHITE in self.player_ids and Color.BLACK in self.player_ids
    
    def handle_click(self, player_id, x, y):
        color = self.color_of(player_id)
        if color is None:
            raise UnknownPlayerError(f"{player_id} is not seated in room {self.room_id}")
        self._session.handle_click(x, y, color)
    
    def handle_jump(self, player_id, x, y):
        color = self.color_of(player_id)
        if color is None:
            raise UnknownPlayerError(f"{player_id} is not seated in room {self.room_id}")
        self._session.handle_jump(x, y, color)

    def get_snapshot(self):
        snapshot = self._session.get_snapshot()
        snapshot["scores"] = dict(self.scores)
        return snapshot
    
    def color_of(self, player_id):
        for color, pid in self.player_ids.items():
            if pid == player_id:
                return color
        return None
    
    def reseat(self, color, new_player_id):
        """Like seat(), but overwrites whoever's already there - used when
        a disconnected player reconnects and needs their seat back."""
        if color not in (Color.WHITE, Color.BLACK):
            raise ValueError(f"Invalid color: {color}")
        self.player_ids[color] = new_player_id

    def resign(self, color):
        winner = Color.BLACK if color == Color.WHITE else Color.WHITE
        self._session.force_game_over(winner)
    
    def tick(self, elapsed_ms):
        self._session.tick(elapsed_ms)