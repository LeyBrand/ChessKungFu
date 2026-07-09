import sys

VALID_PIECES = {'.', 'wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'}

WHITE = 'w'
BLACK = 'b'

def processer():
    input_data = sys.stdin.read()
    print(input_data)


def board_piece_parsing(board_text):

    lines = [line.split() for line in board_text.strip().splitlines()]
    if not lines:
        return None

    expected_cols = len(lines[0])

    for line in lines:
        if len(line) != expected_cols:
            print("ERROR ROW_WIDTH_MISMATCH")
            sys.exit()
        for token in line:
            if token not in VALID_PIECES:
                print("ERROR UNKNOWN_TOKEN")
                sys.exit()
    return lines

board_piecec_parsing = board_piece_parsing

def print_board(board):
    for row in board:
        print(" ".join(row))

if __name__ == "__main__":
    input_data = sys.stdin.read()
    b_idx = input_data.find("Board:")
    c_idx = input_data.find("Commands:")
    

    board_part = input_data[b_idx + len("Board:"):c_idx].strip()
    

    parsed_board = board_piecec_parsing(board_part)
    if parsed_board:
        print_board(parsed_board)