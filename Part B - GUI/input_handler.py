import cv2

class MouseObserver:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def notify(self, x, y):
        for callback in self.subscribers:
            callback(x, y)

    def get_callback(self):
        def callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.notify(x, y)
        return callback
    
