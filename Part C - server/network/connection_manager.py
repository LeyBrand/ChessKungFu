class ConnectionManager:
    """
    The network layer's own bookkeeping: who is connected, and which
    room are they sitting in - purely at the connection level. This is
    NOT where "is it this player's turn" lives (that's Room, Floor 2).
    """

    def __init__(self):
        self._connections = {}    # player_id -> websocket-like object
        self._room_players = {}   # room_id -> set of player_ids
        self._usernames = {}      # player_id -> username

    def register(self, player_id, websocket):
        self._connections[player_id] = websocket

    def unregister(self, player_id):
        self._connections.pop(player_id, None)
        self._usernames.pop(player_id, None)
        for players in self._room_players.values():
            players.discard(player_id)

    def join_room(self, room_id, player_id):
        self._room_players.setdefault(room_id, set()).add(player_id)

    def players_in_room(self, room_id):
        return set(self._room_players.get(room_id, set()))

    def get_websocket(self, player_id):
        return self._connections.get(player_id)

    def is_connected(self, player_id):
        return player_id in self._connections

    def set_username(self, player_id, username):
        self._usernames[player_id] = username

    def get_username(self, player_id):
        return self._usernames.get(player_id)