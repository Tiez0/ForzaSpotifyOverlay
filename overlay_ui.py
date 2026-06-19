import tkinter as tk
import threading
import time
import requests
import os
import subprocess

class OverlayUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True) # Remove bordas
        self.root.attributes('-topmost', True) # Sempre por cima
        
        # Cor que sera invisivel (Chroma Key perfeito)
        self.transparent_color = '#000001'
        self.root.wm_attributes('-transparentcolor', self.transparent_color)
        self.root.configure(bg=self.transparent_color)
        self.root.attributes('-alpha', 0.0) # Começa invisível

        # Container principal 100% invisivel
        self.main_frame = tk.Frame(self.root, bg=self.transparent_color)
        self.main_frame.pack(side="left")

        # Container da imagem (Capa do Album) - visivel
        self.image_label = tk.Label(self.main_frame, bg=self.transparent_color)
        self.image_label.pack(side="left", padx=(0, 10))

        # Container do Texto 100% invisivel
        self.text_frame = tk.Frame(self.main_frame, bg=self.transparent_color)
        self.text_frame.pack(side="left", fill="y", expand=True)

        # Textos estilizados igual Forza
        # Titulo da Radio (Amarelo estilizado)
        self.title_label = tk.Label(self.text_frame, text="HORIZON\nSPOTIFY", font=("Impact", 18, "italic"), fg="#eaff00", bg=self.transparent_color, justify="left")
        self.title_label.pack(anchor="w")

        # Nome da Musica (Amarelo)
        self.track_label = tk.Label(self.text_frame, text="Nome da Música", font=("Segoe UI", 16, "bold"), fg="#ffea00", bg=self.transparent_color)
        self.track_label.pack(anchor="w", pady=(5, 0))

        # Artista (Branco)
        self.artist_label = tk.Label(self.text_frame, text="Artista", font=("Segoe UI", 14), fg="white", bg=self.transparent_color)
        self.artist_label.pack(anchor="w")

        # Posicionamento: Lado Esquerdo inferiror (Padrão Forza das imagens)
        screen_height = self.root.winfo_screenheight()
        window_width = 500
        window_height = 180
        x = 50 # Bem encostado na esquerda
        y = screen_height - 300
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.hide_timer = None
        self.is_running = True
        self.photo = None

    def _convert_jpg_to_png(self, jpg_path, png_path):
        # Truque sensacional para converter imagem sem precisar instalar compiladores C++ (PIL)
        ps_cmd = f'''
        Add-Type -AssemblyName System.Drawing;
        $img = [System.Drawing.Image]::FromFile("{jpg_path}");
        $img.Save("{png_path}", [System.Drawing.Imaging.ImageFormat]::Png);
        '''
        subprocess.run(["powershell", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)

    def show_track(self, track_info):
        if not track_info:
            return
            
        self.track_label.config(text=track_info['name'])
        self.artist_label.config(text=track_info['artist'])
        
        # Baixar e exibir a capa do album (em formato 64x64 retornado pelo controller)
        if track_info.get('image_url'):
            try:
                response = requests.get(track_info['image_url'])
                jpg_path = "temp_cover.jpg"
                png_path = "temp_cover.png"
                
                with open(jpg_path, 'wb') as f:
                    f.write(response.content)
                    
                # Converter para PNG (formato nativo que o Tkinter aceita sem Pillow)
                self._convert_jpg_to_png(os.path.abspath(jpg_path), os.path.abspath(png_path))
                
                if os.path.exists(png_path):
                    self.photo = tk.PhotoImage(file=png_path)
                    self.image_label.config(image=self.photo)
            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")
        
        # Faz a janela aparecer instantaneamente (sem aquela caixa preta feia!)
        self.root.attributes('-alpha', 1.0)
        
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
            
        # Esconder após 4 segundos
        self.hide_timer = self.root.after(4000, self.hide_window)

    def hide_window(self):
        self.root.attributes('-alpha', 0.0)

    def update_loop(self):
        while self.is_running:
            self.root.update()
            time.sleep(0.01)

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.update_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False
        self.root.destroy()
