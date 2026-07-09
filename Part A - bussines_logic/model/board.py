from rules.rook_rule import get_rook_moves

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
        if (position.col, position.row) in self.pieces:
            del self.pieces[(position.col, position.row)]

    def legal_destinations(self, piece):
        if piece.kind == "rook":
            return get_rook_moves(self, piece)
        return [] # כאן נוסיף בהמשך חוקים לשאר