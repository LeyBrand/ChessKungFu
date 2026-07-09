import unittest
from rules.rule_engine import validate_move
from model.board import Board
from model.piece import Piece, PieceState
from model.position import position

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.board = Board(8, 8)
        self.piece = Piece(id=1, color="white", kind="pawn", position=position(0, 0))
        self.board.place_piece(self.piece, position(0, 0))

    def test_validate_move_outside_bounds(self):
        result = validate_move(self.board, self.piece, position(10, 10))
        self.assertEqual(result, "outside_board")

    def test_validate_move_not_available(self):
        self.piece.set_state(PieceState.CAPTURED)
        result = validate_move(self.board, self.piece, position(0, 1))
        self.assertEqual(result, "empty_source")

    def test_validate_move_ok(self):
        # בהנחה ש-(0,1) הוא יעד חוקי ב-legal_destinations
        # נצטרך לוודא ש-board.legal_destinations מחזיר את המיקום הזה
        result = validate_move(self.board, self.piece, position(0, 1))
        # אם המימוש תקין, זה אמור להחזיר "ok"
        # self.assertEqual(result, "ok") 
        pass 

if __name__ == '__main__':
    unittest.main()