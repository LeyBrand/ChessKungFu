PIECE_RULES = {
    'K': lambda cd, rd: cd <= 1 and rd <= 1,
    'R': lambda cd, rd: cd == 0 or rd == 0,
    'B': lambda cd, rd: cd == rd,
    'Q': lambda cd, rd: cd == 0 or rd == 0 or cd == rd,
    'N': lambda cd, rd: (cd == 2 and rd == 1) or (cd == 1 and rd == 2),
}

SLIDING_PIECES = {'Q', 'R', 'B'}


class piece:
    def __init__(self, piece, piece_rules = None):
        self.color = piece[0]
        self.type = piece[1]
        self.piece_rules = piece_rules or PIECE_RULES[type]
        self.direction = -1 if self.color == 'w' else 1

    def is_same_color(self, other):
        return self.color == other.color

    