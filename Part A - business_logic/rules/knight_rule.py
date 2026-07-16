from rules.piece_rules import PieceRules


class KnightRules(PieceRules):
    OFFSETS = [
        (1, 2), (1, -2), (-1, 2), (-1, -2),
        (2, 1), (2, -1), (-2, 1), (-2, -1)
    ]

    def legal_destinations(self, board, piece):
        return self._single_step_moves(board, piece, self.OFFSETS)