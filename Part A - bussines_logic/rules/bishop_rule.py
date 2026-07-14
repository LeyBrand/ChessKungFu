from rules.piece_rules import PieceRules


class BishopRules(PieceRules):
    DIRECTIONS = [
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]

    def legal_destinations(self, board, piece):
        return self._sliding_moves(board, piece, self.DIRECTIONS)