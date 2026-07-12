import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from input.controller import Controller
from engine.game_engine import GameEngine
from model.game_state import GameState


def run(board, commands):
    """
    הפעל סדרת commands על board
    יוצר GameState בחוץ (לפי Malki architecture)
    """
    state = GameState(board)  # ← יוצר state בחוץ
    engine = GameEngine(state)  # ← GameEngine קבל state
    controller = Controller(engine)
    
    for command in commands:
        controller.handle(command, board)
