import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PART_A_DIR = os.path.join(_CURRENT_DIR, "..", "..", "Part A - business_logic")
if _PART_A_DIR not in sys.path:
    sys.path.insert(0, os.path.abspath(_PART_A_DIR))

from api.game_api import GameSession  # noqa: E402  (import after sys.path setup)


class BusinessBridge:
    def __init__(self, board_text):
        self._session = GameSession.new_game(board_text)

    # ---- input ---------------------------------------------------------
    def handle_click(self, x, y):
        self._session.handle_click(x, y)

    def handle_jump(self, x, y):
        self._session.handle_jump(x, y)

    # ---- time ------------------------------------------------------------
    def tick(self, elapsed_ms):
        self._session.tick(elapsed_ms)

    # ---- state / output --------------------------------------------------
    def is_game_over(self):
        return self._session.is_game_over()

    def get_render_snapshot(self):
        return self._session.get_snapshot()
