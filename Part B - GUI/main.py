from input_handler import MouseObserver
from display_manager import DisplayManager

def handle_click(x, y):
    print(f"Clicked at coordinates: ({x}, {y})")

def main():
    mouse_observer = MouseObserver()
    display = DisplayManager(window_name="Chess Game")

    mouse_observer.subscribe(handle_click)

    display.setup_mouse_callback(mouse_observer.get_callback())

    print("Displaying window. Click on the window or press 'q' to quit.")
    while True:
        display.render()

        if display.should_close():
            break

    display.close()

if __name__ == "__main__":
    main()