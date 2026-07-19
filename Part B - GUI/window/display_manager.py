from data.img import Img


class DisplayManager:
    def __init__(self, window_name="Chess Game"):
        self.window_name = window_name
        self.current_frame = None
        self._window = Img()
        self._window.create_window(self.window_name)
        self._running = True

    def setup_mouse_callback(self, on_left_click=None, on_right_click=None):
        self._window.set_mouse_callback(self.window_name, on_left_click, on_right_click)

    def update_frame(self, frame_img):
        self.current_frame = frame_img

    def render(self):
        if self.current_frame is not None:
            self._running = self.current_frame.render(self.window_name)

    def should_close(self):
        return not self._running

    def close(self):
        self._window.close_window(self.window_name)
