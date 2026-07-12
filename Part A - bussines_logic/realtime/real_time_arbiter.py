import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.piece import PieceState


class RealTimeArbiter:
    """
    מנהל הזמן של המשחק
    אחראי על motions + motion resolution (כמו Malki)
    """
    
    def __init__(self, board):
        self.board = board
        self.game_clock_ms = 0
        self.active_motions = []
    
    def now(self):
        """החזר את הזמן הנוכחי של המשחק"""
        return self.game_clock_ms
    
    def advance(self, ms):
        """קדם את השעון ב-ms מילישניות"""
        self.game_clock_ms += ms
    
    def add_motion(self, motion):
        """הוסף motion לרשימה"""
        self.active_motions.append(motion)
    
    def get_active_motions(self):
        """חזר את כל ה-motions הפעילים"""
        return self.active_motions
    
    def remove_motion(self, motion):
        """הסר motion מרשימה"""
        if motion in self.active_motions:
            self.active_motions.remove(motion)
    
    def tick(self, ms):
        """
        קדם את השעון ובצע motions שהסתיימו
        זה הלב של ה-arbiter - כמו Malki
        """
        self.game_clock_ms += ms
        king_captured = False
        
        # מצא את כל ה-motions שסיימו
        completed_motions = []
        for motion in self.active_motions:
            if motion.is_complete(self.game_clock_ms):
                completed_motions.append(motion)
        
        # בצע את כל ה-motions שהסתיימו
        for motion in completed_motions:
            # בדוק מה נתפסה לפני שמוזיזים
            captured_piece = self.board.get_piece_at(motion.end_pos)
            
            # בצע את התנועה בboard
            self.board.remove_piece(motion.start_pos)
            motion.piece.move_to(motion.end_pos)
            self.board.place_piece(motion.piece, motion.end_pos)
            motion.piece.set_state(PieceState.IDLE)
            
            # הסר motion מ-arbiter
            self.active_motions.remove(motion)
            
            # בדוק הכתרה (pawn promotion)
            if motion.piece.kind == "P":
                promotion_row = 0 if motion.piece.color == "white" else self.board.rows - 1
                if motion.end_pos.row == promotion_row:
                    motion.piece.kind = "Q"
            
            # בדוק אם מלך נתפס
            if captured_piece is not None and captured_piece.kind == "K":
                king_captured = True
        
        return king_captured
    
    def reset(self):
        """אתחל את הarbiter"""
        self.game_clock_ms = 0
        self.active_motions = []
