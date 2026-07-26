import json
import pytest

from network.protocol import parse_incoming, SnapshotMessage, ErrorMessage


def test_parse_incoming_valid_move():
    raw = json.dumps({"type": "MOVE", "room_id": "r1", "x": 10, "y": 20})
    data = parse_incoming(raw)
    assert data["type"] == "MOVE"


def test_parse_incoming_missing_type_raises():
    with pytest.raises(ValueError):
        parse_incoming(json.dumps({"room_id": "r1"}))


def test_parse_incoming_unknown_type_raises():
    with pytest.raises(ValueError):
        parse_incoming(json.dumps({"type": "TELEPORT"}))


def test_make_snapshot_message_shape():
    msg = json.loads(SnapshotMessage(data={"foo": "bar"}).to_json())
    assert msg == {"type": "SNAPSHOT", "data": {"foo": "bar"}}


def test_make_error_message_shape():
    msg = json.loads(ErrorMessage(reason="boom").to_json())
    assert msg == {"type": "ERROR", "reason": "boom"}