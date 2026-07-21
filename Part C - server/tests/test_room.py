import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "Part A - business_logic"))

import pytest
from api.game_api import GameSession
from events.event_bus import EventBus
from tournament.room import Room, UnknownPlayerError
from tests.conftest import STARTING_BOARD_TEXT


def make_room(player_ids=None):
    event_bus = EventBus()
    session = GameSession.new_game(STARTING_BOARD_TEXT, event_bus=event_bus)
    return Room("room-1", session, event_bus, player_ids or {"white": "p1", "black": "p2"})


def test_color_of_known_player():
    room = make_room()
    assert room.color_of("p1") == "white"
    assert room.color_of("p2") == "black"


def test_color_of_unknown_player_is_none():
    room = make_room()
    assert room.color_of("stranger") is None


def test_seated_player_can_move():
    room = make_room()
    room.handle_click("p1", 100, 100)
    assert room.get_snapshot()["selected_cell"] == (1, 1)


def test_unseated_player_is_rejected():
    room = make_room()
    with pytest.raises(UnknownPlayerError):
        room.handle_click("intruder", 100, 100)
