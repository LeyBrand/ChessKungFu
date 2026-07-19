class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_name, callback):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name, **payload):
        callbacks = self._subscribers.get(event_name, [])
        for callback in callbacks:
            callback(**payload)
