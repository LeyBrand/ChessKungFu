# Part A - bussines_logic/model/game_state.py
class GameState:
    """
    מצב המשחק - data only, לא logic
    Malki's approach: struct עם board + is_game_over
    """
    def __init__(self, board):
        self.board = board
        self.is_game_over = False