class Board:
    def __init__(self, rows_length, cols_length):
        self.rows_length = rows_length
        self.cols_length = cols_length
        self.pieces = {}

    def in_bounds(self, position):
        return 0 <= position.col < self.cols_length and 0 <= position.row < self.rows_length

    def get_piece_at(self, position):
        return self.pieces.get((position.col, position.row))

    def add_piece(self, piece, position):
        key = (position.col, position.row)
        if key in self.pieces:
            raise ValueError(f"Cell {key} is already occupied")

        self.pieces[key] = piece
        piece.position = position

    def remove_piece(self, position):
        key = (position.col, position.row)
        if key in self.pieces:
            del self.pieces[key]

    def place_piece(self, piece, position):
        self.pieces[(position.col, position.row)] = piece
        piece.position = position

    def move_piece(self, from_pos, to_pos):
        piece = self.get_piece_at(from_pos)
        if piece is None:
            return

        self.remove_piece(from_pos)
        self.place_piece(piece, to_pos)