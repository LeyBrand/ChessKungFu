from iteration_8.logic import is_valid_move as _is_valid_move, apply_arrived_moves as _apply_arrived_moves_8
from iteration_6.logic import add_pending_move, is_in_movement
from iteration_7.logic import is_dst_taken
from iteration_1.logic import print_board, WHITE

def _pawn_start_row(color, board_rows):
    return board_rows - 2 if color == WHITE else 1

def is_valid_move(piece, src, dst, board=None):
    if piece[1] != 'P':
        return _is_valid_move(piece, src, dst, board)
    sc, sr = src
    dc, dr = dst
    cd, rd = abs(dc - sc), dr - sr
    direction = -1 if piece[0] == WHITE else 1
    is_capture = board is not None and board[dr][dc] != '.'
    if is_capture:
        return cd == 1 and rd == direction
    if cd != 0:
        return False
    if rd == direction:
        return True
    if rd == 2 * direction:
        board_rows = len(board) if board is not None else 8
        if sr != _pawn_start_row(piece[0], board_rows):
            return False
        mid_row = sr + direction
        return board is None or board[mid_row][sc] == '.'
    return False

def apply_arrived_moves(board, pending_moves, game_time, game_over):
    arrived = [m for m in pending_moves if game_time >= m[3]]
    arrived.sort(key=lambda m: m[3])
    for move in arrived:
        piece, src, dst, _ = move
        dc, dr = dst
        dst_piece = board[dr][dc]
        if dst_piece != '.' and dst_piece[0] == piece[0]:
            pending_moves.remove(move)
            continue
        if not is_valid_move(piece, src, dst, board):
            pending_moves.remove(move)
            continue
        board[dr][dc] = piece
        board[src[1]][src[0]] = '.'
        pending_moves.remove(move)
        if dst_piece in ('wK', 'bK'):
            game_over[0] = True
        if piece[1] == 'P':
            last_row = 0 if piece[0] == WHITE else len(board) - 1
            if dr == last_row:
                board[dr][dc] = piece[0] + 'Q'

def processer():
    pending_moves = []
    game_over = [False]

    def click_handler(x, y, board, selected_pos, game_time):
        apply_arrived_moves(board, pending_moves, game_time, game_over)
        if game_over[0]:
            return selected_pos
        col, row = x // 100, y // 100
        if selected_pos is None:
            if board[row][col] != '.' and not is_in_movement((col, row), pending_moves):
                return (col, row)
        else:
            piece = board[selected_pos[1]][selected_pos[0]]
            dst = (col, row)
            if is_valid_move(piece, selected_pos, dst, board) and not is_dst_taken(dst, pending_moves):
                add_pending_move(piece, selected_pos, dst, game_time, pending_moves)
                return None
        return selected_pos

    def print_handler(board, game_time):
        apply_arrived_moves(board, pending_moves, game_time, game_over)
        print_board(board)

    from iteration_6.logic import processer as _processer6
    _processer6(click_handler=click_handler, print_handler=print_handler)

if __name__ == '__main__':
    processer()
