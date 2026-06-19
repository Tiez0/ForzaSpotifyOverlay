import tkinter as tk
import threading
import time
import requests
import os
import subprocess

class OverlayUI:
    def __init__(self):
        # WINDOW 1: For the Album Cover only (Will be 100% Solid)
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        self.transparent_color = '#000001'
        self.root.wm_attributes('-transparentcolor', self.transparent_color)
        self.root.configure(bg=self.transparent_color)
        self.root.attributes('-alpha', 0.0)

        self.img_canvas = tk.Canvas(self.root, width=500, height=250, bg=self.transparent_color, highlightthickness=0)
        self.img_canvas.pack(fill="both", expand=True)

        # WINDOW 2: For the Text Boxes only (Will be 85% Translucent)
        self.text_win = tk.Toplevel(self.root)
        self.text_win.overrideredirect(True)
        self.text_win.attributes('-topmost', True)
        self.text_win.wm_attributes('-transparentcolor', self.transparent_color)
        self.text_win.configure(bg=self.transparent_color)
        self.text_win.attributes('-alpha', 0.0)

        self.txt_canvas = tk.Canvas(self.text_win, width=500, height=250, bg=self.transparent_color, highlightthickness=0)
        self.txt_canvas.pack(fill="both", expand=True)

        self.box_bg = '#4f4f4f'
        self.font_family = "Franklin Gothic Demi Cond" 
        
        self.image_item = None
        self.track_box = []
        self.artist_box = []
        
        self.track_text = self.txt_canvas.create_text(30, 160, text="", font=(self.font_family, 18), fill="#ffdd00", anchor="w")
        self.artist_text = self.txt_canvas.create_text(30, 205, text="", font=(self.font_family, 16), fill="white", anchor="w")

        self.txt_canvas.tag_raise(self.track_text)
        self.txt_canvas.tag_raise(self.artist_text)

        screen_height = self.root.winfo_screenheight()
        window_width = 500
        window_height = 250
        x = 50 
        y = screen_height - 650 
        
        # Both windows are stacked perfectly at the exact same position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.text_win.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.hide_timer = None
        self.is_running = True
        self.photo = None

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, color):
        ids = []
        ids.append(self.txt_canvas.create_oval(x1, y1, x1+2*r, y1+2*r, outline=color, fill=color))
        ids.append(self.txt_canvas.create_oval(x2-2*r, y1, x2, y1+2*r, outline=color, fill=color))
        ids.append(self.txt_canvas.create_oval(x1, y2-2*r, x1+2*r, y2, outline=color, fill=color))
        ids.append(self.txt_canvas.create_oval(x2-2*r, y2-2*r, x2, y2, outline=color, fill=color))
        ids.append(self.txt_canvas.create_rectangle(x1+r, y1, x2-r, y2, outline=color, fill=color))
        ids.append(self.txt_canvas.create_rectangle(x1, y1+r, x2, y2-r, outline=color, fill=color))
        return ids

    def _convert_jpg_to_rounded_png(self, jpg_path, png_path):
        ps_cmd = f'''
        Add-Type -AssemblyName System.Drawing;
        $src = [System.Drawing.Image]::FromFile("{jpg_path}");
        $bmp = New-Object System.Drawing.Bitmap(120, 120);
        $g = [System.Drawing.Graphics]::FromImage($bmp);
        $g.Clear([System.Drawing.Color]::Transparent);
        $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias;
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;
        $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality;
        $path = New-Object System.Drawing.Drawing2D.GraphicsPath;
        $r = 16;
        $path.AddArc(0, 0, $r, $r, 180, 90);
        $path.AddArc(120 - $r, 0, $r, $r, 270, 90);
        $path.AddArc(120 - $r, 120 - $r, $r, $r, 0, 90);
        $path.AddArc(0, 120 - $r, $r, $r, 90, 90);
        $path.CloseFigure();
        $g.SetClip($path);
        $g.DrawImage($src, 0, 0, 120, 120);
        $bmp.Save("{png_path}", [System.Drawing.Imaging.ImageFormat]::Png);
        $g.Dispose();
        $bmp.Dispose();
        $src.Dispose();
        '''
        subprocess.run(["powershell", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)

    def _truncate_text(self, text, max_length):
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text

    def show_track(self, track_info):
        if not track_info:
            return
            
        name = self._truncate_text(track_info['name'], 30)
        artist = self._truncate_text(track_info['artist'], 35)
            
        self.txt_canvas.itemconfig(self.track_text, text=name)
        self.txt_canvas.itemconfig(self.artist_text, text=artist)
        
        for item in self.track_box + self.artist_box:
            self.txt_canvas.delete(item)
            
        bbox_track = self.txt_canvas.bbox(self.track_text)
        bbox_artist = self.txt_canvas.bbox(self.artist_text)
        
        padding_x = 10
        padding_y = 6
        self.track_box = self._draw_rounded_rect(bbox_track[0]-padding_x, bbox_track[1]-padding_y, bbox_track[2]+padding_x, bbox_track[3]+padding_y, 8, self.box_bg)
        self.artist_box = self._draw_rounded_rect(bbox_artist[0]-padding_x, bbox_artist[1]-padding_y, bbox_artist[2]+padding_x, bbox_artist[3]+padding_y, 8, self.box_bg)
        
        for item in self.track_box + self.artist_box:
            self.txt_canvas.tag_lower(item)
            
        if self.image_item:
            self.img_canvas.delete(self.image_item)
            
        if track_info.get('image_url'):
            try:
                response = requests.get(track_info['image_url'])
                jpg_path = "temp_cover.jpg"
                png_path = "temp_cover.png"
                
                with open(jpg_path, 'wb') as f:
                    f.write(response.content)
                    
                self._convert_jpg_to_rounded_png(os.path.abspath(jpg_path), os.path.abspath(png_path))
                
                if os.path.exists(png_path):
                    self.photo = tk.PhotoImage(file=png_path)
                    self.image_item = self.img_canvas.create_image(20, 10, anchor="nw", image=self.photo)
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Image window is solid, text window is translucent
        self.root.attributes('-alpha', 1.0) 
        self.text_win.attributes('-alpha', 0.85) 
        
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
            
        self.hide_timer = self.root.after(4000, self.hide_window)

    def hide_window(self):
        self.root.attributes('-alpha', 0.0)
        self.text_win.attributes('-alpha', 0.0)

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
        self.text_win.destroy()
        self.root.destroy()
