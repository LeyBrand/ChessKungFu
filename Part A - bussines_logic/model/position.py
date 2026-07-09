class position:
    def __init__(self, col, row):
        self.col = col
        self.row = row

    def __eq__(self, other):
        return self.col == other.col and self.row == other.row

    def __repr__(self):
        return f"({self.col}, {self.row})"