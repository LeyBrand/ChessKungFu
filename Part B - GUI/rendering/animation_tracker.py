class AnimationTracker:
    def __init__(self, event_bus=None):
        self.active_animation = None
        self.triggered_at_ms = None

        if event_bus is not None:
            event_bus.subscribe("GAME_STARTED", self._on_game_started)
            event_bus.subscribe("GAME_ENDED", self._on_game_ended)

    def _on_game_started(self, **kwargs):
        self.active_animation = "start"
        self.triggered_at_ms = kwargs.get("time_ms", 0)

    def _on_game_ended(self, **kwargs):
        self.active_animation = "end"
        self.triggered_at_ms = kwargs.get("time_ms", 0)

    def clear(self):
        self.active_animation = None
        self.triggered_at_ms = None
)