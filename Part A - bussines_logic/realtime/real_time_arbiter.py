# Part A - bussines_logic/realtime/real_time_arbiter.py
import time

class RealTimeArbiter:
    """
    מנהל הזמן של המשחק
    לא singleton - כל GameEngine יוצר את שלו
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
    
    def reset(self):
        """אתחל את הarbiter"""
        self.game_clock_ms = 0
        self.active_motions = []