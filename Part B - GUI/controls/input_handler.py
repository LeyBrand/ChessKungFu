"""
Pure pub/sub event dispatcher - no cv2 knowledge at all. Img now handles
translating raw cv2 mouse events into plain (x, y) calls, so this class
only needs to route those calls to whoever subscribed.
"""


class MouseObserver:
    def __init__(self):
        self.subscribers = {"left": [], "right": []}

    def subscribe(self, callback, button="left"):
        self.subscribers[button].append(callback)

    def notify(self, x, y, button):
        for callback in self.subscribers[button]:
            callback(x, y)
