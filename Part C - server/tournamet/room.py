class Room:
    def __init__(self, room_id, session, event_bus, player_ids):
        self.room_id = room_id
        self._session = session
        self.event_bus = event_bus
        self.player_ids = player_ids

    def handle_click(self, player_id, x, y):
        self._session.handle_click(x, y,)

    def get_snapshot(self):
        return self._session.get_snapshot()
