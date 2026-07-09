class Board:
    def __init__(self, cols, rows):
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