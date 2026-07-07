import sys
from iteration_1.logic import print_board, board_piecec_parsing

def process_click(x, y, board, selected_pos):
    col = x // 100
    row = y // 100

    if 0 <= row < len(board) and 0 <= col < len(board[0]):
        if selected_pos is None:
            if board[row][col] != '.':
                return (col, row)
        else:
            if board[row][col] != ".":
                return (col, row)
            
            else:
                src_col, src_row = selected_pos
                piece = board[src_row][src_col]

                board[row][col] = piece
                board[src_row][src_col] = '.'
                return None
    return selected_pos

def processer():
    
    input_data = sys.stdin.read()

    b_idx = input_data.find("Board:")
    c_idx = input_data.find("Commands:")
    parsed_board = board_piecec_parsing(input_data[b_idx + len("Board:") : c_idx].strip())

    selected_pos = None
    game_time = 0
    command_text = input_data[c_idx:].replace("Commands:", "").strip()

    for line in command_text.splitlines():
        parts = line.split()
        if not parts:
            continue

        cmd = parts[0]

        if cmd == "click":
            x, y = int(parts[1]), int(parts[2])
            selected_pos = process_click(x, y, parsed_board, selected_pos)

        elif cmd == "wait":
            ms = int(parts[1])
            game_time += ms

        elif cmd == "print" and parts[1] == "board":
            print_board(parsed_board)


if __name__ == "__main__":
    processer()