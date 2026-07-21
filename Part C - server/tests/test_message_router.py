import json
import pytest

from tournament.tournament_manager import TournamentManager
from network.connection_manager import ConnectionManager
from network.message_router import handle_message
from tests.conftest import STARTING_BOARD_TEXT


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)


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
