class MouseObserver:
    def __init__(self):
        self.subscribers = {"left": [], "right": []}

    def subscribe(self, callback, button="left"):
        self.subscribers[button].append(callback)

    def notify(self, x, y, button):
        for callback in self.subscribers[button]:
            callback(x, y)
