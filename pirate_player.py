"""
----------------------------------------------------------------------------
"THE CUDDLEDEATH BEER-WARE LICENSE" (Revision 42):
As long as you retain this notice you can do whatever you want with this 
stuff. If we meet some day, and you think this stuff is worth it, you can 
buy me a beer in return. - Cuddledeath
----------------------------------------------------------------------------
"""

import os
import random
import time
import st7789
from gpiozero import Button
from pygame import mixer
from PIL import Image, ImageDraw
from subprocess import call

# --- Configuration ---
MUSIC_PATH = "/home/pirate/Music"
LOGO_PATH = os.path.join(MUSIC_PATH, "logo.png")
WIDTH, HEIGHT = 240, 240

# --- Hardware Setup ---
disp = st7789.ST7789(
    port=0, cs=1, dc=9, backlight=13, 
    rotation=90, spi_speed_hz=80000000
)
disp.begin()

# Buttons: X=Next, Y=Pause, A=Vol+, B=Vol-
btn_next = Button(16)
btn_pause = Button(24)
btn_vup = Button(5)
btn_vdn = Button(6)

# --- State & Audio Setup ---
mixer.init()
vol = 0.7
is_paused = False  # Track if the user manually paused the music
mixer.music.set_volume(vol)
current_song_name = "None"
current_folder = ""

# --- Boot Splash ---
if os.path.exists(LOGO_PATH):
    try:
        logo_img = Image.open(LOGO_PATH).convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        disp.display(logo_img)
        time.sleep(3)
    except: pass
else:
    img = Image.new('RGB', (WIDTH, HEIGHT), (0,0,0))
    ImageDraw.Draw(img).text((80, 110), "STARTING...", (255,255,255))
    disp.display(img)
    time.sleep(1)

def update_ui(title, folder_path, status="Playing"):
    """ Updates the LCD with album art and track info. """
    art_path = next((os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f.lower() != "logo.png"), None)
    try:
        if art_path:
            img = Image.open(art_path).convert('RGB')
            img.thumbnail((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
            bg = Image.new('RGB', (WIDTH, HEIGHT), (0,0,0))
            bg.paste(img, ((WIDTH - img.width)//2, (HEIGHT - img.height)//2))
            img = bg
        else: 
            img = Image.new('RGB', (WIDTH, HEIGHT), (30, 0, 60))
    except: 
        img = Image.new('RGB', (WIDTH, HEIGHT), (20, 20, 20))

    draw = ImageDraw.Draw(img, 'RGBA')
    draw.rectangle([0, HEIGHT-70, WIDTH, HEIGHT], fill=(0, 0, 0, 180))
    draw.text((10, HEIGHT-60), f"{status}:", (200, 200, 200))
    draw.text((10, HEIGHT-45), title[:22], (255, 255, 255))
    draw.text((10, HEIGHT-20), f"Vol: {int(vol*100)}%", (0, 255, 0))
    disp.display(img)

def play_random():
    """ Picks a random song and resets the pause state. """
    global current_song_name, current_folder, is_paused
    is_paused = False # Reset pause state so new song plays immediately
    songs = [os.path.join(r, f) for r, d, fs in os.walk(MUSIC_PATH) for f in fs if f.lower().endswith(('.mp3', '.wav'))]
    
    if songs:
        path = random.choice(songs)
        current_song_name, current_folder = os.path.basename(path), os.path.dirname(path)
        try:
            mixer.music.load(path)
            mixer.music.play()
            update_ui(current_song_name, current_folder)
        except:
            play_random()

def toggle_pause():
    """ Properly handles the pause state to prevent the main loop from skipping songs. """
    global is_paused
    if is_paused:
        mixer.music.unpause()
        is_paused = False
        update_ui(current_song_name, current_folder, "Playing")
    else:
        mixer.music.pause()
        is_paused = True
        update_ui(current_song_name, current_folder, "Paused")

def adj_vol(n):
    """ Adjusts volume and updates the UI indicator. """
    global vol
    vol = max(0, min(1, vol + n))
    mixer.music.set_volume(vol)
    status = "Paused" if is_paused else "Playing"
    update_ui(current_song_name, current_folder, status)

# --- Button Handlers ---
btn_next.when_pressed = play_random
btn_pause.when_pressed = toggle_pause
btn_vup.when_pressed = lambda: adj_vol(0.05)
btn_vdn.when_pressed = lambda: adj_vol(-0.05)

# --- Main Runtime Loop ---
play_random()



while True:
    # 1. Safe Shutdown: Hold Vol Up + Vol Down for 3 seconds
    if btn_vup.is_pressed and btn_vdn.is_pressed:
        start = time.time()
        while btn_vup.is_pressed and btn_vdn.is_pressed:
            if time.time() - start > 3:
                img = Image.new('RGB', (WIDTH, HEIGHT), (255, 0, 0))
                ImageDraw.Draw(img).text((70, 110), "SHUTTING DOWN...", (255,255,255))
                disp.display(img)
                time.sleep(2)
                call("sudo shutdown -h now", shell=True)
            time.sleep(0.1)
    
    # 2. Auto-play Logic: 
    # Only pick a new song if the current one is finished AND we haven't manually paused.
    if not mixer.music.get_busy() and not is_paused: 
        play_random()
    
    time.sleep(0.5)
