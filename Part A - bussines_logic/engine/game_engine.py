import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from constants import MOVE_MS
from realtime.real_time_arbiter import RealTimeArbiter
from realtime.motion import Motion
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
    - מקבל GameState (לא יוצר)
    - מחזיק RealTimeArbiter (שמנהל motions + resolution)
    - עושה רק validation ו-request_move
    """
    
    def __init__(self, state):
        """קבל GameState מחוץ (לא יוצר)"""
        self.state = state
        self.arbiter = RealTimeArbiter(self.state.board)
        self.move_history = []
    
    def has_motion_on_path(self, from_pos, to_pos):
        """בדוק אם כבר יש motion בדרך"""
        for motion in self.arbiter.get_active_motions():
            if motion.start_pos == from_pos or motion.end_pos == to_pos:
                return True
        return False
    
    def request_move(self, from_pos, to_pos):
        """בקש move חדש - רק validation"""
        # בדוק אם המשחק הסתיים
        if self.state.game_over:
            return MoveResult(False, "game_over")
        
        # בדוק אם הposition חוקי
        if not self.state.board.in_bounds(from_pos) or not self.state.board.in_bounds(to_pos):
            return MoveResult(False, "out_of_bounds")
        
        # בדוק אם יש piece בموضע המוצא
        piece = self.state.board.get_piece_at(from_pos)
        if piece is None:
            return MoveResult(False, "empty_source")
        
        # בדוק אם כבר יש motion בדרך
        if self.has_motion_on_path(from_pos, to_pos):
            return MoveResult(False, "motion_in_progress")
        
        # בדוק אם move חוקי (דרך rule_engine)
        from rules.rule_engine import validate_move
        validation_result = validate_move(self.state.board, piece, to_pos)
        if validation_result != "ok":
            return MoveResult(False, validation_result)
        
        # צור Motion חדש
        now = self.arbiter.now()
        motion = Motion(piece, from_pos, to_pos, now)
        
        # קבע את ה-piece כ-moving
        piece.set_state(PieceState.MOVING)
        
        # הוסף לarbiter
        self.arbiter.add_motion(motion)
        self.move_history.append((from_pos, to_pos, "motion_added"))
        
        return MoveResult(True, "ok")
    
    def wait(self, ms):
        """צפה ms מילישניות - arbiter עושה הכל"""
        if self.arbiter.tick(ms):
            self.state.game_over = True
    
    def snapshot(self):
        """צור תמונת מזל של כל ה-state"""
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
