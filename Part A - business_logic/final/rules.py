from final.board import WHITE

PIECE_RULES = {
    'K': lambda cd, rd: cd <= 1 and rd <= 1,
    'R': lambda cd, rd: cd == 0 or rd == 0,
    'B': lambda cd, rd: cd == rd,
    'Q': lambda cd, rd: cd == 0 or rd == 0 or cd == rd,
    'N': lambda cd, rd: (cd == 2 and rd == 1) or (cd == 1 and rd == 2),
    'P': lambda cd, rd, direction, is_capture: (
        cd == 1 and rd == direction
    ) if is_capture else (
        cd == 0 and rd == direction
    ),
}

SLIDING_PIECES = {'Q', 'R', 'B'}

def get_piece_type(piece):
    return piece[1]

def get_piece_color(piece):
    return piece[0]

def is_same_color(piece1, piece2):
    return get_piece_color(piece1) == get_piece_color(piece2)

def get_pawn_direction(piece):
    return -1 if get_piece_color(piece) == WHITE else 1

def is_path_clear(src, dst, board):
    sc, sr = src
    dc, dr = dst
    col_step = 0 if dc == sc else (1 if dc > sc else -1)
    row_step = 0 if dr == sr else (1 if dr > sr else -1)
    col, row = sc + col_step, sr + row_step
    while (col, row) != (dc, dr):
        if board[row][col] != '.':
            return False
        col += col_step
        row += row_step
    return True

def is_valid_move(piece, src, dst, board = None):
    piece_type = get_piece_type(piece)
    sc, sr = src
    dc, dr = dst
    col_diff = abs(dc - sc)
    row_diff = abs(dr - sr)
    direction = get_pawn_direction(piece) if piece_type == 'P' else 0
    is_capture = board is not None and board[dr][dc] != '.'
    rule = PIECE_RULES.get(piece_type)
    if piece_type == 'P':
        return rule(col_diff, row_diff, direction, is_capture)
    if piece_type in SLIDING_PIECES:
        if not rule(col_diff, row_diff):
            return False
        return is_path_clear(src, dst, board)
    return rule(col_diff, row_diff)

def is_in_movement(src, pending_moves):
    return any(src == move[1] for move in pending_moves)

def add_pending_move(piece, src, dst, game_time, pending_moves):
    pending_moves.append((piece, src, dst, game_time + 1000 * (abs(dst[0] - src[0]) + abs(dst[1] - src[1]))))

def apply_arrived_moves(board, pending_moves, game_time):
    for move in pending_moves[:]:
        piece, src, dst, arrival = move
        if game_time >= arrival:
            board[dst[1]][dst[0]] = piece
            board[src[1]][src[0]] = '.'
            pending_moves.remove(move)

