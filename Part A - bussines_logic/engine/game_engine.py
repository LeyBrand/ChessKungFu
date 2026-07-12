# Part A - bussines_logic/engine/game_engine.py

from constants import EMPTY_CELL, MOVE_MS
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion
from model.piece import PieceState

class MoveResult:
    def __init__(self, success, message):
        self.success = success
        self.message = message

class GameEngine:
    """
    מנוע המשחק - מחזיק את ה-state של המשחק
    זה המקום היחיד שמחזיק את הtruth של המצב
    """
    def __init__(self, board):
        self.board = board
        self.arbiter = RealTimeArbiter.instance()
        
        # STATE - זה מה שמשתמר בין קריאות
        self.selected_pos = None
        self.active_motion = None
        self.queued_moves = []
        self.game_over = False
        
        # History לצורך snapshot
        self.move_history = []
    
    def request_move(self, from_pos, to_pos):
        """
        בקש move - זה מה שכל קלט (click/jump) חייב לעבור דרכו
        
        החזיר MoveResult כדי שcontroller יוכל להציג הודעות
        אבל ה-state עצמו נשמר כאן
        """
        # בדוק אם המשחק הסתיים
        if self.game_over:
            return MoveResult(False, "game_over")
        
        # בדוק אם הposition חוקי
        if not self.board.in_bounds(from_pos) or not self.board.in_bounds(to_pos):
            return MoveResult(False, "out_of_bounds")
        
        piece = self.board.get_piece_at(from_pos)
        if piece is None:
            return MoveResult(False, "empty_source")
        
        # בדוק אם move חוקי (דרך rule_engine)
        from rules.rule_engine import validate_move
        validation_result = validate_move(self.board, piece, to_pos)
        if validation_result != "ok":
            return MoveResult(False, validation_result)
        
        # אתה יכול לבצע move! אבל אולי יש motion פעיל
        now = self.arbiter.now()
        piece.set_state(PieceState.MOVING)
        
        motion = Motion(piece, from_pos, to_pos, now)
        
        if self.active_motion is None:
            # אין תנועה פעילה - התחל מיד
            self.active_motion = motion
            self.move_history.append((from_pos, to_pos, "started"))
        else:
            # יש תנועה פעילה - הוסף לתור
            self.queued_moves.append((piece, from_pos, to_pos))
            self.move_history.append((from_pos, to_pos, "queued"))
        
        return MoveResult(True, "move_accepted")
    
    def wait(self, ms):
        """
        צפה ms מילישניות
        זה משדרג את ה-clock ובדוק אם motions הסתיימו
        """
        self.arbiter.advance(ms)
        self._resolve_motions()
    
    def _resolve_motions(self):
        """
        זה ה-_resolve שצריך להיות כאן!!!
        בדוק אילו motions הסתיימו בזמן הנוכחי
        """
        now = self.arbiter.now()
        
        # ייתכן שמספר motions יסתיימו - while loop זה חיוני
        while self.active_motion and self.active_motion.is_complete(now):
            motion = self.active_motion
            
            # בדוק מה נתפסה לפני הפעולה
            captured_piece = self.board.get_piece_at(motion.end_pos)
            
            # בצע את התנועה בboard
            self.board.remove_piece(motion.start_pos)
            motion.piece.move_to(motion.end_pos)
            self.board.place_piece(motion.piece, motion.end_pos)
            motion.piece.set_state(PieceState.IDLE)
            
            self.move_history.append((motion.start_pos, motion.end_pos, "completed"))
            
            self.active_motion = None
            
            # בדוק הכתרה
            if motion.piece.kind == "P":
                promotion_row = 0 if motion.piece.color == "white" else self.board.rows - 1
                if motion.end_pos.row == promotion_row:
                    motion.piece.kind = "Q"
                    self.move_history.append(("promotion", motion.end_pos, "queen"))
            
            # בדוק אם מלך נתפס
            if captured_piece is not None and captured_piece.kind == "K":
                self.game_over = True
                self.queued_moves = []  # מבטלים את התור
                self.move_history.append(("game_over", captured_piece, "king_captured"))
                return  # ← עצור כל דבר
            
            # אם יש תור ברידע - ספוק את התנועה הבאה
            if not self.game_over and self.queued_moves:
                piece, start_pos, destination = self.queued_moves.pop(0)
                new_motion = Motion(piece, start_pos, destination, now)
                piece.set_state(PieceState.MOVING)
                self.active_motion = new_motion
    
    def snapshot(self):
        """
        חזיר תמונת מזל של כל ה-state
        כדי שנוכל להשחזר או לשמור
        """
        pieces_state = {}
        for (col, row), piece in self.board.pieces.items():
            pieces_state[(col, row)] = {
                'id': piece.id,
                'kind': piece.kind,
                'color': piece.color,
                'state': piece.state
            }
        
        return {
            'timestamp': self.arbiter.now(),
            'board_pieces': pieces_state,
            'game_over': self.game_over,
            'active_motion': {
                'from': (self.active_motion.start_pos.col, self.active_motion.start_pos.row),
                'to': (self.active_motion.end_pos.col, self.active_motion.end_pos.row),
                'started_at': self.active_motion.start_time,
                'duration': self.active_motion.duration_ms
            } if self.active_motion else None,
            'queued_count': len(self.queued_moves),
            'move_history': self.move_history
        }