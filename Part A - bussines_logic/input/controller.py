from constants import EMPTY_CELL
from input.board_mapper import pixel_to_board

class Controller:
    def __init__(self):
        self.selected_pos = None

    def handle(self, command, board):
        name = command["name"]
        actions = {
            "click": self._handle_click,
            "print": self._handle_print
        }
        
        name = command["name"]
        if name in actions:
            actions[name](command["args"], board)

    def _handle_click(self, args, board):
        x, y = int(args[0]), int(args[1])
        col, row = pixel_to_board(x, y)
        self.click((row, col), board)

    def _handle_print(self, args, board):
        from data_io.board_printer import print_board
        print_board(board)

    def click(self, position, board):
        if self.selected_pos is None:
            if board.in_bounds(position):
                piece = board.get_piece_at(position)
                if piece is not None and piece != EMPTY_CELL:
                    self.selected_pos = position
        else:
            if board.in_bounds(position):
                piece = board.get_piece_at(self.selected_pos)
                
                from rules.rule_engine import validate_move
                result = validate_move(board, piece, position)
                
                if result == "ok":
                    board.remove_piece(self.selected_pos)
                    board.place_piece(piece, position)
                    self.selected_pos = None  # איפוס לאחר מהלך מוצלח
                else:
                    self.selected_pos = None 
            else:
                self.selected_pos = None