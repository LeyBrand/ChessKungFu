import time

from data.img import Img
from bridge.business_bridge import BusinessBridge
from controls.input_handler import MouseObserver
from window.display_manager import DisplayManager
from rendering.frame_renderer import render_frame


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

    bridge = BusinessBridge(STARTING_BOARD_TEXT)

    def handle_click(x, y):
        bridge.handle_click(x, y)

    def handle_jump(x, y):
        bridge.handle_jump(x, y)

    mouse_observer = MouseObserver()
    mouse_observer.subscribe(handle_click, "left")
    mouse_observer.subscribe(handle_jump, "right")
    display.setup_mouse_callback(mouse_observer.get_callback())

    last_time = time.time()

    while True:
        now = time.time()
        elapsed_ms = (now - last_time) * 1000
        last_time = now

        bridge.tick(elapsed_ms)

        board_snapshot = bridge.get_render_snapshot()
        frame = render_frame(base_img, board_snapshot, cell_size=100)
        display.update_frame(frame)
        display.render()

        if display.should_close():
            break

    display.close()


if __name__ == "__main__":
    main()
