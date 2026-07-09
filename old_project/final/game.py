from final.board import CELL_SIZE, print_board as _print_board
from final.rules import is_valid_move, is_in_movement, is_dst_taken, add_pending_move, apply_arrived_moves

class ChessGame:
    def __init__(self, board, piece_rules = None):
        self.board = board
        self.selected_pos = None
        self.game_time = 0
        self._validator = piece_rules or is_valid_move
        self.pending_moves = []
        self.game_over = [False, None]

    def click(self, x, y):

        col = x // CELL_SIZE
        row = y // CELL_SIZE

        if not (0 <= row < len(self.board) and 0 <= col < len(self.board[row])):
            return 
            
        apply_arrived_moves(self.board, self.pending_moves, self.game_time, self.game_over)
        if self.game_over[0]:
            return
        
        
        if self.selected_pos is None:
            if self.board[row][col] != '.' and not is_in_movement((col, row), self.pending_moves):
                self.selected_pos = (col, row)
        else:
            src = self.selected_pos
            dst = (col, row)
            piece = self.board[src[1]][src[0]]
            if self._validator(piece, src, dst, self.board) and not is_dst_taken(dst, self.pending_moves):
                add_pending_move(piece, src, dst, self.game_time, self.pending_moves)
                self.selected_pos = None
            else:
                self.selected_pos = (col, row) if self.board[row][col] != '.' and not is_in_movement((col, row), self.pending_moves) else None
    def print_board(self):
        apply_arrived_moves(self.board, self.pending_moves, self.game_time, self.game_over)
        _print_board(self.board)