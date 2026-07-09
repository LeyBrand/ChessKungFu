import pytest
from io import StringIO
import sys
# בהנחה שהלוגיקה נמצאת ב-iteration_1.logic
from iteration_1.logic import board_piecec_parsing, print_board

def test_board_parsing(capsys):
    # נבדוק את הלוגיקה על ידי העברת הקלט לפונקציית ה-parsing
    # ולא על ידי הרצת ה-main כולו, כדי להימנע מבעיות עם sys.exit
    
    # טסט ללוח תקין
    input_text = "wK . . bK\n. . . .\nwR . . bR"
    expected_output = "wK . . bK\n. . . .\nwR . . bR\n"
    
    parsed = board_piecec_parsing(input_text)
    print_board(parsed)
    
    captured = capsys.readouterr().out
    assert captured == expected_output

def test_unknown_token(capsys):
    # בדיקת טוקן לא חוקי
    invalid_input = "wK xZ . ."
    
    # בודקים שהפונקציה מדפיסה את השגיאה כפי שהגדרת
    with pytest.raises(SystemExit):
        board_piecec_parsing(invalid_input)
    
    captured = capsys.readouterr().out
    assert "ERROR UNKNOWN_TOKEN" in captured

def test_row_width_mismatch(capsys):
    # בדיקת חוסר התאמה ברוחב
    mismatched_input = "wK . .\nbK"
    
    with pytest.raises(SystemExit):
        board_piecec_parsing(mismatched_input)
        
    captured = capsys.readouterr().out
    assert "ERROR ROW_WIDTH_MISMATCH" in captured