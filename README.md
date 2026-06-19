<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg" width="200" alt="Spotify Logo">
  <h1>🏎️ Forza Horizon Spotify Overlay</h1>
  <p>A seamless, anti-cheat safe Spotify widget that mimics the native Forza Horizon radio UI.</p>
</div>

> [!WARNING]
> **Beta Version (v1.0-beta):** This project is currently in its early beta stage. You may encounter minor UI bugs or unexpected behavior. Feedback and issue reports are highly appreciated!

---

## ✨ Features

- **Native UI Replication**: Faithfully recreates the in-game Horizon Radio HUD using translucent dual-window rendering and the native "Franklin Gothic" font family.
- **Anti-Cheat Safe**: 100% external overlay. It does not inject DLLs or read game memory, ensuring absolutely zero ban risk online.
- **Gamepad Integration**: Listens to D-Pad inputs (Left/Right) via XInput to skip or rewind Spotify tracks just like changing radio stations in-game.
- **Smart Formatting**: Dynamically rounds album cover corners, crops long titles, and automatically adjusts layout.
- **Auto-Hide**: Fades out after 4 seconds of inactivity, just like the real game HUD.

## 🛠️ Prerequisites

1. **Python 3.x** installed on your Windows machine.
2. A **Spotify Developer Account** to get your API credentials.

## 🚀 Installation & Setup

### 1. Get your Spotify API Keys
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Click **Create an App**.
3. Set the **Redirect URI** to `http://127.0.0.1:8080`.
4. Copy your `Client ID` and `Client Secret`.

### 2. Clone the Repository
```bash
git clone https://github.com/Tiez0/ForzaSpotifyOverlay.git
cd ForzaSpotifyOverlay
```

### 3. Install Dependencies
```bash
pip install spotipy PyQt6 XInput-Python psutil requests
```

### 4. Configuration
1. Open the `config.json` file in the project folder.
2. Paste your `Client ID` and `Client Secret` into the respective fields.
3. Keep the `SPOTIPY_REDIRECT_URI` as `http://127.0.0.1:8080`.
4. Optionally, add the path to your Forza executable if you want the app to auto-launch.

```json
{
    "SPOTIPY_CLIENT_ID": "YOUR_CLIENT_ID_HERE",
    "SPOTIPY_CLIENT_SECRET": "YOUR_CLIENT_SECRET_HERE",
    "SPOTIPY_REDIRECT_URI": "http://127.0.0.1:8080",
    "FORZA_EXECUTABLE_PATH": "C:\\XboxGames\\Forza Horizon 5\\Content\\ForzaHorizon5.exe"
}
```

## 🎮 How to Use

1. Double-click the **`run.bat`** file (or run `python main.py` in your terminal).
2. The very first time you run it, your browser will open asking you to log into Spotify and authorize the app.
3. Open Forza Horizon.
4. Press **D-Pad Right** to skip to the next track, or **D-Pad Left** to go to the previous track.
5. Enjoy the seamless native UI appearing perfectly above your minimap!

## 🤝 Contributing
Pull requests are welcome! If you want to add new features like dynamic colors based on album art, feel free to submit a PR.

## 📝 License
This project is for educational and entertainment purposes. It is not affiliated with Playground Games, Xbox Game Studios, or Spotify.