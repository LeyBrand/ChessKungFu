import os

DEFAULT_SOUNDS_ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "sounds")


def _winsound_play(path):
    import winsound  # imported lazily - keeps this module importable on non-Windows
    winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)


class SoundPlayer:
    def __init__(self, root=DEFAULT_SOUNDS_ROOT, play_func=_winsound_play):
        self.root = root
        self._play_func = play_func

    def play(self, filename):
        path = os.path.join(self.root, filename)

        if not os.path.isfile(path):
            print(f"[SoundPlayer] Warning: sound file not found: {path}")
            return

        self._play_func(path)