import pytest
from io import StringIO
from logic import print_board

@pytest.mark.parametrize("input_text, expected_output", [
    # Test 2: לוח מלבני 3x4
    (
        "Board:\nwK . . bK\n. . . .\nwR . . bR\nCommands: print board",
        "wK . . bK\n. . . .\nwR . . bR"
    ),
    # Test 3: אסימונים וצבעים שונים
    (
        "Board:\nwK . bQ\n. wN .\nbP . wR\nCommands: print board",
        "wK . bQ\n. wN .\nbP . wR"
    ),
    # Test 4: זיהוי טוקן לא חוקי
    (
        "Board: wK xZ . . Commands: ",
        "ERROR UNKNOWN_TOKEN"
    ),
    # Test 5: חוסר התאמה ברוחב השורות
    (
        "Board:\nwK . . .\nbK\nCommands: ",
        "ERROR ROW_WIDTH_MISMATCH"
    )
])
def test_board_parsing(monkeypatch, capsys, input_text, expected_output):
    # החלפת ה-stdin בקלט המדומה
    monkeypatch.setattr('sys.stdin', StringIO(input_text))
    
    # הרצת הפונקציה הראשית
    print_board()
    
    # קריאת הפלט שהודפס
    captured = capsys.readouterr().out.strip()
    
    # השוואה לתוצאה המצופה
    assert captured == expected_output