import sys
from io import StringIO
from iteration_1.logic import board_piecec_parsing
from iteration_10.logic import is_valid_move, apply_arrived_moves, processer


def run(input_str):
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = StringIO(input_str), StringIO()
    processer()
    output = sys.stdout.getvalue()
    sys.stdin, sys.stdout = old_in, old_out
    return output.strip()


# --- double move ---

def test_pawn_double_move_from_start():
    assert is_valid_move('wP', (0, 6), (0, 4)) is True

def test_pawn_double_move_not_from_start():
    assert is_valid_move('wP', (0, 5), (0, 3)) is False

def test_black_pawn_double_move_from_start():
    assert is_valid_move('bP', (0, 1), (0, 3)) is True

def test_pawn_double_move_blocked():
    board = board_piecec_parsing(
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        "bP . . . . . . .\n"
        "wP . . . . . . .\n"
        ". . . . . . . ."
    )
    assert is_valid_move('wP', (0, 6), (0, 4), board) is False

def test_pawn_double_move_path_clear():
    board = board_piecec_parsing(
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        ". . . . . . . .\n"
        "wP . . . . . . .\n"
        ". . . . . . . ."
    )
    assert is_valid_move('wP', (0, 6), (0, 4), board) is True


# --- promotion ---

def test_white_pawn_promotes_to_queen():
    board = board_piecec_parsing(". . .\n. wP .\n. . .")
    pending_moves = []
    game_over = [False]
    from iteration_6.logic import add_pending_move
    add_pending_move('wP', (1, 1), (1, 0), 0, pending_moves)
    apply_arrived_moves(board, pending_moves, 1000, game_over)
    assert board[0][1] == 'wQ'

def test_black_pawn_promotes_to_queen():
    board = board_piecec_parsing(". . .\n. bP .\n. . .")
    pending_moves = []
    game_over = [False]
    from iteration_6.logic import add_pending_move
    add_pending_move('bP', (1, 1), (1, 2), 0, pending_moves)
    apply_arrived_moves(board, pending_moves, 1000, game_over)
    assert board[2][1] == 'bQ'


# --- integration ---

def test_pawn_double_move_integration():
    result = run(
        "Board:\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n. . . . . . . .\n"
        ". . . . . . . .\n. . . . . . . .\nwP . . . . . . .\n. . . . . . . .\n"
        "Commands:\nclick 50 650\nclick 50 450\nwait 3000\nprint board"
    )
    lines = result.splitlines()
    assert lines[4] == "wP . . . . . . ."
    assert lines[6] == ". . . . . . . ."
    assert lines[7] == ". . . . . . . ."
