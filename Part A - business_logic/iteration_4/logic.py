import sys
from iteration_3.logic import is_valid_move as _is_valid_move, process_click as _process_click, processer

def is_path_clear(piece, src, dst, board):
    sc, sr = src
    dc, dr = dst
    col_step = 0 if dc == sc else (1 if dc > sc else -1)
    row_step = 0 if dr == sr else (1 if dr > sr else -1)
    c, r = sc + col_step, sr + row_step
    while (c, r) != (dc, dr):
        if board[r][c] != '.':
            return False
        c += col_step
        r += row_step
    return True

def is_valid_move(piece, src, dst, board = None):
    if not _is_valid_move(piece, src, dst):
        return False
    if board is not None:
        dc, dr = dst
        if board[dr][dc] != '.' and board[dr][dc][0] == piece[0]:
            return False
        if piece[1] in ('R', 'B', 'Q'):
            return is_path_clear(piece, src, dst, board)
    return True

def process_click(x, y, board, selected_pos):
    return _process_click(x, y, board, selected_pos,
                           validator = lambda piece, src, dst:
                            is_valid_move(piece, src, dst, board))

if __name__ == "__main__":
    processer(click_handler = process_click)
