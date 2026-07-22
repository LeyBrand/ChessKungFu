import sys
import ast
import inspect

from tournament import tournament_manager
from tournament.tournament_manager import TournamentManager, UnknownRoomError
from tests.conftest import STARTING_BOARD_TEXT


import ast
import inspect
from tournament import tournament_manager

def test_tournament_manager_module_does_not_import_network_libs():
    source = inspect.getsource(tournament_manager)
    tree = ast.parse(source)
    imported_names = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "websockets" not in imported_names
    assert "asyncio" not in imported_names


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
