from scoring.piece_values import value_of

OPPONENT = {"white": "black", "black": "white"}


class ScoreTracker:
    def __init__(self):
        self._last_seen = {}           # id -> {"kind": ..., "color": ...}
        self._already_counted = set()  
        self.scores = {"white": 0, "black": 0}

    def update(self, pieces):
        current_ids = set()

        for piece in pieces:
            pid = piece["id"]
            current_ids.add(pid)
            self._last_seen[pid] = {"kind": piece["kind"], "color": piece["color"]}

            if piece.get("state") == "captured":
                self._count_capture(pid)

        vanished_ids = set(self._last_seen.keys()) - current_ids - self._already_counted
        for pid in vanished_ids:
            self._count_capture(pid)

        return dict(self.scores)

    def _count_capture(self, pid):
        if pid in self._already_counted:
            return
        info = self._last_seen[pid]
        capturer = OPPONENT[info["color"]]
        self.scores[capturer] += value_of(info["kind"])
        self._already_counted.add(pid)
