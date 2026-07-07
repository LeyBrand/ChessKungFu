import sys
from iteration_2.logic import processer, process_click as _process_click

def is_valid_move(piece, src, dst):
    sc, sr = src
    dc, dr = dst
    col_diff = abs(dc - sc)
    row_diff = abs(dr - sr)

    p = piece[1]
    if p == 'K':
        return col_diff <= 1 and row_diff <= 1
    if p == 'R':
        return col_diff == 0 or row_diff == 0
    if p == 'B':
        return col_diff == row_diff
    if p == 'Q':
        return col_diff == 0 or row_diff == 0 or col_diff == row_diff
    if p == 'N':
        return (col_diff == 2 and row_diff == 1) or (col_diff == 1 and row_diff == 2)
    return True

def process_click(x, y, board, selected_pos):
    return _process_click(x, y, board, selected_pos, validator = is_valid_move)


if __name__ == "__main__":
    processer(click_handler = process_click)
    