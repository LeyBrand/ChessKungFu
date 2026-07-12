from constants import EMPTY_CELL
from input.board_mapper import pixel_to_cell

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
        col, row = pixel_to_cell(x, y)
        self.click((row, col), board)

    def _handle_print(self, args, board):
        from data_io.board_printer import print_board
        print_board(board)

    def click(self, position, board):
        if not board.in_bounds(position):
            self.selected_pos = None
            return
        
        clicked_piece = board.get_piece_at(position)

        if self.selected_pos is None:
            if clicked_piece is not None and clicked_piece != EMPTY_CELL:
                self.selected_pos = position
        else:
            if clicked_piece is not None and clicked_piece != EMPTY_CELL:
                self.selected_pos = position
            else:
                piece_to_move = board.get_piece_at(self.selected_pos)
                from rules.rule_engine import validate_move
                result = validate_move(board, piece_to_move, position)
                
                if result == "ok":
                    board.remove_piece(self.selected_pos)
                    board.place_piece(piece_to_move, position)
                    self.selected_pos = None  # איפוס לאחר מהלך מוצלח
                else:
                    self.selected_pos = None 