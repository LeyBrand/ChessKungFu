import pytest
from iteration_1.logic import board_piecec_parsing
from iteration_5.logic import is_valid_move, process_click

def test_white_pawn_forward():
    assert is_valid_move('wP', (0, 2), (0, 1)) is True

def test_white_pawn_backward():
    assert is_valid_move('wP', (0, 2), (0, 3)) is False

def test_black_pawn_forward():
    assert is_valid_move('bP', (0, 1), (0, 2)) is True

def test_black_pawn_backward():
    assert is_valid_move('bP', (0, 1), (0, 0)) is False

def test_white_pawn_capture():
    assert is_valid_move('wP', (1, 2), (2, 1)) is True

def test_pawn_two_cells():
    assert is_valid_move('wP', (0, 4), (0, 2)) is False

def test_pawn_capture_forward():
    assert is_valid_move('wP', (0, 2), (0, 1)) is True
    assert is_valid_move('wP', (1, 2), (1, 1)) is True  # לא לכידה — תנועה ישרה

def test_pawn_click():
    board = board_piecec_parsing(". . .\nwP . .\n. . .")
    sel = process_click(50, 150, board, None)
    sel = process_click(50, 50, board, sel)
    assert sel is None
    assert board[0][0] == 'wP'
