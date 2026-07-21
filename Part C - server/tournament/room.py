class UnknownPlayerError(ValueError):
    pass


class Room:
    """
    Owns exactly one GameSession plus the mapping of which player_id plays
    which color. Knows about "players" and "rooms" - GameSession does not.
    """

    def __init__(self, room_id, session, event_bus, player_ids):
        self.room_id = room_id
        self._session = session
        self.event_bus = event_bus
        self.player_ids = dict(player_ids)  # e.g. {"white": "p1", "black": "p2"}

    def color_of(self, player_id):
        for color, pid in self.player_ids.items():
            if pid == player_id:
                return color
        return None

    def handle_click(self, player_id, x, y):
        if self.color_of(player_id) is None:
            raise UnknownPlayerError(f"{player_id} is not seated in room {self.room_id}")
        self._session.handle_click(x, y)

    def handle_jump(self, player_id, x, y):
        if self.color_of(player_id) is None:
            raise UnknownPlayerError(f"{player_id} is not seated in room {self.room_id}")
        self._session.handle_jump(x, y)

    def tick(self, elapsed_ms):
        self._session.tick(elapsed_ms)

    def is_game_over(self):
        return self._session.is_game_over()

    def get_snapshot(self):
        return self._session.get_snapshot()
