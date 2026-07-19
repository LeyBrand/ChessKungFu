from events.event_bus import EventBus
from api.game_api import GameSession


# מלך שחור ב-(0,5), צריח לבן ב-(0,6). מהלך אחד ישר קדימה = לכידת מלך = סוף משחק.
KING_CAPTURE_BOARD_TEXT = """
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
bK .  .  .  .  .  .  .
wR .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
"""


def test_game_over_event_fires_only_after_king_capture_completes():
    bus = EventBus()
    game_over_events = []
    bus.subscribe("GAME_OVER", lambda **kw: game_over_events.append(kw))

    session = GameSession.new_game(KING_CAPTURE_BOARD_TEXT, event_bus=bus)
    session.handle_click(0 * 100, 6 * 100)  # select the white rook
    session.handle_click(0 * 100, 5 * 100)  # move onto the black king

    # move accepted, but motion hasn't landed yet - game isn't over yet
    assert game_over_events == []
    assert session.is_game_over() is False

    session.tick(1000)  # 1 square * MOVE_MS(1000) = duration of the motion

    assert len(game_over_events) == 1
    assert session.is_game_over() is True