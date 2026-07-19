from events.event_bus import EventBus
from api.game_api import GameSession

STARTING_BOARD_TEXT = """
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR
"""

bus = EventBus()
bus.subscribe("MOVE_MADE", lambda **move: print("MOVE_MADE event received:", move))

session = GameSession.new_game(STARTING_BOARD_TEXT, event_bus=bus)

# קליק ראשון = בחירת כלי (חייל לבן בעמודה 0, שורה 6 - פינה שמאלית תחתונה)
session.handle_click(0 * 100, 6 * 100)
# קליק שני = יעד - צעד אחד קדימה
session.handle_click(0 * 100, 5 * 100)