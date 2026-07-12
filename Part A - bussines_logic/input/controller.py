from constants import EMPTY_CELL
from input.board_mapper import pixel_to_cell
from model.position import *

class Controller:
    def __init__(self):
        self.selected_pos = None

    def handle(self, command, board):
        name = command["name"]
        actions = {
            "click": self._handle_click,
            "print": self._handle_print,
            "wait": lambda args, board: None
        }
        
        name = command["name"]
        if name in actions:
            actions[name](command["args"], board)

    def _handle_click(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_cell(x, y)
        self.click(Position(col, row), board)

    def _handle_print(self, args, board):
        from data_io.board_printer import print_board
        print_board(board)

    def click(self, position, board):
        if not board.in_bounds(position):
            self.selected_pos = None
            return

        clicked_piece = board.get_piece_at(position)

        if self.selected_pos is None:
            # אם שום דבר לא בחור, בוחרים רק אם לחצנו על כלי
            if clicked_piece and clicked_piece != EMPTY_CELL:
                self.selected_pos = position
        else:
            selected_piece = board.get_piece_at(self.selected_pos)
            is_empty = clicked_piece is None or clicked_piece == EMPTY_CELL

            if not is_empty and clicked_piece.color == selected_piece.color:
                if position == self.selected_pos:
                    self.selected_pos = None  # ביטול בחירה בלחיצה חוזרת
                else:
                    self.selected_pos = position  # החלפת בחירה לכלי החדש
    
    # אם לחצנו על משבצת ריקה או על כלי אויב -> מנסים לבצע תנועה
            else:
                from rules.rule_engine import validate_move
                result = validate_move(board, selected_piece, position)
        
                if result == "ok":
                    board.remove_piece(self.selected_pos)
                    selected_piece.move_to(position)
                    board.place_piece(selected_piece, position)
        
                self.selected_pos = None