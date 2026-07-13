import pytest
from model.board import Board
from model.position import Position
from model.piece import Piece
from rules.rook_rule import RookRules

@pytest.fixture
def board():
    return Board(8, 8)

def test_sliding_moves_basic(board):
    rook = Piece(id=1, color="white", kind="rook", position=Position(3, 3))
    board.place_piece(rook, Position(3, 3))
    
    # תוקן: אין ארגומנטים ב-RookRules()
    rules = RookRules()
    moves = rules.legal_destinations(board, rook)
    
    assert len(moves) == 14
    assert Position(3, 0) in moves
    assert Position(0, 3) in moves

def test_sliding_moves_blocked_by_own_piece(board):
    rook = Piece(id=1, color="white", kind="rook", position=Position(3, 3))
    blocking_piece = Piece(id=2, color="white", kind="pawn", position=Position(3, 5))
    
    board.place_piece(rook, Position(3, 3))
    board.place_piece(blocking_piece, Position(3, 5))
    
    # תוקן: אין ארגומנטים ב-RookRules()
    rules = RookRules()
    moves = rules.legal_destinations(board, rook)
    
    assert Position(3, 5) not in moves
    assert Position(3, 6) not in moves

def test_sliding_moves_capture_enemy(board):
    rook = Piece(id=1, color="white", kind="rook", position=Position(3, 3))
    enemy_piece = Piece(id=2, color="black", kind="pawn", position=Position(3, 5))
    
    board.place_piece(rook, Position(3, 3))
    board.place_piece(enemy_piece, Position(3, 5))
    
    rules = RookRules() 
    moves = rules.legal_destinations(board, rook)

    assert Position(3, 5) in moves
    assert Position(3, 6) not in moves