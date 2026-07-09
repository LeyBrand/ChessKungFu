import unittest
from model.board import Board
from model.piece import Piece
from model.position import position
import input.controller  # שימי לב: ייבוא של כל המודול

class TestControllerFlow(unittest.TestCase):
    def setUp(self):
        self.board = Board(8, 8)
        self.rook = Piece(id=1, color="white", kind="rook", position=position(0, 0))
        self.board.place_piece(self.rook, position(0, 0))
        input.controller.selected_pos = None # איפוס ישיר דרך המודול

    def test_move_rook_success(self):
        # 1. לחיצה ראשונה
        input.controller.click(position(0, 0), self.board)
        # בדיקה דרך המודול
        self.assertEqual(input.controller.selected_pos, position(0, 0))
        
        # 2. לחיצה שנייה
        input.controller.click(position(0, 5), self.board)
        
        # בדיקה שהכלי זז
        self.assertIsNone(self.board.get_piece_at(position(0, 0)))
        self.assertEqual(self.board.get_piece_at(position(0, 5)), self.rook)
        self.assertIsNone(input.controller.selected_pos)
if __name__ == '__main__':
    unittest.main()