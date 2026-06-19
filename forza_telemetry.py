import socket
import struct
import threading

class ForzaTelemetry:
    def __init__(self, port=5300):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            # Bind to localhost to listen for Forza packets
            self.sock.bind(('127.0.0.1', self.port))
            # Set a 2-second timeout so we can detect if the game closed or telemetry is off
            self.sock.settimeout(2.0)
            print(f"Telemetry listener started on port {self.port}")
        except Exception as e:
            print(f"Telemetry bind error: {e}")
            
        # We default to True. If telemetry is off, the overlay will still work normally.
        # Once telemetry connects, this will accurately reflect the game state.
        self.is_race_on = True 
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        if self.thread:
            self.thread.join(timeout=1.0)

    def _loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                if len(data) >= 4:
                    # The very first 4 bytes of Forza Telemetry is a 32-bit integer for IsRaceOn
                    # 1 = Driving / In Game
                    # 0 = Paused / Map / Menu
                    is_race_on_flag = struct.unpack('<i', data[0:4])[0]
                    self.is_race_on = (is_race_on_flag == 1)
            except socket.timeout:
                # If we stop receiving packets for 2 seconds, assume game closed or telemetry is off
                self.is_race_on = True 
            except Exception:
                pass
