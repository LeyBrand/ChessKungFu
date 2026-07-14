from rules.piece_rules import PieceRules


class RookRules(PieceRules):
    DIRECTIONS = [
        (0, 1), (0, -1), (1, 0), (-1, 0)  
    ]

    def legal_destinations(self, board, piece):
        return self._sliding_moves(board, piece, self.DIRECTIONS)