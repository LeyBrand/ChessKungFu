import cv2

class MouseObserver:
    def __init__(self):
        self.subscribers = {"left": [], "right": []}

    def subscribe(self, callback, button="left"):
        self.subscribers[button].append(callback)

    def notify(self, x, y, button):
        for callback in self.subscribers[button]:
            callback(x, y)

    def get_callback(self):
        def callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.notify(x, y, "left")
            elif event == cv2.EVENT_RBUTTONDOWN:
                self.notify(x, y, "right")
        return callback