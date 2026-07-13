import pytest
from model.board import Board
from model.position import Position
from model.piece import Piece
from rules.pawn_rule import PawnRules

@pytest.fixture
def board():
    return Board(8, 8)

def test_pawn_single_and_double_step(board):
    # רגלי לבן בשורה 6 (Start row)
    pawn = Piece(id=1, color="white", kind="P", position=Position(3, 6))
    board.place_piece(pawn, Position(3, 6))
    
    rules = PawnRules()
    moves = rules.legal_destinations(board, pawn)
    
    assert Position(3, 5) in moves # צעד יחיד
    assert Position(3, 4) in moves # צעד כפול
    assert len(moves) == 2

def test_pawn_blocked_double_step(board):
    pawn = Piece(id=1, color="white", kind="P", position=Position(3, 6))
    blocker = Piece(id=2, color="white", kind="P", position=Position(3, 5))
    board.place_piece(pawn, Position(3, 6))
    board.place_piece(blocker, Position(3, 5))
    
    rules = PawnRules()
    moves = rules.legal_destinations(board, pawn)
    
    assert len(moves) == 0 # לא יכול לזוז בכלל

def test_pawn_capture_diagonal(board):
    pawn = Piece(id=1, color="white", kind="P", position=Position(3, 3))
    enemy = Piece(id=2, color="black", kind="P", position=Position(4, 2))
    board.place_piece(pawn, Position(3, 3))
    board.place_piece(enemy, Position(4, 2))
    
    rules = PawnRules()
    moves = rules.legal_destinations(board, pawn)
    
    assert Position(4, 2) in moves
    assert Position(3, 2) in moves # גם צעד ישר אפשרי

def test_pawn_blocked_forward_capture_only(board):
    pawn = Piece(id=1, color="white", kind="P", position=Position(3, 3))
    blocker = Piece(id=2, color="white", kind="P", position=Position(3, 2))
    enemy = Piece(id=3, color="black", kind="P", position=Position(2, 2))
    
    board.place_piece(pawn, Position(3, 3))
    board.place_piece(blocker, Position(3, 2))
    board.place_piece(enemy, Position(2, 2))
    
    rules = PawnRules()
    moves = rules.legal_destinations(board, pawn)
    
    assert Position(3, 2) not in moves # חסום קדימה
    assert Position(2, 2) in moves     # אבל יכול לאכול באלכסון