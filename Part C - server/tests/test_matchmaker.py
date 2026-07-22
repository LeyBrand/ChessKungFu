import pytest

from tournament.matchmaker import Matchmaker


class FakeClock:
    def __init__(self, start=0.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def matchmaker(clock):
    return Matchmaker(clock=clock)


def test_seek_with_empty_pool_returns_none_and_waits(matchmaker):
    result = matchmaker.seek("p1", "alice", 1200)
    assert result is None
    assert matchmaker.is_waiting("p1")


def test_seek_matches_players_within_elo_range(matchmaker):
    matchmaker.seek("p1", "alice", 1200)
    result = matchmaker.seek("p2", "bob", 1250)
    assert result == "p1"
    assert not matchmaker.is_waiting("p1")
    assert not matchmaker.is_waiting("p2")


def test_seek_does_not_match_players_outside_elo_range(matchmaker):
    matchmaker.seek("p1", "alice", 1200)
    result = matchmaker.seek("p2", "bob", 1350)
    assert result is None
    assert matchmaker.is_waiting("p1")
    assert matchmaker.is_waiting("p2")


def test_cancel_removes_player_from_pool(matchmaker):
    matchmaker.seek("p1", "alice", 1200)
    matchmaker.cancel("p1")
    assert not matchmaker.is_waiting("p1")


def test_check_timeouts_removes_players_past_timeout(matchmaker, clock):
    matchmaker.seek("p1", "alice", 1200)
    clock.advance(61)
    timed_out = matchmaker.check_timeouts()
    assert timed_out == ["p1"]
    assert not matchmaker.is_waiting("p1")


def test_check_timeouts_keeps_players_within_timeout(matchmaker, clock):
    matchmaker.seek("p1", "alice", 1200)
    clock.advance(30)
    timed_out = matchmaker.check_timeouts()
    assert timed_out == []
    assert matchmaker.is_waiting("p1")

def test_seek_matches_earliest_waiting_player_first(matchmaker, clock):
    matchmaker.seek("p1", "alice", 1200)
    clock.advance(1)
    matchmaker.seek("p2", "carol", 1305)  # too far from p1 (diff=105) - won't auto-match p1

    result = matchmaker.seek("p3", "bob", 1205)  # eligible for both p1 (diff=5) and p2 (diff=100)

    assert result == "p1"