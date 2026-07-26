from constants import CELL_SIZE as DEFAULT_CELL_SIZE


def cell_to_pixel(col, row, cell_size=DEFAULT_CELL_SIZE):
    return (col * cell_size, row * cell_size)


def piece_pixel(position, motion, cell_size=DEFAULT_CELL_SIZE):
    if motion is None:
        col, row = position
        return cell_to_pixel(col, row, cell_size)

    from_col, from_row = motion.from_cell
    to_col, to_row = motion.to_cell
    progress = motion.progress

    x = (from_col + (to_col - from_col) * progress) * cell_size
    y = (from_row + (to_row - from_row) * progress) * cell_size
    return (x, y)
