from rules.piece_rules import PieceRules


class KingRules(PieceRules):
    OFFSETS = [
        (0, 1), (0, -1), (1, 0), (-1, 0),   
        (1, 1), (1, -1), (-1, 1), (-1, -1)  
    ]

    def legal_destinations(self, board, piece):
        return self._single_step_moves(board, piece, self.OFFSETS)