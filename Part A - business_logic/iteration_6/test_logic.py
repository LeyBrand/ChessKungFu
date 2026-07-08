import pytest
from io import StringIO
from iteration_6.logic import processer

def test_one_cell_move_before_arrival_board_unchanged(monkeypatch):
    input_str = "Board:\nwR . .\nCommands:\nclick 50 50\nclick 150 50\nwait 500\nprint board"
    monkeypatch.setattr('sys.stdin', StringIO(input_str))
    captured = StringIO()
    monkeypatch.setattr('sys.stdout', captured)
    processer()
    assert captured.getvalue().strip() == "wR . ."

def test_two_cell_move_before_and_after_arrival(monkeypatch):
    input_str = "Board:\nwR . .\nCommands:\nclick 50 50\nclick 250 50\nwait 1000\nprint board\nwait 1000\nprint board"
    monkeypatch.setattr('sys.stdin', StringIO(input_str))
    captured = StringIO()
    monkeypatch.setattr('sys.stdout', captured)
    processer()
    lines = captured.getvalue().strip().splitlines()
    assert lines[0] == "wR . ."
    assert lines[1] == ". . wR"

def test_moving_piece_ignores_redirect(monkeypatch):
    input_str = "Board:\nwR . .\nCommands:\nclick 50 50\nclick 250 50\nwait 1000\nclick 50 50\nclick 150 50\nwait 1000\nprint board"
    monkeypatch.setattr('sys.stdin', StringIO(input_str))
    captured = StringIO()
    monkeypatch.setattr('sys.stdout', captured)
    processer()
    assert captured.getvalue().strip() == ". . wR"
