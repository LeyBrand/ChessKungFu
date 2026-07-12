# Part A - bussines_logic/text_tests/script_runner.py
from input.controller import Controller
from engine.game_engine import GameEngine

def run(board, commands):
    """
    הפעל סדרת commands על board
    """
    engine = GameEngine(board)  # ← יוצר state בתוך engine
    controller = Controller(engine)
    
    for command in commands:
        controller.handle(command, board)