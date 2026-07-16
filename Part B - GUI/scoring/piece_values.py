"""
Standard chess piece values, used only for the GUI-side scoreboard. Kings are
never scored (a king is never "captured" under the normal rules the engine
enforces - the game ends instead).
"""

PIECE_VALUES = {
    "P": 1,
    "N": 3,
    "B": 3,
    "R": 5,
    "Q": 9,
    "K": 0,
}


def value_of(kind):
    return PIECE_VALUES.get(kind, 0)
