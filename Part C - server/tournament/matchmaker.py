import time


class Matchmaker:
    """Offline-testable matchmaking pool. No network/asyncio imports -
    same principle as TournamentManager. FIFO among ELO-eligible
    candidates: dict insertion order in Python guarantees the
    longest-waiting eligible opponent gets matched first."""

    def __init__(self, clock=None, elo_range=100, timeout_sec=60):
        self._clock = clock or time.monotonic
        self._elo_range = elo_range
        self._timeout_sec = timeout_sec
        self._waiting = {}  # player_id -> {"username", "rating", "joined_at"}

    def seek(self, player_id, username, rating):
        """Returns the matched player_id if an eligible opponent is
        already waiting (and removes them from the pool). Otherwise adds
        this player to the pool and returns None."""
        for other_id, info in self._waiting.items():
            if abs(info["rating"] - rating) <= self._elo_range:
                del self._waiting[other_id]
                return other_id

        self._waiting[player_id] = {
            "username": username,
            "rating": rating,
            "joined_at": self._clock(),
        }
        return None

    def cancel(self, player_id):
        self._waiting.pop(player_id, None)

    def check_timeouts(self):
        """Returns the player_ids that have waited >= timeout_sec, and
        removes them from the pool."""
        now = self._clock()
        timed_out = [
            pid for pid, info in self._waiting.items()
            if now - info["joined_at"] >= self._timeout_sec
        ]
        for pid in timed_out:
            del self._waiting[pid]
        return timed_out

    def is_waiting(self, player_id):
        return player_id in self._waiting