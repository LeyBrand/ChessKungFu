import inspect
import pytest

from tournament import serialization
from tournament.serialization import (
    snapshot_to_json,
    snapshot_from_json,
    move_request_from_json,
    move_request_to_json,
)


def test_module_never_imports_pickle():
    assert "pickle" not in serialization.__dict__
    assert not hasattr(serialization, "pickle")


def test_snapshot_roundtrip():
    snapshot = {"timestamp_ms": 4200, "selected_cell": [1, 3], "pieces": [], "is_game_over": False}
    raw = snapshot_to_json(snapshot)
    assert isinstance(raw, str)
    assert snapshot_from_json(raw) == snapshot


def test_move_request_from_json_valid():
    raw = move_request_to_json("room-1", "p1", 120, 340)
    parsed = move_request_from_json(raw)
    assert parsed["room_id"] == "room-1"
    assert parsed["x"] == 120
    assert parsed["y"] == 340


def test_move_request_from_json_missing_fields_raises():
    with pytest.raises(ValueError):
        move_request_from_json('{"room_id": "room-1"}')
