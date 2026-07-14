LIGHT_SQUARE = "#f0d9b5"
DARK_SQUARE = "#b58863"
SELECTED_OUTLINE = "#ff3333"
GAME_OVER_TEXT_COLOR = "#ff0000"


def build_draw_instructions(snapshot, cell_size):
    instructions = []

    for row in range(snapshot.board_height):
        for col in range(snapshot.board_width):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            instructions.append({
                "type": "rect",
                "x": col * cell_size,
                "y": row * cell_size,
                "width": cell_size,
                "height": cell_size,
                "color": color,
            })

    if snapshot.selected_cell is not None:
        col, row = snapshot.selected_cell
        instructions.append({
            "type": "rect_outline",
            "x": col * cell_size,
            "y": row * cell_size,
            "width": cell_size,
            "height": cell_size,
            "color": SELECTED_OUTLINE,
            "line_width": 4,
        })

    for piece_view in snapshot.pieces:
        x, y = piece_view["pixel"]
        label = _piece_label(piece_view["color"], piece_view["kind"])
        instructions.append({
            "type": "text",
            "label": label,
            "x": x + cell_size / 2,
            "y": y + cell_size / 2,
            "color": "#000000" if piece_view["color"] == "white" else "#ffffff",
        })

    if snapshot.game_over:
        instructions.append({
            "type": "text",
            "label": "GAME OVER",
            "x": (snapshot.board_width * cell_size) / 2,
            "y": (snapshot.board_height * cell_size) / 2,
            "color": GAME_OVER_TEXT_COLOR,
        })

    return instructions


def _piece_label(color, kind):
    """תווית טקסטואלית פשוטה לכלי, למשל 'wK' או 'bQ'."""
    color_char = "w" if color == "white" else "b"
    return f"{color_char}{kind}"