import sys
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.join(_CURRENT_DIR, "..")
if os.path.abspath(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, os.path.abspath(_ROOT_DIR))

import time

from data.img import Img
from controls.input_handler import MouseObserver
from window.display_manager import DisplayManager
from rendering.frame_renderer import render_frame, SIDEBAR_WIDTH, init_scoring, init_move_log
from network.network_bridge import NetworkBridge
from screens.home_screen import HomeScreen
from screens.waiting_screen import WaitingScreen
from screens.mode_select_screen import ModeSelectScreen
from screens.room_screen import RoomScreen
from constants import CELL_SIZE


def main():
    bridge = NetworkBridge()
    bridge.start()
    print("[main] bridge started")

    username = HomeScreen(bridge).run()
    print(f"[main] home screen done, username={username}")
    if username is None:
        return

    mode = ModeSelectScreen().run()
    print(f"[main] mode select screen done, mode={mode}")
    if mode is None:
        return
    
    if mode == "play":
        match = WaitingScreen(bridge).run()
    elif mode == "room":
        match = RoomScreen(bridge).run()

    print(f"[main] match screen done, match={match}")
    if match is None:
        return
    room_id, my_color = match

    print("[main] creating DisplayManager...")
    display = DisplayManager(window_name="Chess Game")
    print("[main] DisplayManager created")

    base_img = Img().read("data/board.png")
    print("[main] board image loaded")
    board_width_px = base_img.width

    latest_snapshot = None
    def handle_click(x, y):
        board_x = x - SIDEBAR_WIDTH
        if 0 <= board_x < board_width_px:
            bridge.send({"type": "MOVE", "room_id": room_id, "x": board_x, "y": y})
        
    def handle_jump(x, y):
        board_x = x - SIDEBAR_WIDTH
        if 0 <= board_x < board_width_px and 0 <= y < board_width_px:
            bridge.send({"type": "JUMP", "room_id": room_id, "x": board_x, "y": y})

    mouse_observer = MouseObserver()
    mouse_observer.subscribe(handle_click, "left")
    mouse_observer.subscribe(handle_jump, "right")

    display.setup_mouse_callback(on_left_click=lambda x, y: mouse_observer.notify(x, y, "left"), on_right_click=lambda x, y: mouse_observer.notify(x, y, "right"))

    print("[main] entering game loop")
    loop_count = 0
    while True:
        loop_count += 1
        if loop_count % 60 == 0:  # once every ~2 seconds
            print(f"[main] loop alive, snapshot_received={latest_snapshot is not None}")

        for msg in bridge.poll():
            print(f"[main] got message: {msg['type']}")
            if msg["type"] == "SNAPSHOT":
                latest_snapshot = msg["data"]

        if latest_snapshot is not None:
            frame = render_frame(base_img, latest_snapshot, cell_size=CELL_SIZE)
            display.update_frame(frame)
            display.render()

        if display.should_close():
            break

        time.sleep(0.03)

    display.close()


if __name__ == "__main__":
    main()