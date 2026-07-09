import unittest
from model.board import Board
from model.position import position
from model.piece import Piece

class TestBoard(unittest.TestCase):
    def setUp(self):
        # לוח סטנדרטי 8x8
        self.board = Board(8, 8)
        self.piece = Piece(id=1, color="white", kind="pawn", position=position(0, 0))

    def test_in_bounds(self):
        # בדיקת גבולות תקינה
        self.assertTrue(self.board.in_bounds(position(0, 0)))
        self.assertTrue(self.board.in_bounds(position(7, 7)))
        # בדיקת גבולות חורגת
        self.assertFalse(self.board.in_bounds(position(8, 0)))
        self.assertFalse(self.board.in_bounds(position(-1, 0)))

    def test_place_and_get_piece(self):
        pos = position(2, 2)
        self.board.place_piece(self.piece, pos)
        self.assertEqual(self.board.get_piece_at(pos), self.piece)
        self.assertEqual(self.piece.position, pos)

    def test_friendly_destination(self):
        target = Piece(id=2, color="white", kind="rook", position=position(1, 1))
        self.board.place_piece(self.piece, position(0, 0))
        self.board.place_piece(target, position(1, 1))
        
        # האם (1,1) נחשב ליעד ידידותי עבור ה-pawn ב-(0,0)?
        self.assertTrue(self.board.is_friendly_destination(self.piece, position(1, 1)))

if __name__ == '__main__':
    unittest.main()