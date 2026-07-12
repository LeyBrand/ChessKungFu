# Part A - bussines_logic/text_tests/script_runner.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from input.controller import Controller
from engine.game_engine import GameEngine


def run(board, commands):
    """
    הפעל סדרת commands על board
    
    חשוב: יוצרים GameEngine פעם אחת לכל run
    כדי ששמירת state תעבוד בצורה נכונה
    """
    engine = GameEngine(board)
    controller = Controller(engine)
    
    for command in commands:
        controller.handle(command, board)