from constants import EMPTY_CELL, WHITE, BLACK
from model.position import Position

def print_board(board):
    for r in range(board.rows):
        row_tokens = []
        for c in range(board.cols):
            piece = board.get_piece_at(Position(c, r))
            if piece is None:
                row_tokens.append(EMPTY_CELL)
            else:
                color_char = WHITE if piece.color == 'white' else BLACK
                row_tokens.append(f"{color_char}{piece.kind}")
        
        print(" ".join(row_tokens))