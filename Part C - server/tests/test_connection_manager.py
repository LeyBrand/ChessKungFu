from network.connection_manager import ConnectionManager


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)


def test_register_and_lookup():
    cm = ConnectionManager()
    ws = FakeWebSocket()
    cm.register("p1", ws)
    assert cm.is_connected("p1")
    assert cm.get_websocket("p1") is ws


def test_join_room_tracks_membership():
    cm = ConnectionManager()
    cm.join_room("room-1", "p1")
    cm.join_room("room-1", "p2")
    assert cm.players_in_room("room-1") == {"p1", "p2"}


def test_unregister_removes_from_rooms_too():
    cm = ConnectionManager()
    cm.register("p1", FakeWebSocket())
    cm.join_room("room-1", "p1")
    cm.unregister("p1")
    assert not cm.is_connected("p1")
    assert "p1" not in cm.players_in_room("room-1")
