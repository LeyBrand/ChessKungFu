import sys

def print_board():
    input_data = sys.stdin.read()
    parsed_board = board_piecec_parsing(input_data)
    if not parsed_board[0]:
        print(parsed_board[1])
        return

    else:
        for row in parsed_board:
            print(row)
        return

def board_piecec_parsing(input_data):

    if not input_data:
        return
    
    try:
        board_part = input_data.split("Board:")[1].split("Commands:")[0].strip()
    except IndexError:
        return
    
    lines = [line.strip() for line in board_part.splitlines() if line.strip()]

    if not lines:
        return
    
    valid_pieces = {'.', 'wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'}

    parsed_board = []
    expected_cols = None

    for line in lines:
        tokens = line.split()
        if not tokens:
            continue

        for token in tokens:
            if token not in valid_pieces:
                return [False, "ERROR UNKNOWN_TOKEN"]
            
            if expected_cols is None:
                expected_cols = len(tokens)
            elif len(tokens) != expected_cols:
                return [False, "ERROR ROW_WIDTH_MISMATCH"] 
            
        parsed_board.append(tokens)
    
    return [True, parsed_board]

if __name__ == "__main__":
    print_board()
