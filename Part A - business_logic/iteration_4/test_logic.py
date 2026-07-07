import pytest
from iteration_1.logic import board_piecec_parsing
from iteration_4.logic import is_valid_move, is_path_clear, process_click

def test_rook_blocked():
    board = board_piecec_parsing(". wP . .\n. . . .\n. . . .\n. . . .")
    assert is_path_clear('wR', (0, 0), (3, 0), board) is False

def test_rook_not_blocked():
    board = board_piecec_parsing(". . . .\n. . . .\n. . . .\n. . . .")
    assert is_path_clear('wR', (0, 0), (3, 0), board) is True

def test_bishop_blocked():
    board = board_piecec_parsing(". . . .\n. wP . .\n. . . .\n. . . .")
    assert is_path_clear('wB', (0, 0), (3, 3), board) is False

def test_knight_jumps_over():
    board = board_piecec_parsing("wN wP wP\nwP wP wP\n. . .\n. . .")
    assert is_valid_move('wN', (0, 0), (1, 2), board) is True

def test_cannot_capture_own_piece():
    board = board_piecec_parsing("wR . wP\n. . .\n. . .")
    assert is_valid_move('wR', (0, 0), (2, 0), board) is False

def test_can_capture_enemy_piece():
    board = board_piecec_parsing("wR . bP\n. . .\n. . .")
    assert is_valid_move('wR', (0, 0), (2, 0), board) is True

def test_rook_blocked_click():
    board = board_piecec_parsing("wR wP .\n. . .\n. . .")
    sel = process_click(50, 50, board, None)
    sel = process_click(250, 50, board, sel)
    assert sel == (0, 0)
    assert board[0][0] == 'wR'

def test_capture_enemy_click():
    board = board_piecec_parsing("wR . bP\n. . .\n. . .")
    sel = process_click(50, 50, board, None)
    sel = process_click(250, 50, board, sel)
    assert sel is None
    assert board[0][2] == 'wR'
