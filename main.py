import time
import subprocess
import os
import json
import psutil

from spotify_controller import SpotifyController
from gamepad_listener import GamepadListener
from overlay_ui import OverlayUI

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar config.json: {e}")
        return {}

def is_process_running(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            return True
    return False

def main():
    print("Iniciando Forza Spotify Overlay...")
    config = load_config()
    
    forza_path = config.get("FORZA_EXECUTABLE_PATH", "")
    
    # Inicia o Forza caso nao esteja rodando
    if forza_path and os.path.exists(forza_path):
        forza_exe_name = os.path.basename(forza_path)
        if not is_process_running(forza_exe_name):
            print(f"Iniciando o jogo: {forza_path}")
            try:
                subprocess.Popen([forza_path])
            except Exception as e:
                print(f"Erro ao iniciar o Forza: {e}")
        else:
            print("Forza ja esta em execucao.")
    else:
        print("Caminho do Forza nao configurado ou nao encontrado. Ignorando auto-start do jogo.")

    print("Conectando ao Spotify...")
    spotify = SpotifyController()
    
    print("Inicializando Overlay UI...")
    overlay = OverlayUI()

    def on_right():
        print("D-PAD Right pressionado -> Pular Musica")
        if spotify.next_track():
            time.sleep(0.5) # Aguarda o Spotify atualizar o status
            track_info = spotify.get_current_track_info()
            overlay.show_track(track_info)

    def on_left():
        print("D-PAD Left pressionado -> Voltar Musica")
        if spotify.previous_track():
            time.sleep(0.5) # Aguarda o Spotify atualizar o status
            track_info = spotify.get_current_track_info()
            overlay.show_track(track_info)

    print("Inicializando Leitor de Controle Xbox...")
    gamepad = GamepadListener(on_dpad_right=on_right, on_dpad_left=on_left)
    gamepad.start()

    print("Overlay rodando! Pressione D-PAD Direita/Esquerda para trocar a musica.")
    
    try:
        # Tkinter precisa rodar na thread principal
        overlay.root.mainloop()
    except KeyboardInterrupt:
        print("Encerrando...")
    finally:
        gamepad.stop()

if __name__ == "__main__":
    main()
