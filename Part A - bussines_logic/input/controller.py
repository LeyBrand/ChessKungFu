# Part A - bussines_logic/input/controller.py
from constants import EMPTY_CELL
from input.board_mapper import pixel_to_cell
from model.position import Position
from engine.game_engine import GameEngine


class Controller:
    def __init__(self, engine: GameEngine):
        self.engine = engine
        self.current_selection = None
    
    def handle(self, command, board):
        """ממשק קלט ראשי"""
        name = command["name"]
        args = command.get("args", [])
        
        actions = {
            "click": self._handle_click,
            "print": self._handle_print,
            "wait": self._handle_wait,
            "jump": self._handle_jump,
            "snapshot": self._handle_snapshot
        }
        
        if name in actions:
            actions[name](args, board)

    def _handle_click(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        position = Position(col, row)
        
        if not board.in_bounds(position):
            self.engine.current_selection = None
            return
        
        piece = board.get_piece_at(position)
        
        if self.engine.current_selection is None:
            if piece is not None:
                self.engine.current_selection = position
        else:
            selected_piece = board.get_piece_at(self.engine.current_selection)
            if piece and selected_piece and piece.color == selected_piece.color:
                self.engine.current_selection = position
            else:
                result = self.engine.request_move(self.engine.current_selection, position)
                self.engine.current_selection = None
    def _handle_wait(self, args, board):
        ms = int(args[0])
        self.engine.wait(ms)
    
    def _handle_print(self, args, board):
        from data_io.board_printer import print_board
        print_board(board)
    
    def _handle_snapshot(self, args, board):
        snapshot = self.engine.snapshot()
        return snapshot
    
    def _handle_jump(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        pos = Position(col, row)
        result = self.engine.jump(pos)