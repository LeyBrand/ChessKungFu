from constants import EMPTY_CELL, WHITE, BLACK
from model.position import position

def print_board(board):
    print(f"DEBUG: Printing board with {board.cols} columns")
    for r in range(board.rows):
        row_tokens = []
        for c in range(board.cols):
            piece = board.get_piece_at(position(r, c))
            if piece is None:
                row_tokens.append(EMPTY_CELL)
            else:
                color_char = WHITE if piece.color == 'white' else BLACK
                row_tokens.append(f"{color_char}{piece.kind}")
        
        print(" ".join(row_tokens))