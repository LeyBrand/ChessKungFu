import unittest
from data_io.board_parser import parse_board
from data_io.board_printer import print_board_to_string # הנחה: פונקציה שמחזירה מחרוזת במקום להדפיס

class TestBoardIO(unittest.TestCase):

    def test_parse_valid_rectangular_board(self):
        board_text = ". wK\n. ."
        board = parse_board(board_text)
        self.assertEqual(board.rows, 2)
        self.assertEqual(board.cols, 2)

    def test_reject_inconsistent_row_length(self):
        board_text = ". wK .\n. ."
        with self.assertRaisesRegex(ValueError, "ROW_WIDTH_MISMATCH"):
            parse_board(board_text)

    def test_reject_unknown_token(self):
        board_text = ". wZ" # wZ אינו כלי חוקי
        with self.assertRaisesRegex(ValueError, "UNKNOWN_TOKEN"):
            parse_board(board_text)

    def test_printer_round_trip(self):
        """בודק שמה שיוצא מהמדפיס זהה למה שנכנס לפארסר"""
        original_text = ". wK\n. ."
        board = parse_board(original_text)
        # בהנחה שיצרת פונקציה שמחזירה מחרוזת (מומלץ לבדיקות)
        output_text = print_board_to_string(board).strip()
        self.assertEqual(output_text, original_text)

if __name__ == '__main__':
    unittest.main()