from constants import VALID_PIECES
import sys

def parse(board_text):
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
