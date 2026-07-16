from model.game_state import GameState
from engine.game_engine import GameEngine
from input.controller import Controller


def build_app(board):
    state = GameState(board)
    engine = GameEngine(state)
    controller = Controller(engine)
    return state, engine, controller