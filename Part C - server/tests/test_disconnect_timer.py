import pytest

from tournament.disconnect_timer import DisconnectTimer


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
def timer(clock):
    return DisconnectTimer(clock=clock)


def test_start_makes_it_pending(timer):
    timer.start("room1", "white")
    assert timer.is_pending("room1", "white")


def test_cancel_removes_pending(timer):
    timer.start("room1", "white")
    timer.cancel("room1", "white")
    assert not timer.is_pending("room1", "white")


def test_check_expired_returns_nothing_before_timeout(timer, clock):
    timer.start("room1", "white")
    clock.advance(19)
    assert timer.check_expired() == []
    assert timer.is_pending("room1", "white")


def test_check_expired_returns_and_clears_after_timeout(timer, clock):
    timer.start("room1", "white")
    clock.advance(20)
    expired = timer.check_expired()
    assert expired == [("room1", "white")]
    assert not timer.is_pending("room1", "white")


def test_seconds_remaining_counts_down(timer, clock):
    timer.start("room1", "white")
    clock.advance(5)
    assert timer.seconds_remaining("room1", "white") == 15


def test_seconds_remaining_none_when_not_pending(timer):
    assert timer.seconds_remaining("room1", "white") is None


def test_two_rooms_tracked_independently(timer, clock):
    timer.start("room1", "white")
    clock.advance(10)
    timer.start("room2", "black")
    clock.advance(11)  # room1 now at 21s (expired), room2 at 11s (not yet)

    expired = timer.check_expired()
    assert expired == [("room1", "white")]
    assert timer.is_pending("room2", "black")