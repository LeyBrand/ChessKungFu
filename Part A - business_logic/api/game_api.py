from model.game_state import GameState
from engine.game_engine import GameEngine
from input.controller import Controller
from data_io.board_parser import parse_board
from view.renderer import build_board_snapshot


class GameSession:
    def __init__(self, board):
        self.state = GameState(board)
        self.engine = GameEngine(self.state)
        self.controller = Controller(self.engine)

    @classmethod
    def new_game(cls, board_text):
        """Build a GameSession directly from a textual board layout."""
        board = parse_board(board_text)
        if board is None:
            raise ValueError("Could not parse board text")
        return cls(board)

    # ---- input -----------------------------------------------------
    def handle_click(self, x, y):
        self.controller.handle({"name": "click", "args": [str(x), str(y)]}, self.state.board)

    def handle_jump(self, x, y):
        self.controller.handle({"name": "jump", "args": [str(x), str(y)]}, self.state.board)

    # ---- time --------------------------------------------------------
    def tick(self, elapsed_ms):
        self.engine.wait(elapsed_ms)

    # ---- state / output ----------------------------------------------
    def is_game_over(self):
        return self.state.game_over

    def get_snapshot(self):
        """Returns a plain dict ready for rendering:
        {pieces, selected_cell, is_game_over, timestamp_ms}
        """
        engine_snapshot = self.engine.snapshot(selected_pos=self.controller.selected_pos)
        return build_board_snapshot(engine_snapshot)