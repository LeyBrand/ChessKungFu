import sys

from tournament.tournament_manager import TournamentManager, UnknownRoomError
from tests.conftest import STARTING_BOARD_TEXT


def test_no_network_modules_loaded():
    """The offline test: TournamentManager must not have pulled in
    asyncio/websockets as a side effect of import. If this ever fails,
    a layering boundary got crossed somewhere."""
    assert "websockets" not in sys.modules


def test_create_room_returns_id_and_room_is_playable():
    tm = TournamentManager()
    room_id = tm.create_room(STARTING_BOARD_TEXT, {"white": "p1", "black": "p2"})

    assert tm.room_exists(room_id)
    snapshot = tm.get_snapshot(room_id)
    assert snapshot["is_game_over"] is False
    assert snapshot["selected_cell"] is None


def test_handle_move_updates_room_state():
    tm = TournamentManager()
    room_id = tm.create_room(STARTING_BOARD_TEXT, {"white": "p1", "black": "p2"})

    tm.handle_move(room_id, "p1", 120, 340)
    snapshot = tm.get_snapshot(room_id)

    assert snapshot["selected_cell"] == (1, 3)  # 120//100, 340//100


def test_unknown_room_raises():
    tm = TournamentManager()
    import pytest
    with pytest.raises(UnknownRoomError):
        tm.get_snapshot("no-such-room")


def test_two_rooms_are_fully_independent():
    tm = TournamentManager()
    room_a = tm.create_room(STARTING_BOARD_TEXT, {"white": "p1", "black": "p2"})
    room_b = tm.create_room(STARTING_BOARD_TEXT, {"white": "p3", "black": "p4"})

    tm.handle_move(room_a, "p1", 100, 100)

    assert tm.get_snapshot(room_a)["selected_cell"] == (1, 1)
    assert tm.get_snapshot(room_b)["selected_cell"] is None
