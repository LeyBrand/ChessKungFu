import sys
from iteration_2.logic import processer, process_click as _process_click

PIECE_RULES = {
    'K': lambda cd, rd: cd <= 1 and rd <= 1,
    'R': lambda cd, rd: cd == 0 or rd == 0,
    'B': lambda cd, rd: cd == rd,
    'Q': lambda cd, rd: cd == 0 or rd == 0 or cd == rd,
    'N': lambda cd, rd: (cd == 2 and rd == 1) or (cd == 1 and rd == 2)
}

def is_valid_move(piece, src, dst, board = None):
    sc, sr = src
    dc, dr = dst
    col_diff = abs(dc - sc)
    row_diff = abs(dr - sr)

    rule = PIECE_RULES.get(piece[1])
    
    return rule(col_diff, row_diff) if rule else True

def process_click(x, y, board, selected_pos, validator = None):
    return _process_click(x, y, board, selected_pos, validator = validator or is_valid_move)


if __name__ == "__main__":
    processer(click_handler = process_click)
    