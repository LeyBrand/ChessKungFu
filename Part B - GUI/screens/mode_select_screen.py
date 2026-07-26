import cv2
import numpy as np

WINDOW_NAME = "Chess Game"
CANVAS_SIZE = (300, 700)


class ModeSelectScreen:
    """Blocking screen after login. Returns 'play', 'room', or None (quit)."""

    def run(self):
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_GUI_NORMAL)
        while True:
            canvas = np.full((*CANVAS_SIZE, 3), 245, dtype=np.uint8)
            cv2.putText(canvas, "P - Play (find opponent)", (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2)
            cv2.putText(canvas, "R - Room (create/join by ID)", (30, 170),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2)
            cv2.putText(canvas, "Esc - Quit", (30, 220),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (40, 40, 40), 2)
            cv2.imshow(WINDOW_NAME, canvas)

            key = cv2.waitKey(30)
            if key == 27:
                cv2.destroyWindow(WINDOW_NAME)
                return None
            if key in (ord('p'), ord('P')):
                cv2.destroyWindow(WINDOW_NAME)
                return "play"
            if key in (ord('r'), ord('R')):
                cv2.destroyWindow(WINDOW_NAME)
                return "room"