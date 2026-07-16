from constants import CELL_SIZE

def cell_to_pixel(col, row):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    return (x, y)