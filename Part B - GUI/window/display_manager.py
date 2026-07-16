import cv2

class DisplayManager:
    def __init__(self, window_name = "Chess Game"):
        self.window_name = window_name
        self.current_frame = None
        cv2.namedWindow(self.window_name)

    def setup_mouse_callback(self, callback_function):
        cv2.setMouseCallback(self.window_name, callback_function)

    def update_frame(self, frame):
        self.current_frame = frame

    def render(self):
        if self.current_frame is not None:
            cv2.imshow(self.window_name, self.current_frame)
    
    def should_close(self):
        return cv2.waitKey(1) & 0xFF == ord('q')
    
    def close(self):
        cv2.destroyWindow(self.window_name)
