"""
Integration tests for EventBus wiring through GameSession -> GameEngine
-> RealTimeArbiter. Unlike tests/unit, nothing here is mocked - a real
GameSession runs on a real (small, custom) board.
"""

from events.event_bus import EventBus
from api.game_api import GameSession


# חייל שחור ב-(0,5), צריח לבן ב-(0,6). מהלך אחד ישר קדימה = לכידה.
CAPTURE_BOARD_TEXT = """
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
bP .  .  .  .  .  .  .
wR .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
"""


def test_move_made_event_fires_on_accepted_move():
    bus = EventBus()
    received = []
    bus.subscribe("MOVE_MADE", lambda **move: received.append(move))

    session = GameSession.new_game(CAPTURE_BOARD_TEXT, event_bus=bus)
    session.handle_click(0 * 100, 6 * 100)  # select the white rook
    session.handle_click(0 * 100, 5 * 100)  # move it forward

    assert len(received) == 1
    assert received[0]["from"] == (0, 6)
    assert received[0]["to"] == (0, 5)
    assert received[0]["color"] == "white"


def test_piece_captured_event_fires_only_after_motion_completes():
    bus = EventBus()
    captured_events = []
    bus.subscribe("PIECE_CAPTURED", lambda **info: captured_events.append(info))

    session = GameSession.new_game(CAPTURE_BOARD_TEXT, event_bus=bus)
    session.handle_click(0 * 100, 6 * 100)
    session.handle_click(0 * 100, 5 * 100)

    # move accepted, but motion hasn't landed yet - no capture yet
    assert captured_events == []

    session.tick(1000)  # 1 square * MOVE_MS(1000) = duration of the motion

    assert len(captured_events) == 1
    assert captured_events[0]["color"] == "black"
    assert captured_events[0]["captured_by"] == "white"

# מתווסף ל: Part A - business_logic/tests/integration/scripts/test_event_bus_wiring.py

# מלך שחור ב-(0,5), צריח לבן ב-(0,6). מהלך אחד ישר קדימה = אכילת המלך.
GAME_OVER_BOARD_TEXT = """
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
bK .  .  .  .  .  .  .
wR .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
"""


def test_game_started_event_fires_on_session_creation():
    bus = EventBus()
    started_events = []
    bus.subscribe("GAME_STARTED", lambda **kwargs: started_events.append(kwargs))

    GameSession.new_game(GAME_OVER_BOARD_TEXT, event_bus=bus)

    assert len(started_events) == 1


def test_game_over_event_fires_when_king_is_captured():
    bus = EventBus()
    game_over_events = []
    bus.subscribe("GAME_OVER", lambda **kwargs: game_over_events.append(kwargs))

    session = GameSession.new_game(GAME_OVER_BOARD_TEXT, event_bus=bus)
    session.handle_click(0 * 100, 6 * 100)  # select the white rook
    session.handle_click(0 * 100, 5 * 100)  # move it onto the black king

    # move accepted, but motion hasn't landed yet - no GAME_OVER yet
    assert game_over_events == []

    session.tick(1000)  # 1 square * MOVE_MS(1000) = duration of the motion

    assert len(game_over_events) == 1