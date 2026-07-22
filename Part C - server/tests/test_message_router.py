import json
import pytest

from tournament.tournament_manager import TournamentManager
from network.connection_manager import ConnectionManager
from network.message_router import handle_message
from tests.conftest import STARTING_BOARD_TEXT
from tournament.matchmaker import Matchmaker

class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)

class FakePlayerStore:
    def __init__(self, ratings):
        self._ratings = ratings

    def get_rating(self, username):
        return self._ratings[username]

@pytest.mark.asyncio
async def test_join_then_move_broadcasts_snapshot_to_both_players():
    tm = TournamentManager()
    cm = ConnectionManager()
    room_id = tm.create_room(STARTING_BOARD_TEXT, {"white": "p1", "black": "p2"})

    ws1, ws2 = FakeWebSocket(), FakeWebSocket()
    cm.register("p1", ws1)
    cm.register("p2", ws2)

    await handle_message(json.dumps({"type": "JOIN_ROOM", "room_id": room_id}), "p1", tm, cm, ws1)
    await handle_message(json.dumps({"type": "JOIN_ROOM", "room_id": room_id}), "p2", tm, cm, ws2)

    move_msg = json.dumps({"type": "MOVE", "room_id": room_id, "x": 100, "y": 100})
    await handle_message(move_msg, "p1", tm, cm, ws1)

    assert len(ws1.sent) == 1
    assert len(ws2.sent) == 1
    payload = json.loads(ws1.sent[0])
    assert payload["type"] == "SNAPSHOT"
    assert payload["data"]["selected_cell"] == [1, 1]  # JSON round-trip: tuple -> list


@pytest.mark.asyncio
async def test_move_in_unknown_room_sends_error_not_exception():
    tm = TournamentManager()
    cm = ConnectionManager()
    ws = FakeWebSocket()
    cm.register("p1", ws)

    move_msg = json.dumps({"type": "MOVE", "room_id": "ghost-room", "x": 0, "y": 0})
    await handle_message(move_msg, "p1", tm, cm, ws)

    assert len(ws.sent) == 1
    payload = json.loads(ws.sent[0])
    assert payload["type"] == "ERROR"


@pytest.mark.asyncio
async def test_malformed_message_sends_error():
    tm = TournamentManager()
    cm = ConnectionManager()
    ws = FakeWebSocket()

    await handle_message("not-json-at-all", "p1", tm, cm, ws)

    assert len(ws.sent) == 1
    payload = json.loads(ws.sent[0])
    assert payload["type"] == "ERROR"

@pytest.mark.asyncio
async def test_play_with_no_opponent_waits_silently():
    tm = TournamentManager()
    cm = ConnectionManager()
    matchmaker = Matchmaker()
    player_store = FakePlayerStore({"alice": 1200})

    ws = FakeWebSocket()
    cm.register("p1", ws)
    cm.set_username("p1", "alice")

    await handle_message(json.dumps({"type": "PLAY"}), "p1", tm, cm, ws, matchmaker, player_store)

    assert ws.sent == []
    assert matchmaker.is_waiting("p1")


@pytest.mark.asyncio
async def test_play_matches_two_players_and_sends_match_found_to_both():
    tm = TournamentManager()
    cm = ConnectionManager()
    matchmaker = Matchmaker()
    player_store = FakePlayerStore({"alice": 1200, "bob": 1210})

    ws1, ws2 = FakeWebSocket(), FakeWebSocket()
    cm.register("p1", ws1)
    cm.set_username("p1", "alice")
    cm.register("p2", ws2)
    cm.set_username("p2", "bob")

    await handle_message(json.dumps({"type": "PLAY"}), "p1", tm, cm, ws1, matchmaker, player_store)
    assert ws1.sent == []  # still waiting, nothing sent yet

    await handle_message(json.dumps({"type": "PLAY"}), "p2", tm, cm, ws2, matchmaker, player_store)

    assert len(ws1.sent) == 1
    assert len(ws2.sent) == 1
    payload1 = json.loads(ws1.sent[0])
    payload2 = json.loads(ws2.sent[0])
    assert payload1["type"] == "MATCH_FOUND"
    assert payload2["type"] == "MATCH_FOUND"
    assert payload1["room_id"] == payload2["room_id"]
    assert {payload1["color"], payload2["color"]} == {"white", "black"}


@pytest.mark.asyncio
async def test_cancel_seek_removes_player_from_pool():
    tm = TournamentManager()
    cm = ConnectionManager()
    matchmaker = Matchmaker()
    player_store = FakePlayerStore({"alice": 1200})

    ws = FakeWebSocket()
    cm.register("p1", ws)
    cm.set_username("p1", "alice")

    await handle_message(json.dumps({"type": "PLAY"}), "p1", tm, cm, ws, matchmaker, player_store)
    assert matchmaker.is_waiting("p1")

    await handle_message(json.dumps({"type": "CANCEL_SEEK"}), "p1", tm, cm, ws, matchmaker, player_store)
    assert not matchmaker.is_waiting("p1")