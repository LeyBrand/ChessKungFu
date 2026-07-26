import cv2
import numpy as np

WINDOW_NAME = "Chess Game"
CANVAS_SIZE = (300, 700)


class WaitingScreen:
    """Blocking screen shown after sending PLAY. Returns (room_id, color)
    on MATCH_FOUND, or None if the search failed/was cancelled."""

    def __init__(self, bridge):
        self.bridge = bridge

    def run(self):
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_GUI_NORMAL)
        self.bridge.send({"type": "PLAY"})

        message = "Searching for an opponent..."
        while True:
            canvas = np.full((*CANVAS_SIZE, 3), 245, dtype=np.uint8)
            cv2.putText(canvas, message, (30, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
            cv2.imshow(WINDOW_NAME, canvas)

            key = cv2.waitKey(30)
            if key == 27:
                self.bridge.send({"type": "CANCEL_SEEK"})
                cv2.destroyWindow(WINDOW_NAME)
                return None

            for msg in self.bridge.poll():
                if msg["type"] == "MATCH_FOUND":
                    cv2.destroyWindow(WINDOW_NAME)
                    return msg["room_id"], msg["color"]
                elif msg["type"] == "MATCH_NOT_FOUND":
                    message = "No opponent found. Press Esc to give up, or wait..."
                else:
                    self.bridge.incoming.put(msg)