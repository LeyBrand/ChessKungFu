import pytest
import unittest.mock
from unittest.mock import MagicMock
from model.position import Position
from model.piece import Piece
from engine.game_engine import GameEngine

@pytest.fixture
def mock_state():
    state = MagicMock()
    state.game_over = False
    state.board = MagicMock()
    return state

@pytest.fixture
def engine(mock_state):
    return GameEngine(mock_state)

def test_request_move_game_over(engine, mock_state):
    mock_state.game_over = True
    result = engine.request_move(Position(0,0), Position(0,1))
    assert result.is_accepted is False
    assert result.reason == "game_over"

def test_request_move_empty_source(engine, mock_state):
    # כאשר אין כלי בלוח
    mock_state.board.get_piece_at.return_value = None
    result = engine.request_move(Position(0,0), Position(0,1))
    assert result.is_accepted is False
    assert result.reason == "empty_source"

def test_request_move_success(engine, mock_state):
    piece = Piece(id=1, color="white", kind="R", position=Position(0,0))
    mock_state.board.get_piece_at.return_value = piece
    with unittest.mock.patch('rules.rule_engine.validate_move', return_value="ok"):
        result = engine.request_move(Position(0,0), Position(0,5))
        assert result.is_accepted is True
        assert result.reason == "ok"

def test_resolve_airborne_landing(engine, mock_state):
    piece = Piece(id=1, color="white", kind="R", position=Position(0, 0))
    engine.airborne = [{
        "piece": piece,
        "origin": Position(0, 0),
        "land_time": 50 
    }]
    
    engine.wait(100)
    
    mock_state.board.place_piece.assert_called_with(piece, Position(0, 0))
    assert len(engine.airborne) == 0