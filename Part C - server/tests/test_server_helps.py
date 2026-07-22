import pytest

from network.server import _find_pending_reconnect, _notify_opponent


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)


class FakeConnectionManager:
    def __init__(self, websockets_by_player):
        self._websockets = websockets_by_player

    def get_websocket(self, player_id):
        return self._websockets.get(player_id)


class FakeTournamentManager:
    def __init__(self, player_ids):
        self._player_ids = player_ids

    def get_player_ids(self, room_id):
        return self._player_ids


def test_find_pending_reconnect_matches_by_username():
    disconnected = {("room1", "white"): "alice"}
    assert _find_pending_reconnect("alice", disconnected) == ("room1", "white")


def test_find_pending_reconnect_returns_none_for_unknown_username():
    disconnected = {("room1", "white"): "alice"}
    assert _find_pending_reconnect("bob", disconnected) is None


def test_find_pending_reconnect_empty_pool():
    assert _find_pending_reconnect("alice", {}) is None


@pytest.mark.asyncio
async def test_notify_opponent_sends_to_the_other_color():
    ws = FakeWebSocket()
    tm = FakeTournamentManager({"white": "p1", "black": "p2"})
    cm = FakeConnectionManager({"p2": ws})

    await _notify_opponent("room1", "white", "hello", tm, cm)

    assert ws.sent == ["hello"]


@pytest.mark.asyncio
async def test_notify_opponent_no_op_if_opponent_not_seated():
    tm = FakeTournamentManager({"white": "p1"})  # black not seated
    cm = FakeConnectionManager({})

    # should not raise, just silently do nothing
    await _notify_opponent("room1", "white", "hello", tm, cm)


@pytest.mark.asyncio
async def test_notify_opponent_no_op_if_opponent_has_no_websocket():
    tm = FakeTournamentManager({"white": "p1", "black": "p2"})
    cm = FakeConnectionManager({})  # p2 registered no websocket

    await _notify_opponent("room1", "white", "hello", tm, cm)