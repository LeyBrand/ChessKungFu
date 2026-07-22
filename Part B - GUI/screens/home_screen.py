import queue

import cv2
import numpy as np

from network.login_client import login_async

WINDOW_NAME = "Chess Game"
CANVAS_SIZE = (400, 700)  # height, width

FIELD_USERNAME = "username"
FIELD_PASSWORD = "password"
STAGE_CONNECTING = "connecting"
STAGE_ERROR = "error"


class HomeScreen:
    """Blocking OpenCV login screen. Returns the logged-in username on
    success, or None if the user closed the window / gave up."""

    def __init__(self):
        self.username = ""
        self.password = ""
        self.stage = FIELD_USERNAME
        self.error_message = None
        self.result_queue = queue.Queue()

    def run(self):
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_GUI_NORMAL)

        while True:
            self._draw()
            key = cv2.waitKey(30)

            if key == 27:  # Esc
                cv2.destroyWindow(WINDOW_NAME)
                return None

            if self.stage == FIELD_USERNAME:
                self._handle_text_input(key, field="username")
            elif self.stage == FIELD_PASSWORD:
                self._handle_text_input(key, field="password")
            elif self.stage == STAGE_CONNECTING:
                try:
                    result = self.result_queue.get_nowait()
                except queue.Empty:
                    continue
                if result["ok"]:
                    cv2.destroyWindow(WINDOW_NAME)
                    return result["username"]
                else:
                    self.error_message = result["reason"]
                    self.stage = STAGE_ERROR
            elif self.stage == STAGE_ERROR:
                if key == 13:  # Enter - try again
                    self.username = ""
                    self.password = ""
                    self.error_message = None
                    self.stage = FIELD_USERNAME

    def _handle_text_input(self, key, field):
        if key == -1:
            return
        if key == 13:  # Enter
            if field == "username" and self.username:
                self.stage = FIELD_PASSWORD
            elif field == "password" and self.password:
                self.stage = STAGE_CONNECTING
                login_async(self.username, self.password, self.result_queue)
            return
        if key == 8:  # Backspace
            if field == "username":
                self.username = self.username[:-1]
            else:
                self.password = self.password[:-1]
            return
        if 32 <= key <= 126:  # printable ASCII
            char = chr(key)
            if field == "username":
                self.username += char
            else:
                self.password += char

    def _draw(self):
        canvas = np.full((*CANVAS_SIZE, 3), 245, dtype=np.uint8)

        cv2.putText(canvas, "KungFu Chess - Login", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2)

        cv2.putText(canvas, f"Username: {self.username}", (30, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

        masked = "*" * len(self.password)
        cv2.putText(canvas, f"Password: {masked}", (30, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)

        if self.stage == STAGE_CONNECTING:
            cv2.putText(canvas, "Connecting...", (30, 260),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 100, 0), 1)
        elif self.stage == STAGE_ERROR:
            cv2.putText(canvas, f"Error: {self.error_message}", (30, 260),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1)
            cv2.putText(canvas, "Press Enter to try again", (30, 300),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        cv2.imshow(WINDOW_NAME, canvas)