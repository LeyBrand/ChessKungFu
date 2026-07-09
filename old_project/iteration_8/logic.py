from iteration_6.logic import processer as _processer, add_pending_move, is_in_movement
from iteration_7.logic import is_dst_taken
from iteration_4.logic import is_valid_move as _is_valid_move_4
from iteration_5.logic import is_valid_move as _is_valid_move_5
from iteration_1.logic import print_board

def is_valid_move(piece, src, dst, board=None):
    if piece[1] == 'P':
        return _is_valid_move_5(piece, src, dst, board)
    return _is_valid_move_4(piece, src, dst, board)

def apply_arrived_moves(board, pending_moves, game_time):
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

def processer():
    pending_moves = []

    def click_handler(x, y, board, selected_pos, game_time):
        apply_arrived_moves(board, pending_moves, game_time)
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
        apply_arrived_moves(board, pending_moves, game_time)
        print_board(board)

    _processer(click_handler=click_handler, print_handler=print_handler)

if __name__ == '__main__':
    processer()
