from __future__ import annotations

import pathlib

import cv2
import numpy as np

class Img:
    def __init__(self):
        self.img = None

    def read(self, path: str | pathlib.Path,
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = cv2.INTER_AREA) -> "Img":
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size is not None:
            target_w, target_h = size
            h, w = self.img.shape[:2]

            if keep_aspect:
                scale = min(target_w / w, target_h / h)
                new_w, new_h = int(w * scale), int(h * scale)
            else:
                new_w, new_h = target_w, target_h

            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)

        return self

    def draw_on(self, other_img, x, y):
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        if self.img.shape[2] != other_img.img.shape[2]:
            if self.img.shape[2] == 3 and other_img.img.shape[2] == 4:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2BGRA)
            elif self.img.shape[2] == 4 and other_img.img.shape[2] == 3:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGRA2BGR)

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if y + h > H or x + w > W:
            raise ValueError("Logo does not fit at the specified position.")

        roi = other_img.img[y:y + h, x:x + w]

        if self.img.shape[2] == 4:
            b, g, r, a = cv2.split(self.img)
            mask = a / 255.0
            for c in range(3):
                roi[..., c] = (1 - mask) * roi[..., c] + mask * self.img[..., c]
        else:
            other_img.img[y:y + h, x:x + w] = self.img

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)

    def show(self):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow("Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def copy(self) -> "Img":
        clone = Img()
        clone.img = self.img.copy()
        return clone

    def draw_rect(self, pt1, pt2, color, thickness=2):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.rectangle(self.img, pt1, pt2, color, thickness)
        return self

    def create_window(self, window_name: str) -> None:
        cv2.namedWindow(window_name, cv2.WINDOW_GUI_NORMAL)

    def set_mouse_callback(self, window_name: str, on_left_click=None, on_right_click=None) -> None:
        def _cv2_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN and on_left_click is not None:
                on_left_click(x, y)
            elif event == cv2.EVENT_RBUTTONDOWN and on_right_click is not None:
                on_right_click(x, y)

        cv2.setMouseCallback(window_name, _cv2_callback)

    def render(self, window_name: str, wait_ms: int = 1) -> bool:
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow(window_name, self.img)
        key = cv2.waitKey(wait_ms) & 0xFF
        return key != ord('q')

    def close_window(self, window_name: str) -> None:
        cv2.destroyWindow(window_name)

    def with_side_panels(self, left_width: int, right_width: int, bg_color) -> "Img":
        if self.img is None:
            raise ValueError("Image not loaded.")

        h, w, channels = self.img.shape
        color = tuple(bg_color)
        if channels == 4 and len(color) == 3:
            color = (*color, 255)

        parts = []
        if left_width > 0:
            left_panel = np.zeros((h, left_width, channels), dtype=self.img.dtype)
            left_panel[:] = color
            parts.append(left_panel)

        parts.append(self.img)

        if right_width > 0:
            right_panel = np.zeros((h, right_width, channels), dtype=self.img.dtype)
            right_panel[:] = color
            parts.append(right_panel)

        combined = Img()
        combined.img = np.hstack(parts)
        return combined

    @property
    def width(self) -> int:
        if self.img is None:
            raise ValueError("Image not loaded.")
        return self.img.shape[1]
    @property
    def height(self) -> int:
        if self.img is None:
            raise ValueError("Image not loaded.")
        return self.img.shape[0]

    def text_size(self, txt, font_size, thickness=1):
        (w, h), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, font_size, thickness)
        return w, h
