class AnimationTracker:
    def __init__(self, event_bus=None):
        self.active_animation = None  # "start" | "over" | None

        if event_bus is not None:
            event_bus.subscribe("GAME_STARTED", self._on_game_started)
            event_bus.subscribe("GAME_OVER", self._on_game_over)

    def _on_game_started(self, **kwargs):
        self.active_animation = "start"

    def _on_game_over(self, **kwargs):
        self.active_animation = "over"

    def clear(self):
        self.active_animation = None