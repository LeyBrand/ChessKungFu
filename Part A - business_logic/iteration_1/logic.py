import sys

def board_piecec_parsing():
    
    input_data = sys.stdin.read()

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
                print("ERROR UNKNOWN_TOKEN")
                return
            
            if expected_cols is None:
                expected_cols = len(tokens)
            elif len(tokens) != expected_cols:
                print("ERROR ROW_WIDTH_MISMATCH")
                return
            
        parsed_board.append(" ".join(tokens))

    for row in parsed_board:
        print(row)

if __name__ == "__main__":
    board_piecec_parsing()
