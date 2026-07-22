import pytest
from model.board import Board
from model.position import Position
from model.piece import Piece
from rules import rule_engine # הנחה שהקובץ נקרא rule_engine.py

@pytest.fixture
def board():
    return Board(8, 8)

def test_validate_move_outside_bounds(board):
    piece = Piece(id=1, color="white", kind="R", position=Position(0, 0))
    board.place_piece(piece, Position(0, 0))
    result = rule_engine.validate_move(board, Position(0, 0), Position(10, 10))
    assert result.is_valid is False
    assert result.reason == "outside_board"

def test_validate_move_illegal_piece_move(board):
    # צריח ב-(0,0) לא יכול לזוז ל-(1,1)
    piece = Piece(id=1, color="white", kind="R", position=Position(0, 0))
    board.place_piece(piece, Position(0, 0))
    result = rule_engine.validate_move(board, piece.position, Position(1, 1))
    assert result.is_valid is False
    assert result.reason == "illegal_piece_move"

def test_validate_move_friendly_destination(board):
    piece = Piece(id=1, color="white", kind="R", position=Position(0, 0))
    friend = Piece(id=2, color="white", kind="P", position=Position(0, 1))
    board.place_piece(piece, Position(0, 0))
    board.place_piece(friend, Position(0, 1))

def test_validate_move_ok(board):
    piece = Piece(id=1, color="white", kind="R", position=Position(0, 0))
    board.place_piece(piece, Position(0, 0))
    result = rule_engine.validate_move(board, piece.position, Position(0, 5))
    assert result.is_valid is True
    assert result.reason == "ok"