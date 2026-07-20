import pytest

from player_registry import PlayerRegistry, ServerFullError


def test_first_player_gets_white_second_gets_black():
    registry = PlayerRegistry()
    ws1, ws2 = object(), object()

    color1 = registry.register(ws1, "alice")
    color2 = registry.register(ws2, "bob")

    assert color1 == "white"
    assert color2 == "black"


def test_registry_reports_full_after_two_players():
    registry = PlayerRegistry()
    registry.register(object(), "alice")

    assert registry.is_full() is False

    registry.register(object(), "bob")

    assert registry.is_full() is True


def test_registering_a_third_player_raises():
    registry = PlayerRegistry()
    registry.register(object(), "alice")
    registry.register(object(), "bob")

    with pytest.raises(ServerFullError):
        registry.register(object(), "carol")


def test_get_player_returns_stored_info():
    registry = PlayerRegistry()
    ws = object()
    registry.register(ws, "alice")

    assert registry.get_player(ws) == {"username": "alice", "color": "white"}


def test_get_player_returns_none_for_unknown_websocket():
    registry = PlayerRegistry()

    assert registry.get_player(object()) is None


def test_unregister_frees_the_departed_players_color():
    registry = PlayerRegistry()
    ws1 = object()
    registry.register(ws1, "alice")           # white
    registry.register(object(), "bob")        # black
    assert registry.is_full() is True

    registry.unregister(ws1)                  # white slot is now open
    assert registry.is_full() is False

    color = registry.register(object(), "carol")

    assert color == "white"