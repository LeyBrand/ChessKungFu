import sys

WHITE = 'w'
BLACK = 'b'

VALID_PIECES = {
    '.', 
    'wK', 'wQ', 'wR', 'wB', 'wN', 'wP',
    'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'
}

CELL_SIZE = 100

class board:
    def __init__(self, board_text):
        self.board = self.board_parsing(board_text)

    def board_parsing(self, board_text):
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
    
    def print_board(self):
        for row in self.board:
            print(" ".join(row))
