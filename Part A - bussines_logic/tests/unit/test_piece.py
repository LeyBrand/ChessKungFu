import unittest
from model.piece import Piece, PieceState
from model.position import position

class TestPiece(unittest.TestCase):
    def setUp(self):
        # יצירת כלי לבדיקה לפני כל טסט
        self.pos = position(0, 0)
        self.piece = Piece(id=1, color="white", kind="pawn", position=self.pos)

    def test_initial_state(self):
        # בדיקה שהכלי מתחיל ב-IDLE
        self.assertEqual(self.piece.state, PieceState.IDLE)
        self.assertTrue(self.piece.is_available())

    def test_move_updates_position(self):
        # בדיקה שהזזה מעדכנת את המיקום
        new_pos = position(1, 1)
        self.piece.move_to(new_pos)
        self.assertEqual(self.piece.position, new_pos)

    def test_state_change(self):
        # בדיקה ששינוי מצב עובד ושזה משפיע על הזמינות
        self.piece.set_state(PieceState.MOVING)
        self.assertEqual(self.piece.state, PieceState.MOVING)
        self.assertFalse(self.piece.is_available())
        
        self.piece.set_state(PieceState.CAPTURED)
        self.assertEqual(self.piece.state, PieceState.CAPTURED)
        self.assertFalse(self.piece.is_available())

if __name__ == '__main__':
    unittest.main()