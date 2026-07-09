import pytest
from io import StringIO
from iteration_3.logic import is_valid_move, process_click, processer
from iteration_1.logic import board_piecec_parsing

# --- is_valid_move ---

def test_king_legal():
    assert is_valid_move('wK', (0, 0), (1, 1)) is True

def test_king_illegal():
    assert is_valid_move('wK', (0, 0), (2, 0)) is False

def test_rook_legal():
    assert is_valid_move('wR', (0, 0), (0, 4)) is True

def test_rook_illegal():
    assert is_valid_move('wR', (0, 0), (2, 2)) is False

def test_bishop_legal():
    assert is_valid_move('wB', (0, 0), (3, 3)) is True

def test_bishop_illegal():
    assert is_valid_move('wB', (0, 0), (0, 3)) is False

def test_queen_legal_straight():
    assert is_valid_move('wQ', (0, 0), (0, 5)) is True

def test_queen_legal_diagonal():
    assert is_valid_move('wQ', (0, 0), (3, 3)) is True

def test_queen_illegal():
    assert is_valid_move('wQ', (0, 0), (1, 3)) is False

def test_knight_legal():
    assert is_valid_move('wN', (0, 0), (1, 2)) is True

def test_knight_illegal():
    assert is_valid_move('wN', (0, 0), (2, 2)) is False

# --- process_click עם validator ---

def test_illegal_move_ignored():
    board = board_piecec_parsing("wR . .\n. . .\n. . .")
    sel = process_click(50, 50, board, None)
    sel = process_click(150, 150, board, sel)  # אלכסון - לא חוקי לצריח
    assert sel == (0, 0)
    assert board[0][0] == 'wR'

def test_legal_move_executed():
    board = board_piecec_parsing("wR . .\n. . .\n. . .")
    sel = process_click(50, 50, board, None)
    sel = process_click(250, 50, board, sel)  # ישר - חוקי לצריח
    assert sel is None
    assert board[0][2] == 'wR'
    assert board[0][0] == '.'

# --- processer אינטגרציה ---

def test_processer_invalid_move(monkeypatch):
    input_str = "Board:\nwK . .\n. . .\n. . .\nCommands:\nclick 50 50\nclick 250 250\nprint board"
    monkeypatch.setattr('sys.stdin', StringIO(input_str))
    captured = StringIO()
    monkeypatch.setattr('sys.stdout', captured)
    processer(click_handler=process_click)
    output = captured.getvalue().strip()
    assert "wK . ." in output  # המלך לא זז
