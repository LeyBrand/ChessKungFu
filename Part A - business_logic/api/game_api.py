"""
STUB NOTICE
-----------
This is NOT your real Part A. Your actual GameSession (real board + real
chess rules) was never shown to me in this conversation - only its public
interface, inferred from how Part B calls it (business_bridge.py,
frame_renderer.py). This stub implements that exact interface with
trivial behavior, so that TournamentManager / Room / the network layer
can be tested honestly against the *real contract*, without pretending
to also test chess rules that live in your actual file.

Replace this file with your real one - nothing in Part C or Part B
should need to change, since they only depend on this interface.
"""


class GameSession:
    def __init__(self, board_text, event_bus=None):
        self.board_text = board_text
        self.event_bus = event_bus
        self.selected_cell = None
        self._elapsed_ms = 0
        self._game_over = False
        self.pieces = []  # real Part A fills this from board_text

    @classmethod
    def new_game(cls, board_text, event_bus=None):
        return cls(board_text, event_bus=event_bus)

    # ---- input -----------------------------------------------------
    def handle_click(self, x, y):
        cell = (x // 100, y // 100)
        self.selected_cell = None if self.selected_cell == cell else cell

    def handle_jump(self, x, y):
        pass

    # ---- time --------------------------------------------------------
    def tick(self, elapsed_ms):
        self._elapsed_ms += elapsed_ms

    # ---- state / output ------------------------------------------------
    def is_game_over(self):
        return self._game_over

    def get_snapshot(self):
        return {
            "timestamp_ms": self._elapsed_ms,
            "selected_cell": self.selected_cell,
            "pieces": self.pieces,
            "is_game_over": self._game_over,
        }
