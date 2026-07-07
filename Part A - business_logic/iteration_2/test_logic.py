import pytest
import sys
from io import StringIO
from iteration_2.logic import processer 

def test_click_moves_piece(monkeypatch):
    # 1. הכנת הקלט המדומה
    input_str = "Board:\nwK . .\n. . .\n. . .\nCommands:\nclick 50 50\nclick 150 150\nprint board"
    monkeypatch.setattr('sys.stdin', StringIO(input_str))
    
    # 2. הכנת הזיכרון ללכידת הפלט
    captured_output = StringIO()
    monkeypatch.setattr('sys.stdout', captured_output)
    
    # 3. הרצת התוכנית
    try:
        processer()
    except SystemExit:
        pass # זה מונע מהטסט לקרוס אם יש sys.exit() בקוד
    
    # 4. בדיקת התוצאות
    output = captured_output.getvalue().strip()
    
    # בדיקה שהלוח המעודכן אכן מודפס
    assert ". . ." in output
    assert ". wK ." in output