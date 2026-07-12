# Part A - bussines_logic/model/game_state.py
class GameState:
    """
    מצב המשחק - data only, לא logic
    אחראי רק לשמירת data
    """
    def __init__(self, board):
        self.board = board
        self.game_over = False