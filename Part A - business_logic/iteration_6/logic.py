from iteration_2.logic import processer as _processer
from iteration_1.logic import print_board
from iteration_5.logic import is_valid_move

def is_in_movement(src, pending_moves):
    return any(move[1] == src for move in pending_moves)

def add_pending_move(piece, src, dst, game_time, pending_moves):
    pending_moves.append((piece, src, dst, game_time + 1000 * (abs(dst[0]-src[0]) + abs(dst[1]-src[1]))))

def apply_arrived_moves(board, pending_moves, game_time):
    for move in pending_moves[:]:
        piece, src, dst, arrival = move
        if game_time >= arrival:
            board[dst[1]][dst[0]] = piece
            board[src[1]][src[0]] = '.'
            pending_moves.remove(move)

def processer():
    pending_moves = []

    def click_handler(x, y, board, selected_pos, game_time):
        col, row = x // 100, y // 100
        if selected_pos is None:
            if board[row][col] != '.' and not is_in_movement((col, row), pending_moves):
                return (col, row)
        else:
            piece = board[selected_pos[1]][selected_pos[0]]
            if is_valid_move(piece, selected_pos, (col, row), board):
                add_pending_move(piece, selected_pos, (col, row), game_time, pending_moves)
                return None
        return selected_pos

    def print_handler(board, game_time):
        apply_arrived_moves(board, pending_moves, game_time)
        print_board(board)

    _processer(click_handler=click_handler, print_handler=print_handler)

if __name__ == '__main__':
    processer()