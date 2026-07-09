import unittest
from data_io.board_parser import parse # ודאי שהייבוא נכון
from constants import EMPTY_CELL
from model.position import position

class TestBoardParser(unittest.TestCase):

    def test_parse_valid_board(self):
        board_text = """
        wK . .
        . . bR
        """
        board = parse(board_text)
        self.assertIsNotNone(board)
        # בדיקה שהכלי הוצב נכון
        piece = board.get_piece_at(position(0, 0))
        self.assertEqual(piece.kind, "K")
        self.assertEqual(piece.color, "white")

    def test_error_row_width_mismatch(self):
        # שורה ראשונה 3 עמודות, שורה שנייה 2 עמודות
        board_text = """
        wK . .
        . bR
        """
        with self.assertRaises(SystemExit): # בודק שהקוד אכן עוצר
            parse(board_text)

    def test_error_unknown_token(self):
        # טוקן שלא קיים ב-VALID_PIECES
        board_text = """
        wK wX
        . .
        """
        with self.assertRaises(SystemExit):
            parse(board_text)

    def test_empty_board(self):
        board_text = ""
        board = parse(board_text)
        self.assertIsNone(board)

if __name__ == '__main__':
    unittest.main()