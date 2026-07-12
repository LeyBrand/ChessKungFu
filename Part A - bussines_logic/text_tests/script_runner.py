# Part A - bussines_logic/text_tests/script_runner.py

from input.controller import Controller
from engine.game_engine import GameEngine

def run(board, commands):
    """
    הפעל סדרת commands על board
    משתמש באותו engine לכל ה-commands (שמירת state!)
    """
    # ← יוצרים engine **פעם אחת** לכל run
    engine = GameEngine(board)
    controller = Controller(engine)
    
    for command in commands:
        controller.handle(command, board)