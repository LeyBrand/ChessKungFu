class GameEngine:
    def __init__(self, board, rule_engine):
        self.board = board
        self.rule_engine = rule_engine
        self.is_game_over = False

    def request_move(self, piece, destination):
        # 1. בדיקה אם המשחק הסתיים
        if self.is_game_over:
            return "game_over"

        # 2. בדיקה מול מנוע החוקים (Validation)
        status = self.rule_engine.validate_move(self.board, piece, destination)
        
        if status == "ok":
            # 3. כאן נפעיל את תחילת התנועה (בשלב מאוחר יותר)
            # return self.start_motion(piece, destination)
            return "move_started"
            
        return status