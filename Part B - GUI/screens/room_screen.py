import cv2
import numpy as np

from constants import MessageType

WINDOW_NAME = "Chess Game"
CANVAS_SIZE = (300, 700)

STAGE_CHOOSE = "choose"
STAGE_TYPE_ID = "type_id"
STAGE_WAITING = "waiting"
STAGE_SHOW_ID = "show_id"
STAGE_ERROR = "error"


class RoomScreen:
    """Blocking screen for Create/Join by room ID. Returns (room_id, color)
    on success (color may be None for a viewer), or None if cancelled."""

    def __init__(self, bridge):
        self.bridge = bridge
        self.stage = STAGE_CHOOSE
        self.room_id_input = ""
        self.created_room_id = None
        self.error_message = None

    def run(self):
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_GUI_NORMAL)
        while True:
            self._draw()
            key = cv2.waitKey(30)

            if key == 27:  # Esc
                cv2.destroyWindow(WINDOW_NAME)
                return None

            if self.stage == STAGE_CHOOSE:
                if key in (ord('c'), ord('C')):
                    self.bridge.send({"type": MessageType.CREATE_ROOM})
                    self.stage = STAGE_WAITING
                elif key in (ord('j'), ord('J')):
                    self.stage = STAGE_TYPE_ID

            elif self.stage == STAGE_TYPE_ID:
                if key == 13:  # Enter
                    if self.room_id_input:
                        self.bridge.send({"type": MessageType.JOIN_ROOM, "room_id": self.room_id_input})
                        self.stage = STAGE_WAITING
                elif key == 8:  # Backspace
                    self.room_id_input = self.room_id_input[:-1]
                elif 32 <= key <= 126:
                    self.room_id_input += chr(key)

            elif self.stage == STAGE_WAITING:
                for msg in self.bridge.poll():
                    if msg["type"] == MessageType.ROOM_CREATED:
                        self.created_room_id = msg["room_id"]
                        self.stage = STAGE_SHOW_ID
                    elif msg["type"] == MessageType.ROOM_JOINED:
                        cv2.destroyWindow(WINDOW_NAME)
                        return msg["room_id"], msg["color"]
                    elif msg["type"] == MessageType.ERROR:
                        self.error_message = msg["reason"]
                        self.stage = STAGE_ERROR
                    else:
                        self.bridge.incoming.put(msg)

            elif self.stage == STAGE_SHOW_ID:
                if key != -1:  # any key
                    cv2.destroyWindow(WINDOW_NAME)
                    return self.created_room_id, "white"

            elif self.stage == STAGE_ERROR:
                if key == 13:
                    self.stage = STAGE_CHOOSE
                    self.room_id_input = ""
                    self.error_message = None

    def _draw(self):
        canvas = np.full((*CANVAS_SIZE, 3), 245, dtype=np.uint8)

        if self.stage == STAGE_CHOOSE:
            cv2.putText(canvas, "C - Create room", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2)
            cv2.putText(canvas, "J - Join room by ID", (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2)
        elif self.stage == STAGE_TYPE_ID:
            cv2.putText(canvas, f"Room ID: {self.room_id_input}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            cv2.putText(canvas, "Enter to join", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        elif self.stage == STAGE_WAITING:
            cv2.putText(canvas, "Waiting for server...", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 100, 0), 1)
        elif self.stage == STAGE_SHOW_ID:
            cv2.putText(canvas, "Room created! Share this ID:", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            cv2.putText(canvas, self.created_room_id, (30, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 90, 0), 1)
            cv2.putText(canvas, "Press any key to continue", (30, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        elif self.stage == STAGE_ERROR:
            cv2.putText(canvas, f"Error: {self.error_message}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1)
            cv2.putText(canvas, "Enter to try again", (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        cv2.imshow(WINDOW_NAME, canvas)