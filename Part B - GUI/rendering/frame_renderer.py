"""
Composes one rendered frame: selection outline, pieces (with their sprites),
scoreboard, and a game-over banner. All pixel-level operations go through
Img (data/img.py) - the only file in Part B allowed to import cv2. This
file's job is deciding WHAT to draw and WHERE, never the low-level HOW.
"""

from mapping.graphics_mapper import cell_to_pixel, piece_pixel
from rendering.sprite_library import SpriteLibrary
from scoring.score_tracker import ScoreTracker

SELECTED_OUTLINE = (51, 51, 255)
GAME_OVER_COLOR = (0, 0, 255)
SCORE_COLOR = (255, 255, 255)

SPRITE_SCALE = 0.8

_sprite_library = SpriteLibrary()
_score_tracker = ScoreTracker()


def render_frame(base_img, board_snapshot, cell_size):
    frame = base_img.copy()
    elapsed_seconds = board_snapshot["timestamp_ms"] / 1000.0

    _draw_selection(frame, board_snapshot["selected_cell"], cell_size)
    _draw_pieces(frame, board_snapshot["pieces"], cell_size, elapsed_seconds)
    _draw_scoreboard(frame, board_snapshot["pieces"])

    if board_snapshot["is_game_over"]:
        frame.put_text("GAME OVER", cell_size * 2, cell_size * 4, 1.2, GAME_OVER_COLOR, 3)

    return frame


def _draw_selection(frame, selected_cell, cell_size):
    if selected_cell is None:
        return
    col, row = selected_cell
    x, y = cell_to_pixel(col, row, cell_size)
    frame.draw_rect((x, y), (x + cell_size, y + cell_size), SELECTED_OUTLINE, 4)


def _draw_pieces(frame, pieces, cell_size, elapsed_seconds):
    sprite_size = int(cell_size * SPRITE_SCALE)
    offset = (cell_size - sprite_size) // 2

    for piece in pieces:
        if piece.get("state") == "captured":
            # Captured pieces stay in the board's internal dict forever
            # (never removed), so they must be skipped here or they'd be
            # drawn as ghosts sitting at their original square.
            continue
        x, y = piece_pixel(piece["position"], piece["motion"], cell_size)
        state = "move" if piece["motion"] is not None else "idle"
        sprite = _sprite_library.get_frame(
            piece["kind"], piece["color"], state, elapsed_seconds,
            size=(sprite_size, sprite_size),
        )
        sprite.draw_on(frame, int(x) + offset, int(y) + offset)


def _draw_scoreboard(frame, pieces):
    scores = _score_tracker.update(pieces)
    frame.put_text(f"White: {scores['white']}", 10, 30, 0.8, SCORE_COLOR, 2)
    frame.put_text(f"Black: {scores['black']}", 10, 60, 0.8, SCORE_COLOR, 2)
