from constants import EMPTY_CELL, VALID_PIECES, WHITE
from model.board import Board
from model.piece import Piece
from model.position import Position

def parse_board(board_text):
    lines = [line.split() for line in board_text.strip().splitlines() if line.strip()]
    if not lines:
        return None
        
    expected_cols = len(lines[0])
    rows = len(lines)
    board = Board(rows, expected_cols)
    
    for r, line in enumerate(lines):
        if len(line) != expected_cols:
            print("ERROR ROW_WIDTH_MISMATCH")
            return None
            
        for c, token in enumerate(line):
            if token not in VALID_PIECES:
                print("ERROR UNKNOWN_TOKEN")
                return None
            
            if token != EMPTY_CELL:
                color = "white" if token.startswith(WHITE) else "black"
                kind = token[1:]
                piece = Piece(id=f"{token}_{c}_{r}", color=color, kind=kind, position=Position(c, r))
                board.add_piece(piece, Position(c, r))
                
    return board