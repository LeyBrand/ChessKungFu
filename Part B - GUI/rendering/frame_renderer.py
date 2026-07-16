"""
Composes one rendered frame: selection outline, pieces (with their sprites),
and a game-over banner. Delegates coordinate math to mapping.graphics_mapper
and pixel compositing to rendering.sprite_compositor - this file's only job
is deciding WHAT to draw and WHERE, not the low-level HOW.
"""

import cv2

from mapping.graphics_mapper import cell_to_pixel, piece_pixel
from rendering.sprite_compositor import overlay_sprite
from rendering.sprite_library import SpriteLibrary

SELECTED_OUTLINE = (51, 51, 255)
GAME_OVER_COLOR = (0, 0, 255)

_sprite_library = SpriteLibrary()


def render_frame(base_img, board_snapshot, cell_size):
    frame = base_img.copy()
    elapsed_seconds = board_snapshot["timestamp_ms"] / 1000.0

    _draw_selection(frame, board_snapshot["selected_cell"], cell_size)
    _draw_pieces(frame, board_snapshot["pieces"], cell_size, elapsed_seconds)

    if board_snapshot["is_game_over"]:
        cv2.putText(frame, "GAME OVER",
                    (frame.shape[1] // 3, frame.shape[0] // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, GAME_OVER_COLOR, 3)

    return frame


def _draw_selection(frame, selected_cell, cell_size):
    if selected_cell is None:
        return
    col, row = selected_cell
    pt1 = cell_to_pixel(col, row, cell_size)
    pt2 = (pt1[0] + cell_size, pt1[1] + cell_size)
    cv2.rectangle(frame, pt1, pt2, SELECTED_OUTLINE, 4)


def _draw_pieces(frame, pieces, cell_size, elapsed_seconds):
    for piece in pieces:
        x, y = piece_pixel(piece["position"], piece["motion"], cell_size)
        state = "move" if piece["motion"] is not None else "idle"
        sprite = _sprite_library.get_frame(piece["kind"], piece["color"], state, elapsed_seconds)
        overlay_sprite(frame, sprite, int(x), int(y), cell_size)
