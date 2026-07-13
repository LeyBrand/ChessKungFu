class Board:
    """
    Board הוא הבעלים של הסידור הלוגי של הכלים בלבד.
    אין לו שום ידע על חוקי תנועה של שחמט - זו אחריות של RuleEngine.
    """

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.pieces = {}

    def in_bounds(self, position):
        return 0 <= position.col < self.cols and 0 <= position.row < self.rows

    def get_piece_at(self, position):
        return self.pieces.get((position.col, position.row))

    def add_piece(self, piece, position):
        """
        הוספת כלי חדש ללוח (משמש בזמן בניית הלוח הראשוני מהפרסינג).
        דוחה תפוסה כפולה - נכשל אם התא כבר תפוס.
        """
        key = (position.col, position.row)
        if key in self.pieces:
            raise ValueError(f"Cell {key} is already occupied")

        self.pieces[key] = piece
        piece.position = position

    def remove_piece(self, position):
        key = (position.col, position.row)
        if key in self.pieces:
            del self.pieces[key]

    def place_piece(self, piece, position):
        """
        הצבה גולמית של כלי במשבצת - דורסת כל מה שהיה שם (כולל אכילה).
        משמשת בעיקר כחלק פנימי של move_piece, וגם ע"י מנגנונים מיוחדים
        (כמו נחיתה אחרי קפיצה) שאינם "מהלך רגיל" עם מקור ויעד.
        """
        self.pieces[(position.col, position.row)] = piece
        piece.position = position

    def move_piece(self, from_pos, to_pos):
        """
        הזזת כלי לאחר שהמהלך כבר אומת במקום אחר (RuleEngine).
        Board לא בודק חוקיות - הוא רק מבצע את ההזזה בפועל,
        כולל דריסה/אכילה של מה שהיה ביעד אם צריך.
        """
        piece = self.get_piece_at(from_pos)
        if piece is None:
            return

        self.remove_piece(from_pos)
        self.place_piece(piece, to_pos)