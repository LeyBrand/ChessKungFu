"""
STUB NOTICE - see api/game_api.py for context. Interface inferred from
ScoreTracker._on_piece_captured / MoveLogTracker._on_move_made, which
subscribe to named events and receive kwargs.
"""


class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_name, callback):
        self._subscribers.setdefault(event_name, []).append(callback)

    def publish(self, event_name, **kwargs):
        for callback in self._subscribers.get(event_name, []):
            callback(**kwargs)
