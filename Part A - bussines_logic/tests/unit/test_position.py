import unittest
from model.position import position

class TestPosition(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(position(1, 2), position(1, 2))

    def test_inequality(self):
        self.assertNotEqual(position(1, 2), position(3, 4))
        
    # בדיקה הדוקה: האם הצלחנו ליצור מיקום?
    def test_attributes(self):
        pos = position(5, 7)
        self.assertEqual(pos.col, 5)
        self.assertEqual(pos.row, 7)

    # בדיקה הדוקה: ייצוג טקסטואלי
    def test_repr(self):
        pos = position(0, 0)
        self.assertEqual(repr(pos), "(0, 0)")

if __name__ == '__main__':
    unittest.main()