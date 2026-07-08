from iteration_6.logic import processer as _processer, is_in_movement, add_pending_move, apply_arrived_moves, is_valid_move
from iteration_1.logic import print_board

def is_dst_taken(dst, pending_moves):
    dc, dr = dst
    return any(move[2][0] == dc or move[2][1] == dr for move in pending_moves)

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

    _processer(click_handler = click_handler, print_handler = print_handler)

if __name__ == "__main__":
    processer()