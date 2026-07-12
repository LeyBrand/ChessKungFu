# Part A - bussines_logic/model/game_state.py
class GameState:
    def __init__(self, board):
        self.board = board
        self.game_over = False