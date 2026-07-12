from rules.rook_rule import get_rook_moves
from rules.king_rule import get_king_moves
from rules.knight_rule import get_knight_moves
from rules.bishop_rule import get_bishop_moves
from rules.queen_rule import get_queen_moves

class Board:
    def __init__(self, rows, cols):
        self.cols = cols
        self.rows = rows
        self.pieces = {}

    def in_bounds(self, position):
        return 0 <= position.col < self.cols and 0 <= position.row < self.rows

    def get_piece_at(self, position):
        return self.pieces.get((position.col, position.row))

    def is_friendly_destination(self, piece, destination):
        target = self.get_piece_at(destination)
        if target is None:
            return False
        return target.color == piece.color

    def place_piece(self, piece, position):
        self.pieces[(position.col, position.row)] = piece
        piece.position = position

    def remove_piece(self, position):
        key = (position.col, position.row)
        if key in self.pieces:
            del self.pieces[key]
    def legal_destinations(self, piece):
        if piece.kind == "R":
            return get_rook_moves(self, piece)
        if piece.kind == "K":
            return get_king_moves(self, piece)
        if piece.kind == "N":
            return get_knight_moves(self, piece)
        if piece.kind == "B":
            return get_bishop_moves(self, piece)
        if piece.kind == "Q":
            return get_queen_moves(self, piece)
        return [] # כאן נוסיף בהמשך חוקים לשאר