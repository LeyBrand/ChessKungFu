from iteration_3.logic import is_valid_move as _is_valid_move, process_click as _process_click, processer

def is_valid_move(piece, src, dst, board=None):
    if piece[1] == 'P':
        sc, sr = src
        dc, dr = dst
        col_diff = abs(dc - sc)
        direction = -1 if piece[0] == 'w' else 1
        if col_diff == 0:
            if board is not None and board[dr][dc] != '.':
                return False
            return dr - sr == direction
        return col_diff == 1 and dr - sr == direction
    return _is_valid_move(piece, src, dst, board)

def process_click(x, y, board, selected_pos):
    return _process_click(x, y, board, selected_pos,
                          validator=lambda piece, src, dst: is_valid_move(piece, src, dst, board))

if __name__ == '__main__':
    processer(click_handler = process_click)
