from constants import Color

class UnknownPlayerError(ValueError):
    pass # missing implement

class Room:
    def __init__(self, room_id, session, event_bus, player_ids=None):
        self.room_id = room_id
        self._session = session
        self.event_bus = event_bus
        self.player_ids = dict(player_ids or {})

    def seat(self, color, player_id):
        if color not in (Color.WHITE, Color.BLACK):
            raise ValueError(f"Invalid color: {color}")
        if color in self.player_ids:
            raise ValueError(f"Color {color} already taken in room {self.room_id}")
        self.player_ids[color] = player_id

    def is_full(self):
        return Color.WHITE in self.player_ids and Color.BLACK in self.player_ids
    def handle_click(self, player_id, x, y):
        if self.color_of(player_id) is None:
            raise UnknownPlayerError(f"{player_id} is not seated in room {self.room_id}")
        self._session.handle_click(x, y)
    
    def get_snapshot(self):
        return self._session.get_snapshot()
    
    def color_of(self, player_id):
        for color, pid in self.player_ids.items():
            if pid == player_id:
                return color
        return None
