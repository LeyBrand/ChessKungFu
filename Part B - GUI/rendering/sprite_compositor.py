"""
Pure pixel-level compositing: alpha-blends a (possibly RGBA) sprite image
onto a frame at a given pixel position. No knowledge of the game, pieces,
or board coordinates - just image math.
"""

import cv2


def overlay_sprite(frame, sprite, x, y, cell_size, scale=0.8):
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
