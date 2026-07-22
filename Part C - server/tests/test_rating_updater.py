import pytest

from events.event_bus import EventBus
from network.rating_updater import subscribe_rating_update
from constants import Color


class FakeConnectionManager:
    def __init__(self, usernames):
        self._usernames = usernames  # player_id -> username

    def get_username(self, player_id):
        return self._usernames.get(player_id)


class FakePlayerStore:
    def __init__(self, ratings):
        self._ratings = dict(ratings)
        self.updates = []

    def get_rating(self, username):
        return self._ratings[username]

    def update_rating(self, username, new_rating):
        self.updates.append((username, new_rating))
        self._ratings[username] = new_rating


def test_game_over_with_winner_updates_both_ratings():
    bus = EventBus()
    player_ids = {Color.WHITE: "p1", Color.BLACK: "p2"}
    cm = FakeConnectionManager({"p1": "alice", "p2": "bob"})
    store = FakePlayerStore({"alice": 1200, "bob": 1200})

    subscribe_rating_update(bus, lambda: player_ids, cm, store)
    bus.publish("GAME_OVER", winner=Color.WHITE)

    assert store.updates == [("alice", 1216), ("bob", 1184)]


def test_game_over_without_winner_does_nothing():
    bus = EventBus()
    cm = FakeConnectionManager({})
    store = FakePlayerStore({})

    subscribe_rating_update(bus, lambda: {}, cm, store)
    bus.publish("GAME_OVER")  # no winner kwarg at all

    assert store.updates == []


def test_game_over_with_unseated_color_does_nothing():
    bus = EventBus()
    player_ids = {Color.WHITE: "p1"}  # black never got seated
    cm = FakeConnectionManager({"p1": "alice"})
    store = FakePlayerStore({"alice": 1200})

    subscribe_rating_update(bus, lambda: player_ids, cm, store)
    bus.publish("GAME_OVER", winner=Color.WHITE)

    assert store.updates == []