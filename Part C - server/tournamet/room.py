class Room:
    def __init__(self, room_id, session, event_bus, player_ids=None):
        self.room_id = room_id
        self._session = session
        self.event_bus = event_bus
        self.player_ids = dict(player_ids or {})

    def seat(self, color, player_id):
        if color not in("white", "black"):
            raise ValueError(f"Invalid color: {color}")
        if color in self.player_ids:
            raise ValueError(f"Color {color} already taken in room {self.room_id}")
        self.player_ids[color] = player_id

    def is_full(self):
        return "white" in self.player_ids and "black" in self.player_ids
    
    def handle_click(self, player_id, x, y):
        self._session.handle_click(x, y,)

    def get_snapshot(self):
        return self._session.get_snapshot()
