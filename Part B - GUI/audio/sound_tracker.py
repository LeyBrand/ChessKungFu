class SoundTracker:
    SOUND_MAP = {
        "MOVE_MADE": "move.wav",
        "PIECE_CAPTURED": "capture.wav",
        "GAME_STARTED": "game_start.wav",
        "GAME_OVER": "game_over.wav",
    }

    def __init__(self, event_bus=None, sound_player=None):
        self._sound_player = sound_player

        if event_bus is not None:
            for event_name, filename in self.SOUND_MAP.items():
                event_bus.subscribe(event_name, self._make_handler(filename))

    def _make_handler(self, filename):
        def handler(**kwargs):
            if self._sound_player is not None:
                self._sound_player.play(filename)
        return handler