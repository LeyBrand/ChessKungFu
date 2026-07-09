import unittest
from model.board import Board
from model.piece import Piece
from model.position import position
from rules.rook_rule import get_rook_moves

class TestRookRule(unittest.TestCase):
    def setUp(self):
        self.board = Board(8, 8)
        self.rook = Piece(id=1, color="white", kind="rook", position=position(3, 3))
        self.board.place_piece(self.rook, position(3, 3))

    def test_rook_moves(self):
        moves = get_rook_moves(self.board, self.rook)
        # צריח במרכז הלוח צריך להיות עם 14 מהלכים חוקיים (7 בכל כיוון)
        self.assertEqual(len(moves), 14)

if __name__ == '__main__':
    unittest.main()