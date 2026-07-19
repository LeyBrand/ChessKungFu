from events.event_bus import EventBus
from api.game_api import GameSession

# לוח מותאם אישית ופשוט, לא לוח פתיחה רגיל: רק שני כלים,
# חייל שחור ב-(0,5) וצריח לבן ב-(0,6) - מהלך אחד ישר קדימה = לכידה.
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

bus = EventBus()
bus.subscribe("MOVE_MADE", lambda **move: print("MOVE_MADE event received:", move))
bus.subscribe("PIECE_CAPTURED", lambda **info: print("PIECE_CAPTURED event received:", info))

session = GameSession.new_game(CAPTURE_BOARD_TEXT, event_bus=bus)

# קליק ראשון = בחירת הצריח הלבן ב-(0,6)
session.handle_click(0 * 100, 6 * 100)
# קליק שני = יעד - (0,5), איפה שעומד החייל השחור
session.handle_click(0 * 100, 5 * 100)

print("--- לפני tick: המהלך אושר אבל עדיין 'בדרך', לא נחת עדיין ---")

# המהלך הוא מרחק של משבצת אחת -> duration_ms = 1 * MOVE_MS = 1000
# מקדמים את השעון עד בדיוק הרגע שבו המהלך "נוחת" בפועל.
session.tick(1000)

print("--- אחרי tick(1000): המהלך היה אמור לנחות, והלכידה להתרחש ---")