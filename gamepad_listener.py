import time
import threading
import XInput

class GamepadListener:
    def __init__(self, on_dpad_right=None, on_dpad_left=None):
        self.on_dpad_right = on_dpad_right
        self.on_dpad_left = on_dpad_left
        self.running = False
        self.thread = None
        
        # Previous button state to detect single clicks (edge detection)
        self.last_dpad_right = False
        self.last_dpad_left = False

    def start(self):
        if not XInput.get_connected()[0]:
            print("No Xbox controller connected. Listener will keep trying...")

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _loop(self):
        while self.running:
            # Get state for controller 0
            state = XInput.get_state(0)
            if state:
                buttons = XInput.get_button_values(state)
                
                # Directional buttons: DPAD_RIGHT and DPAD_LEFT
                dpad_right = buttons.get('DPAD_RIGHT', False)
                dpad_left = buttons.get('DPAD_LEFT', False)
                
                # Edge detection (only trigger on the exact moment the button is pressed)
                if dpad_right and not self.last_dpad_right:
                    if self.on_dpad_right:
                        self.on_dpad_right()
                        
                if dpad_left and not self.last_dpad_left:
                    if self.on_dpad_left:
                        self.on_dpad_left()
                        
                self.last_dpad_right = dpad_right
                self.last_dpad_left = dpad_left
                
            time.sleep(0.05) # Fast loop without stressing the CPU
