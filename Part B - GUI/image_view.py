import cv2
from sprite_library import SpriteLibrary

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
    pt1 = (col * cell_size, row * cell_size)
    pt2 = (pt1[0] + cell_size, pt1[1] + cell_size)
    cv2.rectangle(frame, pt1, pt2, SELECTED_OUTLINE, 4)


def _draw_pieces(frame, pieces, cell_size, elapsed_seconds):
    for piece in pieces:
        x, y = _piece_pixel(piece["position"], piece["motion"], cell_size)
        state = "move" if piece["motion"] is not None else "idle"
        sprite = _sprite_library.get_frame(piece["kind"], piece["color"], state, elapsed_seconds)
        _overlay_sprite(frame, sprite, int(x), int(y), cell_size)


def _piece_pixel(position, motion, cell_size):
    if motion is None:
        col, row = position
        return col * cell_size, row * cell_size

    from_col, from_row = motion["from"]
    to_col, to_row = motion["to"]
    progress = motion["progress"]
    x = (from_col + (to_col - from_col) * progress) * cell_size
    y = (from_row + (to_row - from_row) * progress) * cell_size
    return x, y


def _overlay_sprite(frame, sprite, x, y, cell_size, scale=0.8):
    sprite_size = int(cell_size * scale)
    offset = (cell_size - sprite_size) // 2

    resized = cv2.resize(sprite, (sprite_size, sprite_size), interpolation=cv2.INTER_AREA)
    px, py = x + offset, y + offset
    region = frame[py:py + sprite_size, px:px + sprite_size, :3]

    if resized.shape[2] == 4:
        alpha = resized[:, :, 3] / 255.0
        for c in range(3):
            region[:, :, c] = alpha * resized[:, :, c] + (1 - alpha) * region[:, :, c]
    else:
        region[:] = resized[:, :, :3]

    return frame