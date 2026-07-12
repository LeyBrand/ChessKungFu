# Part A - bussines_logic/input/controller.py
from constants import EMPTY_CELL
from input.board_mapper import pixel_to_cell
from model.position import Position
from model.piece import PieceState
from engine.game_engine import GameEngine


class Controller:
    """
    קונטרולר - מקבל input וקוראה לengine
    לא מחזיק state! ה-engine עושה את זה
    
    Malki's Architecture:
    - Controller זה רק כלי לקבלת input
    - כל הlogic הולך לengine
    """
    
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
    
    # input/controller.py
    def _handle_click(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        position = Position(col, row)
        
        if not board.in_bounds(position):
            self.engine.current_selection = None  # ← עדכן engine
            return
        
        piece = board.get_piece_at(position)
        
        if self.engine.current_selection is None:  # ← קרא מengine
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
        """צפה כמה מילישניות"""
        ms = int(args[0])
        self.engine.wait(ms)
    
    def _handle_print(self, args, board):
        """הדפס את הboard"""
        from data_io.board_printer import print_board
        print_board(board)
    
    def _handle_snapshot(self, args, board):
        """שמור snapshot"""
        snapshot = self.engine.snapshot()
        return snapshot
    
    # input/controller.py
    def _handle_jump(self, args, board):
        """קפוץ ישירות"""
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        pos = Position(col, row)
        result = self.engine.jump(pos)