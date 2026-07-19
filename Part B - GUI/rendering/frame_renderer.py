from mapping.graphics_mapper import cell_to_pixel, piece_pixel
from rendering.sprite_library import SpriteLibrary
from scoring.score_tracker import ScoreTracker
from scoring.move_log_tracker import MoveLogTracker

SELECTED_OUTLINE = (51, 51, 255)
GAME_OVER_COLOR = (0, 0, 255)

SPRITE_SCALE = 0.8
SIDEBAR_WIDTH = 240
MAX_ROWS_FALLBACK = 20

PANEL_BG_COLOR = (190, 183, 188)
HEADER_BG_COLOR = (255, 255, 255)
HEADER_TEXT_COLOR = (0, 0, 0)
COL_HEADER_BG_COLOR = (255, 255, 255)
ROW_BASE_COLOR = (255, 255, 255)
ROW_ALT_COLOR = (222, 218, 222)
TEXT_COLOR = (40, 40, 40)

HEADER_HEIGHT = 36
SCORE_HEIGHT = 24
COLUMN_HEADER_HEIGHT = 26
ROW_HEIGHT = 24
TIME_COL_WIDTH = 100
MOVE_COL_WIDTH = 90
SCORE_TEXT_COLOR = (0, 90, 0)

_sprite_library = SpriteLibrary()
_score_tracker = ScoreTracker()
_move_log_tracker = MoveLogTracker()

def init_scoring(event_bus):
    global _score_tracker
    _score_tracker = ScoreTracker(event_bus = event_bus)

def init_move_log(event_bus):
    global _move_log_tracker
    _move_log_tracker = MoveLogTracker(event_bus=event_bus)

def render_frame(base_img, board_snapshot, cell_size):
    board_frame = base_img.copy()
    elapsed_seconds = board_snapshot["timestamp_ms"] / 1000.0

    _draw_selection(board_frame, board_snapshot["selected_cell"], cell_size)
    _draw_pieces(board_frame, board_snapshot["pieces"], cell_size, elapsed_seconds)

    if board_snapshot["is_game_over"]:
        board_frame.put_text("GAME OVER", cell_size * 2, cell_size * 4, 1.2, GAME_OVER_COLOR, 3)
    frame = board_frame.with_side_panels(SIDEBAR_WIDTH, SIDEBAR_WIDTH, PANEL_BG_COLOR)

    scores = _score_tracker.get_scores()
    white_moves, black_moves = _split_history_by_color(_move_log_tracker.get_moves())
    
    _draw_side_panel(frame, x_start=0, panel_width=SIDEBAR_WIDTH,
                      title="Black", score=scores["black"], moves=black_moves)
    _draw_side_panel(frame, x_start=SIDEBAR_WIDTH + board_frame.width, panel_width=SIDEBAR_WIDTH,
                      title="White", score=scores["white"], moves=white_moves)

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
            continue
        x, y = piece_pixel(piece["position"], piece["motion"], cell_size)
        state = "move" if piece["motion"] is not None else "idle"
        sprite = _sprite_library.get_frame(
            piece["kind"], piece["color"], state, elapsed_seconds,
            size=(sprite_size, sprite_size),
        )
        sprite.draw_on(frame, int(x) + offset, int(y) + offset)


def _split_history_by_color(move_history):
    white_moves = [m for m in move_history if m.get("color") == "white"]
    black_moves = [m for m in move_history if m.get("color") == "black"]
    return white_moves, black_moves


def _cell_name(col, row):
    return f"{chr(ord('a') + col)}{8 - row}"


def _format_time(time_ms):
    total_seconds = time_ms / 1000.0
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:06.3f}"


def _format_move_san(move):
    dest = _cell_name(*move["to"])
    kind = move.get("kind", "P")
    captured = move.get("captured", False)

    if move.get("is_jump"):
        prefix = "" if kind == "P" else kind
        symbol = "x" if captured else "^"
        return f"{prefix}{symbol}{dest}"

    if kind == "P":
        if captured:
            from_col, _ = move["from"]
            origin_file = chr(ord('a') + from_col)
            return f"{origin_file}x{dest}"
        return dest

    return f"{kind}{'x' if captured else ''}{dest}"


def _draw_side_panel(frame, x_start, panel_width, title, score, moves):
    margin = 10
    box_x1 = x_start + margin
    box_x2 = x_start + panel_width - margin

    frame.draw_rect((x_start, 0), (x_start + panel_width, frame.height), PANEL_BG_COLOR, -1)

    # Title header
    header_y1 = 10
    header_y2 = header_y1 + HEADER_HEIGHT
    frame.draw_rect((box_x1, header_y1), (box_x2, header_y2), HEADER_BG_COLOR, -1)
    title_w, title_h = frame.text_size(title, 0.7, 2)
    title_x = box_x1 + max(0, (box_x2 - box_x1 - title_w) // 2)
    title_y = header_y1 + (HEADER_HEIGHT + title_h) // 2
    frame.put_text(title, title_x, title_y, 0.7, HEADER_TEXT_COLOR, 2)

    # Score line
    score_text = f"Score: {score}"
    score_y1 = header_y2 + 6
    score_w, score_h = frame.text_size(score_text, 0.55, 1)
    score_x = box_x1 + max(0, (box_x2 - box_x1 - score_w) // 2)
    frame.put_text(score_text, score_x, score_y1 + score_h, 0.55, SCORE_TEXT_COLOR, 1)

    # Column headers
    table_y1 = score_y1 + SCORE_HEIGHT
    table_x1 = box_x1
    table_width = min(TIME_COL_WIDTH + MOVE_COL_WIDTH, box_x2 - box_x1)
    time_col_x = table_x1 + 8
    move_col_x = table_x1 + TIME_COL_WIDTH + 8

    frame.draw_rect((table_x1, table_y1), (table_x1 + table_width, table_y1 + COLUMN_HEADER_HEIGHT),
                     COL_HEADER_BG_COLOR, -1)
    frame.put_text("Time", time_col_x, table_y1 + 18, 0.5, TEXT_COLOR, 1)
    frame.put_text("Move", move_col_x, table_y1 + 18, 0.5, TEXT_COLOR, 1)

    # Rows
    rows_top = table_y1 + COLUMN_HEADER_HEIGHT
    max_rows = max(0, (frame.height - rows_top) // ROW_HEIGHT)
    recent = moves[-max_rows:] if max_rows > 0 else moves[-MAX_ROWS_FALLBACK:]

    row_y = rows_top
    for i, move in enumerate(recent):
        row_color = ROW_ALT_COLOR if i % 2 == 1 else ROW_BASE_COLOR
        frame.draw_rect((table_x1, row_y), (table_x1 + table_width, row_y + ROW_HEIGHT), row_color, -1)

        frame.put_text(_format_time(move["time_ms"]), time_col_x, row_y + 17, 0.4, TEXT_COLOR, 1)
        frame.put_text(_format_move_san(move), move_col_x, row_y + 17, 0.45, TEXT_COLOR, 1)

        row_y += ROW_HEIGHT