import time


class DisconnectTimer:
    """Offline-testable - same clock-injection pattern as Matchmaker."""

    def __init__(self, clock=None, timeout_sec=20):
        self._clock = clock or time.monotonic
        self._timeout_sec = timeout_sec
        self._pending = {}  # (room_id, color) -> started_at

    def start(self, room_id, color):
        self._pending[(room_id, color)] = self._clock()

    def cancel(self, room_id, color):
        self._pending.pop((room_id, color), None)

    def is_pending(self, room_id, color):
        return (room_id, color) in self._pending

    def seconds_remaining(self, room_id, color):
        started = self._pending.get((room_id, color))
        if started is None:
            return None
        return max(0, self._timeout_sec - (self._clock() - started))

    def check_expired(self):
        now = self._clock()
        expired = [key for key, started in self._pending.items()
                   if now - started >= self._timeout_sec]
        for key in expired:
            del self._pending[key]
        return expired  # list of (room_id, color)