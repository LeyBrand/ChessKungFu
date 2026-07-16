"""
Computes each player's score purely from consecutive snapshots the GUI
already receives from Part A. Pure GUI-side bookkeeping - never talks to
Part A directly, only reads data it already exposes (id/kind/color/state
per piece).

Why this needs to be STATEFUL (not a one-shot function of a single
snapshot): the engine has two different ways a piece stops being "on the
board", and neither one alone is a reliable capture signal:

  1. Ordinary capture (piece A moves onto a square occupied by piece B):
     the board's internal dict is simply overwritten - piece B disappears
     from the snapshot entirely, with no marker of any kind.
  2. Simultaneous-motion collision (e.g. a jump landing at the same time
     another piece moves there): the loser is explicitly marked
     state == "captured", but is never actually removed from the snapshot.

So we track piece identity (id) across frames: anything that silently
disappears between two calls to update() is capture case (1); anything
newly marked state == "captured" is capture case (2). Either way, its
value goes to the OPPOSING color, counted exactly once.
"""

from scoring.piece_values import value_of

OPPONENT = {"white": "black", "black": "white"}


class ScoreTracker:
    def __init__(self):
        self._last_seen = {}           # id -> {"kind": ..., "color": ...}
        self._already_counted = set()  # ids already scored, never double-count
        self.scores = {"white": 0, "black": 0}

    def update(self, pieces):
        """Feed the latest snapshot's pieces list. Returns the current
        {"white": n, "black": n} totals."""
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
