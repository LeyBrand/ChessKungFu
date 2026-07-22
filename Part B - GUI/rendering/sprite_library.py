import os
import json

from data.img import Img
from constants import Color

DEFAULT_SPRITES_ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "pieces_mine")


class SpriteLibrary:
    def __init__(self, root=DEFAULT_SPRITES_ROOT):
        self.root = root
        self._frames_cache = {}
        self._config_cache = {}

    def get_frame(self, kind, color, state, elapsed_seconds, size):
        frames = self._load_frames(kind, color, state, size)
        config = self._load_config(kind, color, state)

        fps = config["graphics"]["frames_per_sec"]
        is_loop = config["graphics"]["is_loop"]

        frame_index = int(elapsed_seconds * fps)
        if is_loop:
            frame_index %= len(frames)
        else:
            frame_index = min(frame_index, len(frames) - 1)

        return frames[frame_index]

    def _state_dir(self, kind, color, state):
        code = self._piece_code(kind, color)
        return os.path.join(self.root, code, "states", state)

    def _load_frames(self, kind, color, state, size):
        key = (self._piece_code(kind, color), state, size)
        if key not in self._frames_cache:
            sprites_dir = os.path.join(self._state_dir(kind, color, state), "sprites")
            filenames = sorted(
                f for f in os.listdir(sprites_dir) if f.lower().endswith(".png")
            )
            frames = [Img().read(os.path.join(sprites_dir, fname), size=size) for fname in filenames]
            self._frames_cache[key] = frames
        return self._frames_cache[key]

    def _load_config(self, kind, color, state):
        key = (self._piece_code(kind, color), state)
        if key not in self._config_cache:
            config_path = os.path.join(self._state_dir(kind, color, state), "config.json")
            with open(config_path, encoding="utf-8") as f:
                self._config_cache[key] = json.load(f)
        return self._config_cache[key]

    @staticmethod
    def _piece_code(kind, color):
        color_char = "W" if color == Color.WHITE else "B"
        return f"{kind}{color_char}"
