import time
import threading
import XInput

class GamepadListener:
    def __init__(self, on_dpad_right=None, on_dpad_left=None):
        self.on_dpad_right = on_dpad_right
        self.on_dpad_left = on_dpad_left
        self.running = False
        self.thread = None
        
        # Estado anterior dos botoes para detectar o "click" (pressionamento unico)
        self.last_dpad_right = False
        self.last_dpad_left = False

    def start(self):
        if not XInput.get_connected()[0]:
            print("Nenhum controle de Xbox conectado. O listener continuara tentando...")

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _loop(self):
        while self.running:
            # Pega o estado do controle 0
            state = XInput.get_state(0)
            if state:
                buttons = XInput.get_button_values(state)
                
                # Botoes direcionais: DPAD_RIGHT e DPAD_LEFT
                dpad_right = buttons.get('DPAD_RIGHT', False)
                dpad_left = buttons.get('DPAD_LEFT', False)
                
                # Detectar apenas o momento em que aperta (edge detection)
                if dpad_right and not self.last_dpad_right:
                    if self.on_dpad_right:
                        self.on_dpad_right()
                        
                if dpad_left and not self.last_dpad_left:
                    if self.on_dpad_left:
                        self.on_dpad_left()
                        
                self.last_dpad_right = dpad_right
                self.last_dpad_left = dpad_left
                
            time.sleep(0.05) # Loop rapido mas sem estressar a CPU
