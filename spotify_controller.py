import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

class SpotifyController:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.config["SPOTIPY_CLIENT_ID"],
            client_secret=self.config["SPOTIPY_CLIENT_SECRET"],
            redirect_uri=self.config["SPOTIPY_REDIRECT_URI"],
            scope="user-modify-playback-state user-read-playback-state"
        ))

    def next_track(self):
        try:
            self.sp.next_track()
            return True
        except Exception as e:
            print(f"Error skipping track: {e}")
            return False

    def previous_track(self):
        try:
            self.sp.previous_track()
            return True
        except Exception as e:
            print(f"Error going to previous track: {e}")
            return False

    def get_current_track_info(self):
        try:
            current = self.sp.current_playback()
            if current and current.get('item'):
                track = current['item']
                return {
                    "name": track['name'],
                    "artist": ", ".join([artist['name'] for artist in track['artists']]),
                    # Fetch medium size image (usually 300x300) for better quality when resizing
                    "image_url": track['album']['images'][1]['url'] if len(track['album']['images']) > 1 else (track['album']['images'][0]['url'] if track['album']['images'] else None)
                }
            return None
        except Exception as e:
            print(f"Error fetching current track: {e}")
            return None
