import pytest

from data.player_store import PlayerStore, UsernameTakenError, InvalidCredentialsError, STARTING_RATING


@pytest.fixture
def store():
    # ":memory:" gives each test a fresh, isolated, in-RAM database - no
    # leftover state between tests, no real file touched on disk.
    s = PlayerStore(db_path=":memory:")
    yield s
    s.close()


def test_create_player_starts_at_default_rating(store):
    store.create_player("alice", "hunter2")

    assert store.get_rating("alice") == STARTING_RATING == 1200


def test_verify_password_succeeds_with_correct_password(store):
    store.create_player("alice", "hunter2")

    store.verify_password("alice", "hunter2")  # should not raise


def test_verify_password_raises_for_wrong_password(store):
    store.create_player("alice", "hunter2")

    with pytest.raises(InvalidCredentialsError):
        store.verify_password("alice", "wrong-password")


def test_verify_password_raises_for_unknown_username(store):
    with pytest.raises(InvalidCredentialsError):
        store.verify_password("nobody", "whatever")


def test_create_player_raises_for_duplicate_username(store):
    store.create_player("alice", "hunter2")

    with pytest.raises(UsernameTakenError):
        store.create_player("alice", "a-different-password")


def test_update_rating_persists(store):
    store.create_player("alice", "hunter2")

    store.update_rating("alice", 1350)

    assert store.get_rating("alice") == 1350


def test_same_password_gets_different_hashes_for_different_users(store):
    # proves the salt is actually random per-user, not a fixed constant -
    # if it weren't, two identical passwords would produce identical
    # rows in the database, defeating the point of salting.
    store.create_player("alice", "same-password")
    store.create_player("bob", "same-password")

    row_alice = store._conn.execute(
        "SELECT password_hash, salt FROM players WHERE username = ?", ("alice",)
    ).fetchone()
    row_bob = store._conn.execute(
        "SELECT password_hash, salt FROM players WHERE username = ?", ("bob",)
    ).fetchone()

    assert row_alice[1] != row_bob[1]        # different salts
    assert row_alice[0] != row_bob[0]         # therefore different hashes