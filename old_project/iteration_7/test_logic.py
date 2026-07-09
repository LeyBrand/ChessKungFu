import sys
from io import StringIO
from iteration_7.logic import processer

def run(input_str):
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = StringIO(input_str), StringIO()
    processer()
    output = sys.stdout.getvalue()
    sys.stdin, sys.stdout = old_in, old_out
    return output.strip()

def test_no_cooldown_after_arrival():
    result = run("Board:\nwR . .\nCommands:\nclick 50 50\nclick 150 50\nwait 1000\nclick 150 50\nclick 250 50\nwait 1000\nprint board")
    assert result == ". . wR"

def test_opposite_colors_do_not_move_concurrently_in_common_route():
    result = run("Board:\nwR . .\n. . .\nbR . .\nCommands:\nclick 50 50\nclick 250 50\nclick 50 250\nclick 250 250\nwait 2000\nprint board")
    assert result == ". . wR\n. . .\nbR . ."

def test_piece_cannot_be_redirected_while_moving():
    result = run("Board:\nwR . .\nCommands:\nclick 50 50\nclick 250 50\nwait 1000\nclick 50 50\nclick 150 50\nwait 1000\nprint board")
    assert result == ". . wR"

def test_piece_ready_after_arrival():
    lines = run("Board:\nwR . .\nCommands:\nclick 50 50\nclick 150 50\nwait 1000\nprint board\nclick 150 50\nclick 250 50\nwait 1000\nprint board").splitlines()
    assert lines[0] == ". wR ."
    assert lines[1] == ". . wR"
