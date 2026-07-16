import pytest
from model.board import Board
from model.position import Position  # עדכני את הנתיב בהתאם

# Mock מחלקה פשוטה לייצוג כלי (כדי שאפשר יהיה להוסיף ללוח)
class MockPiece:
    def __init__(self):
        self.position = None

@pytest.fixture
def board():
    return Board(rows=8, cols=8)

def test_position_equality():
    assert Position(1, 2) == Position(1, 2)
    assert Position(1, 2) != Position(2, 1)

def test_in_bounds(board):
    assert board.in_bounds(Position(0, 0)) is True
    assert board.in_bounds(Position(7, 7)) is True
    assert board.in_bounds(Position(-1, 0)) is False
    assert board.in_bounds(Position(8, 0)) is False

def test_add_and_get_piece(board):
    piece = MockPiece()
    pos = Position(2, 3)
    board.add_piece(piece, pos)
    
    assert board.get_piece_at(pos) == piece
    assert piece.position == pos

def test_add_piece_collision(board):
    piece1 = MockPiece()
    piece2 = MockPiece()
    pos = Position(1, 1)
    
    board.add_piece(piece1, pos)
    with pytest.raises(ValueError, match="already occupied"):
        board.add_piece(piece2, pos)

def test_move_piece(board):
    piece = MockPiece()
    start_pos = Position(0, 0)
    end_pos = Position(1, 1)
    
    board.add_piece(piece, start_pos)
    board.move_piece(start_pos, end_pos)
    
    assert board.get_piece_at(start_pos) is None
    assert board.get_piece_at(end_pos) == piece
    assert piece.position == end_pos

def test_remove_piece(board):
    piece = MockPiece()
    pos = Position(5, 5)
    board.add_piece(piece, pos)
    board.remove_piece(pos)
    
    assert board.get_piece_at(pos) is None