"""
PlayerRegistry: maps a connected websocket to a (username, color) pair.
Pure bookkeeping - no networking, no I/O - so it's trivial to unit test.
"""


class ServerFullError(Exception):
    pass


class PlayerRegistry:
    MAX_PLAYERS = 2

    def __init__(self):
        self._players = {}  # websocket -> {"username": str, "color": "white"|"black"}

    def is_full(self):
        return len(self._players) >= self.MAX_PLAYERS

    def register(self, websocket, username):
        if self.is_full():
            raise ServerFullError(f"Server already has {self.MAX_PLAYERS} players")

        taken_colors = {player["color"] for player in self._players.values()}
        color = "white" if "white" not in taken_colors else "black"
        self._players[websocket] = {"username": username, "color": color}
        return color

    def unregister(self, websocket):
        self._players.pop(websocket, None)

    def get_player(self, websocket):
        return self._players.get(websocket)