from final.board import CELL_SIZE
from final.rules import is_valid_move

class ChessGame:
    def __init__(self, board, piece_rules = None):
        self.board = board
        self.selected_pos = None
        self.game_time = 0
        self._validator = piece_rules or is_valid_move

        def click(self, x, y):
            col = x // CELL_SIZE
            row = y // CELL_SIZE

            if not (0 <= row < len(self.board) and 0 <= col < len(self.board[row])):
                return 
            
            if self.selected_pos is None:
                if self.board[row][col] != '.':
                    self.selected_pos = (col, row)
            else:
                src = self.seleced_pos
                piece = self.board[src[1]][src[0]]
                if self._validator(piece, src, (col, row), self.board):
                    self.board[row][col] = piece
                    self.board[src[1]][src[0]] = '.'
                    self.selected_pos = None