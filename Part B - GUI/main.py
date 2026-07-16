import sys, os, time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PART_A_DIR = os.path.join(CURRENT_DIR, "..", "Part A - bussines_logic")
sys.path.insert(0, os.path.abspath(PART_A_DIR))

from data.img import Img
from input_handler import MouseObserver
from display_manager import DisplayManager
from image_view import render_frame
from board_snapshot_adapter import build_board_snapshot
from app import build_app
from data_io.board_parser import parse_board


STARTING_BOARD_TEXT = """
bR bN bB bQ bK bB bN bR
bP bP bP bP bP bP bP bP
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
.  .  .  .  .  .  .  .
wP wP wP wP wP wP wP wP
wR wN wB wQ wK wB wN wR
"""


def main():
    display = DisplayManager(window_name="Chess Game")
    base_img = Img().read("data/board.png").img

    board = parse_board(STARTING_BOARD_TEXT)
    state, engine, controller = build_app(board)

    def handle_click(x, y):
        controller.handle({"name": "click", "args": [str(x), str(y)]}, board)

    def handle_jump(x, y):
        controller.handle({"name": "jump", "args": [str(x), str(y)]}, board)

    mouse_observer = MouseObserver()
    mouse_observer.subscribe(handle_click, "left")
    mouse_observer.subscribe(handle_jump, "right")
    display.setup_mouse_callback(mouse_observer.get_callback())

    last_time = time.time()

    while True:
        now = time.time()
        elapsed_ms = (now - last_time) * 1000
        last_time = now

        engine.wait(elapsed_ms)

        engine_snapshot = engine.snapshot(selected_pos=controller.selected_pos)
        board_snapshot = build_board_snapshot(engine_snapshot)
        frame = render_frame(base_img, board_snapshot, cell_size=100)
        display.update_frame(frame)
        display.render()

        if display.should_close():
            break

    display.close()


if __name__ == "__main__":
    main()