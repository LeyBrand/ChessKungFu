import sys
from io import StringIO
from iteration_9.logic import processer

def run(input_str):
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = StringIO(input_str), StringIO()
    processer()
    output = sys.stdout.getvalue()
    sys.stdin, sys.stdout = old_in, old_out
    return output.strip()

def test_capturing_king_ends_game():
    result = run("Board:\nwR . bK\nCommands:\nclick 50 50\nclick 250 50\nwait 2000\nprint board")
    assert result == ". . wR"

def test_moves_ignored_after_game_over():
    result = run("Board:\nwR . bK\nCommands:\nclick 50 50\nclick 250 50\nwait 2000\nclick 250 50\nclick 50 50\nwait 2000\nprint board")
    assert result == ". . wR"
