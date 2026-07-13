import pytest
from unittest.mock import MagicMock
from model.position import Position
from model.piece import Piece, PieceState
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion

@pytest.fixture
def board():
    return MagicMock()

@pytest.fixture
def arbiter(board):
    return RealTimeArbiter(board)

def test_advance_time_completes_motion(arbiter, board):
    piece = Piece(id=1, color="white", kind="R", position=Position(0, 0))
    # Motion מ-0,0 ל-0,5 שמתחיל בזמן 0 ונמשך 100ms
    motion = Motion(piece, Position(0, 0), Position(0, 5), start_time=0)
    motion.duration_ms = 100
    
    arbiter.add_motion(motion)
    
    # קידום זמן ל-150ms - המהלך אמור להסתיים
    king_captured = arbiter.advance_time(150)
    
    assert arbiter.now() == 150
    assert len(arbiter.get_active_motions()) == 0
    board.move_piece.assert_called_with(Position(0, 0), Position(0, 5))
    assert piece.state == PieceState.IDLE
    assert king_captured is False

def test_collision_resolution(arbiter, board):
    # יצירת שני כלים שמתחרים על אותה משבצת בו-זמנית
    piece1 = Piece(id=1, color="white", kind="R", position=Position(0, 0))
    piece2 = Piece(id=2, color="black", kind="R", position=Position(1, 1))
    
    m1 = Motion(piece1, Position(0, 0), Position(2, 2), start_time=0)
    m1.duration_ms = 50
    m2 = Motion(piece2, Position(1, 1), Position(2, 2), start_time=10) # m1 הופעל קודם
    m2.duration_ms = 40
    
    arbiter.add_motion(m1)
    arbiter.add_motion(m2)
    
    # קידום זמן ל-100ms (שניהם מסתיימים)
    arbiter.advance_time(100)
    
    # m1 (שהתחיל מוקדם יותר) צריך לנצח, m2 צריך להיות CAPTURED
    assert piece1.state == PieceState.IDLE
    assert piece2.state == PieceState.CAPTURED
    assert len(arbiter.get_active_motions()) == 0