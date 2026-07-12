# Part A - bussines_logic/engine/game_engine.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import MOVE_MS
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion
from model.game_state import GameState
from model.piece import PieceState


class MoveResult:
    """תוצאה של ניסיון move"""
    def __init__(self, success, message):
        self.success = success
        self.message = message


class GameEngine:
    """
    מנוע המשחק - אחראי על כל ה-logic של המשחק
    
    Malki's Architecture:
    - מחזיק GameState (שמכיל board + game_over)
    - מחזיק RealTimeArbiter (שמנהל את ה-motions)
    - אחראי על motion validation ו-completion
    """
    
    def __init__(self, board):
        """
        אתחול engine עם board
        יוצר GameState בתוך Engine
        """
        self.state = GameState(board)
        self.arbiter = RealTimeArbiter(self.state.board)
        
        # History לצורך debug/snapshot
        self.move_history = []
    
    def has_motion_on_path(self, from_pos, to_pos):
        """
        בדוק אם כבר יש motion בדרך
        זה חשוב כדי לא לחסום את אותה משבצת פעמיים
        """
        for motion in self.arbiter.get_active_motions():
            # בדוק אם המשבצת המוצא או היעד כבר בשימוש
            if motion.start_pos == from_pos or motion.end_pos == to_pos:
                return True
        return False
    
    def request_move(self, from_pos, to_pos):
        """
        בקש move חדש
        החזר MoveResult עם success flag
        
        השלבים:
        1. בדוק אם המשחק הסתיים
        2. בדוק אם יש motion בדרך
        3. בדוק אם move חוקי (דרך rule_engine)
        4. צור Motion וקבע אותו
        """
        # שלב 1: בדוק אם המשחק הסתיים
        if self.state.game_over:
            return MoveResult(False, "game_over")
        
        # שלב 2: בדוק אם הposition חוקי
        if not self.state.board.in_bounds(from_pos) or not self.state.board.in_bounds(to_pos):
            return MoveResult(False, "out_of_bounds")
        
        # שלב 3: בדוק אם יש piece בموضع המוצא
        piece = self.state.board.get_piece_at(from_pos)
        if piece is None:
            return MoveResult(False, "empty_source")
        
        # שלב 4: בדוק אם כבר יש motion בדרך
        if self.has_motion_on_path(from_pos, to_pos):
            return MoveResult(False, "motion_in_progress")
        
        # שלב 5: בדוק אם move חוקי (דרך rule_engine)
        from rules.rule_engine import validate_move
        validation_result = validate_move(self.state.board, piece, to_pos)
        if validation_result != "ok":
            return MoveResult(False, validation_result)
        
        # שלב 6: צור Motion חדש
        now = self.arbiter.now()
        motion = Motion(piece, from_pos, to_pos, now)
        
        # שלב 7: קבע את ה-piece כ-moving
        piece.set_state(PieceState.MOVING)
        
        # שלב 8: הוסף לarbiter
        self.arbiter.add_motion(motion)
        self.move_history.append((from_pos, to_pos, "motion_added"))
        
        return MoveResult(True, "ok")
    
    def wait(self, ms):
        """
        צפה ms מילישניות
        זה קדם את השעון ובדוק אילו motions הסתיימו
        """
        self.arbiter.advance(ms)
        self._resolve_motions()
    
    def _resolve_motions(self):
        """
        זה הלב של engine - בדוק אילו motions הסתיימו
        וביצע את updates בboard
        
        משלב:
        1. מצא את כל ה-motions שסיימו
        2. עדכן את board
        3. בדוק הכתרה
        4. בדוק אם מלך נתפס (game_over)
        """
        now = self.arbiter.now()
        
        # מצא את כל ה-motions שסיימו
        completed_motions = []
        for motion in self.arbiter.get_active_motions():
            if motion.is_complete(now):
                completed_motions.append(motion)
        
        # עדכן את board עבור כל motion שהסתיים
        for motion in completed_motions:
            # בדוק מה נתפסה לפני שמוזיזים
            captured_piece = self.state.board.get_piece_at(motion.end_pos)
            
            # בצע את התנועה בboard
            self.state.board.remove_piece(motion.start_pos)
            motion.piece.move_to(motion.end_pos)
            self.state.board.place_piece(motion.piece, motion.end_pos)
            motion.piece.set_state(PieceState.IDLE)
            
            self.move_history.append((motion.start_pos, motion.end_pos, "completed"))
            
            # הסר motion מ-arbiter
            self.arbiter.remove_motion(motion)
            
            # בדוק הכתרה (pawn promotion)
            if motion.piece.kind == "P":
                promotion_row = 0 if motion.piece.color == "white" else self.state.board.rows - 1
                if motion.end_pos.row == promotion_row:
                    motion.piece.kind = "Q"
                    self.move_history.append(("promotion", motion.end_pos, "queen"))
            
            # בדוק אם מלך נתפס
            if captured_piece is not None and captured_piece.kind == "K":
                self.state.game_over = True
                self.move_history.append(("game_over", captured_piece, "king_captured"))
    
    def snapshot(self):
        """
        צור תמונת מזל של כל ה-state
        לצורך saving/loading משחקים
        """
        pieces_state = {}
        for (col, row), piece in self.state.board.pieces.items():
            pieces_state[(col, row)] = {
                'id': piece.id,
                'kind': piece.kind,
                'color': piece.color,
                'state': piece.state
            }
        
        active_motions_snapshot = []
        for motion in self.arbiter.get_active_motions():
            active_motions_snapshot.append({
                'from': (motion.start_pos.col, motion.start_pos.row),
                'to': (motion.end_pos.col, motion.end_pos.row),
                'started_at': motion.start_time,
                'duration': motion.duration_ms,
                'piece_id': motion.piece.id
            })
        
        return {
            'timestamp': self.arbiter.now(),
            'board_pieces': pieces_state,
            'game_over': self.state.game_over,
            'active_motions': active_motions_snapshot,
            'move_history': self.move_history
        }