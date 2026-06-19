import time
import subprocess
import os
import json
import psutil
import threading

from spotify_controller import SpotifyController
from gamepad_listener import GamepadListener
from overlay_ui import OverlayUI
from forza_telemetry import ForzaTelemetry

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config.json: {e}")
        return {}

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            return True
    return False

def main():
    print("Starting Forza Spotify Overlay...")
    config = load_config()
    
    forza_path = config.get("FORZA_EXECUTABLE_PATH", "")
    
    # Start Forza if it is not already running
    if forza_path and os.path.exists(forza_path):
        forza_exe_name = os.path.basename(forza_path)
        if not is_process_running(forza_exe_name):
            print(f"Starting the game: {forza_path}")
            try:
                subprocess.Popen([forza_path])
            except Exception as e:
                print(f"Error starting Forza: {e}")
        else:
            print("Forza is already running.")
    else:
        print("Forza path not configured or not found. Skipping game auto-start.")

    print("Connecting to Spotify...")
    spotify = SpotifyController()
    
    print("Initializing Overlay UI...")
    overlay = OverlayUI()

    print("Initializing Forza Telemetry Listener...")
    telemetry = ForzaTelemetry()
    telemetry.start()

    # Track ID state to prevent duplicate notifications
    last_track_id = None

    def update_track_if_changed():
        nonlocal last_track_id
        try:
            track_info = spotify.get_current_track_info()
            if track_info and track_info.get("id"):
                current_id = track_info["id"]
                if current_id != last_track_id:
                    last_track_id = current_id
                    # IMPORTANT: GUI updates must be scheduled on the main thread
                    overlay.root.after(0, overlay.show_track, track_info)
        except Exception as e:
            print(f"Error checking track: {e}")

    def poll_spotify():
        while True:
            update_track_if_changed()
            time.sleep(3) # Check every 3 seconds

    # Start background polling thread
    threading.Thread(target=poll_spotify, daemon=True).start()

    def on_right():
        if not telemetry.is_race_on:
            print("D-PAD Right ignored (Menu/Map is open)")
            return
            
        print("D-PAD Right pressed -> Skip Track")
        if spotify.next_track():
            time.sleep(0.5) # Wait for Spotify to update the playback status
            update_track_if_changed()

    def on_left():
        if not telemetry.is_race_on:
            print("D-PAD Left ignored (Menu/Map is open)")
            return
            
        print("D-PAD Left pressed -> Previous Track")
        if spotify.previous_track():
            time.sleep(0.5) # Wait for Spotify to update the playback status
            update_track_if_changed()

    print("Initializing Xbox Gamepad Listener...")
    gamepad = GamepadListener(on_dpad_right=on_right, on_dpad_left=on_left)
    gamepad.start()

    print("Overlay is running! Press D-PAD Right/Left to change tracks.")
    
    try:
        # Tkinter must run on the main thread
        overlay.root.mainloop()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        telemetry.stop()
        gamepad.stop()

if __name__ == "__main__":
    main()
