from constants import CELL_SIZE

def pixel_to_cell(x, y):
    col = x // CELL_SIZE
    row = y // CELL_SIZE   
    return (col, row)