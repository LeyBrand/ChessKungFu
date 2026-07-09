import sys
from io import StringIO
from iteration_8.logic import processer

def run(input_str):
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = StringIO(input_str), StringIO()
    processer()
    output = sys.stdout.getvalue()
    sys.stdin, sys.stdout = old_in, old_out
    return output.strip()

def test_enemy_collision_white_started_first():
    result = run("Board:\nwR . . bR\nCommands:\nclick 50 50\nclick 350 50\nclick 350 50\nclick 50 50\nwait 3000\nprint board")
    assert result == ". . . wR"

def test_enemy_collision_black_started_first():
    result = run("Board:\nwR . . bR\nCommands:\nclick 350 50\nclick 50 50\nclick 50 50\nclick 350 50\nwait 3000\nprint board")
    assert result == "bR . . ."

def test_cannot_start_move_through_friendly_piece():
    result = run("Board:\n. . .\nwR wP .\n. . .\nCommands:\nclick 50 150\nclick 250 150\nwait 2000\nprint board")
    assert result == ". . .\nwR wP .\n. . ."

def test_dynamic_block_tactic_not_in_common_route():
    result = run("Board:\n. . . .\nwQ . . bK\n. . bP .\n. . . .\nCommands:\nclick 50 150\nclick 350 150\nwait 200\nclick 250 250\nclick 250 150\nwait 3000\nprint board")
    assert result == ". . . .\n. . . wQ\n. . bP .\n. . . ."

def test_knight_cannot_land_on_friendly_piece():
    result = run("Board:\n. wP .\n. . .\nwN . .\nCommands:\nclick 50 250\nclick 150 50\nwait 1000\nprint board")
    assert result == ". wP .\n. . .\nwN . ."

def test_premove_does_not_execute_in_common_route():
    result = run("Board:\nwR . .\nCommands:\nclick 50 50\nclick 150 50\nclick 50 50\nclick 250 50\nwait 2000\nprint board")
    assert result == ". wR ."
