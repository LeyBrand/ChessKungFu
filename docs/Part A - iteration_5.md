This iteration adds pawn movement rules for white and black pawns.
The tests check that white pawns move upward, black pawns move downward, and pawns capture diagonally.
They also check that pawns cannot move two cells or capture forward.

בעצם יש כאן הוספה לאיטרציה 3 נכון?
אולי אפשר פשוט לעשות את זה בשורות בודודת?

---


כן, בדיוק. ב-[is_valid_move](c:\Users\User\Desktop\ChessKungFu\Part A - business_logic\iteration_3\logic.py#L5) יש כבר `return True` לכל דבר שאינו K/R/B/Q/N — אז רק צריך להוסיף לפני זה את ה-P:

```python
if p == 'P':
    color = piece[0]
    direction = -1 if color == 'w' else 1
    if col_diff == 0:
        return dr - sr == direction
    return col_diff == 1 and dr - sr == direction
```

זה מטפל ב:
- לבן עולה (`direction = -1`), שחור יורד (`direction = 1`)
- `col_diff == 0` → תנועה ישרה (שורה אחת בלבד)
- `col_diff == 1` → לכידה אלכסונית (שורה אחת)

---

אז איך אני מוסיפה את זה בצורה כזאת שזה עדיין ישמר בקובץ נפרד?

---


תיצרי `iteration_5/logic.py` שמייבא מ-iteration_3 ומוסיף רק את ה-P:

```python
from iteration_3.logic import is_valid_move as _is_valid_move, process_click as _process_click, processer

def is_valid_move(piece, src, dst, board=None):
    if piece[1] == 'P':
        sc, sr = src
        dc, dr = dst
        col_diff = abs(dc - sc)
        direction = -1 if piece[0] == 'w' else 1
        if col_diff == 0:
            return dr - sr == direction
        return col_diff == 1 and dr - sr == direction
    return _is_valid_move(piece, src, dst, board)

def process_click(x, y, board, selected_pos):
    return _process_click(x, y, board, selected_pos, validator=is_valid_move)

if __name__ == "__main__":
    processer(click_handler=process_click)
```

בדיוק כמו הדפוס של iteration_4 — מייבא מהאיטרציה הקודמת, מוסיף רק מה שחדש, ומעביר הלאה.

---

אינ רוצה קובץ טסט

---


הנה הטסטים ל-`iteration_5/test_logic.py`:

```python
import pytest
from iteration_1.logic import board_piecec_parsing
from iteration_5.logic import is_valid_move, process_click

def test_white_pawn_forward():
    assert is_valid_move('wP', (0, 2), (0, 1)) is True

def test_white_pawn_backward():
    assert is_valid_move('wP', (0, 2), (0, 3)) is False

def test_black_pawn_forward():
    assert is_valid_move('bP', (0, 1), (0, 2)) is True

def test_black_pawn_backward():
    assert is_valid_move('bP', (0, 1), (0, 0)) is False

def test_white_pawn_capture():
    assert is_valid_move('wP', (1, 2), (2, 1)) is True

def test_pawn_two_cells():
    assert is_valid_move('wP', (0, 4), (0, 2)) is False

def test_pawn_capture_forward():
    assert is_valid_move('wP', (0, 2), (0, 1)) is True
    assert is_valid_move('wP', (1, 2), (1, 1)) is True  # לא לכידה — תנועה ישרה

def test_pawn_click():
    board = board_piecec_parsing(". . .\nwP . .\n. . .")
    sel = process_click(50, 150, board, None)
    sel = process_click(50, 50, board, sel)
    assert sel is None
    assert board[0][0] == 'wP'
```

---

Test 6: pawn_cannot_capture_forward
Incorrect program output
--- Input ---
 Board:
. bR .
. wP .
. . .
Commands:
click 150 150
click 150 50
wait 1000
print board

--- Program output ---
. wP .
. . .
. . .

--- Expected output (exact text)---
. bR .
. wP .
. . .

Summary of tests
+------------------------------+
|  6 tests run/ 5 tests passed |
+------------------------------+

---


הבעיה היא שהפיון יכול לנוע קדימה גם כשיש כלי שם. צריך לאסור תנועה ישרה אם היעד תפוס.

זה דורש גישה ל-`board`, אז צריך לעדכן את `is_valid_move`:

```python
def is_valid_move(piece, src, dst, board=None):
    if piece[1] == 'P':
        sc, sr = src
        dc, dr = dst
        col_diff = abs(dc - sc)
        direction = -1 if piece[0] == 'w' else 1
        if col_diff == 0:
            if board is not None and board[dr][dc] != '.':
                return False
            return dr - sr == direction
        return col_diff == 1 and dr - sr == direction
    return _is_valid_move(piece, src, dst, board)
```

ועדכון `process_click` כדי להעביר את ה-board ל-validator:

```python
def process_click(x, y, board, selected_pos):
    return _process_click(x, y, board, selected_pos,
                          validator=lambda piece, src, dst: is_valid_move(piece, src, dst, board))
```

---

Agentic coding - ON

---

תעדכן

---

I will scan the entire code for the following files:
- `c:\Users\User\Desktop\ChessKungFu\Part A - business_logic\iteration_5\logic.py`

---


עודכן. השינויים:
- נוסף בדיקת `board[dr][dc] != '.'` לפני תנועה ישרה
- `process_click` מעביר עכשיו `board` ל-validator דרך lambda