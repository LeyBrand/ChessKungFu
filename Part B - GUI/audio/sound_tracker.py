class SoundTracker:
    SOUND_MAP = {
        "MOVE_MADE": "move.wav",
        "PIECE_CAPTURED": "capture.wav",
        "GAME_STARTED": "game_start.wav",
        "GAME_ENDED": "game_end.wav"
    }

    def __init__(self, event_bus = None, sound_player = None):
        self._sound_player = sound_player
        if event_bus is not None:
            for event_name in self.SOUND_MAP:
                event_bus.subscribe(event_name, self._make_handler(event_name))


    def _make_handler(self, event_name):
        def handler(**kwargs):
            self.play(event_name)
        return handler
    
    def play(self, event_name):
        filename = self.SOUND_MAP.get(event_name)
        if filename and self._sound_player is not None:
            self._sound_player.play(filename)
