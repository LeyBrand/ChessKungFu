"""
Single source of truth for converting logical board coordinates (col, row)
into pixel coordinates. This is a GUI-only concern - it deliberately does NOT
depend on Part A's constants, since cell size is a rendering detail, not a
business-logic one.
"""

DEFAULT_CELL_SIZE = 100


def cell_to_pixel(col, row, cell_size=DEFAULT_CELL_SIZE):
    """Static cell -> top-left pixel of that cell."""
    return (col * cell_size, row * cell_size)


def piece_pixel(position, motion, cell_size=DEFAULT_CELL_SIZE):
    """
    Resolve the pixel position of a piece for one rendered frame.

    position: (col, row) - the piece's logical cell
    motion:   None, or {"from": (col, row), "to": (col, row), "progress": 0..1}
    """
    if motion is None:
        col, row = position
        return cell_to_pixel(col, row, cell_size)

    from_col, from_row = motion["from"]
    to_col, to_row = motion["to"]
    progress = motion["progress"]

    x = (from_col + (to_col - from_col) * progress) * cell_size
    y = (from_row + (to_row - from_row) * progress) * cell_size
    return (x, y)
