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
import smbus
from gpiozero import Button
from pygame import mixer
from PIL import Image, ImageDraw
from subprocess import call

# --- Configuration & Hardware Setup ---
MUSIC_PATH = "/home/pirate/Music"
LOGO_PATH = os.path.join(MUSIC_PATH, "logo.png")
WIDTH, HEIGHT = 240, 240

# PiSugar 3 Hardware Constants
I2C_BUS = smbus.SMBus(1)
BAT_ADDR = 0x75
REG_BAT = 0x40  # Verified register for your hardware

# Display Setup
disp = st7789.ST7789(port=0, cs=1, dc=9, backlight=13, rotation=90, spi_speed_hz=80000000)
disp.begin()

# Button Mapping (Pirate Audio Standard)
btn_next, btn_pause = Button(16), Button(24)
btn_vup, btn_vdn = Button(5), Button(6)

# --- State & Audio Initialization ---
mixer.init()
vol, is_paused = 0.7, False
mixer.music.set_volume(vol)
current_song_name, current_folder = "None", ""

# --- Boot Splash ---
if os.path.exists(LOGO_PATH):
    try:
        logo_img = Image.open(LOGO_PATH).convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        disp.display(logo_img)
        time.sleep(3)
    except: pass
else:
    img = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))
    ImageDraw.Draw(img).text((80, 110), "STARTING...", (255, 255, 255))
    disp.display(img)
    time.sleep(1)

def update_ui(title, folder_path, status="Playing"):
    """ Updates the LCD with album art, track info, and battery status. """
    art_path = next((os.path.join(folder_path, f) for f in os.listdir(folder_path) 
                    if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f.lower() != "logo.png"), None)
    try:
        if art_path:
            img = Image.open(art_path).convert('RGB')
            img.thumbnail((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
            bg = Image.new('RGB', (WIDTH, HEIGHT), (0,0,0))
            bg.paste(img, ((WIDTH - img.width)//2, (HEIGHT - img.height)//2))
            img = bg
        else: img = Image.new('RGB', (WIDTH, HEIGHT), (30, 0, 60)) # Dark Purple fallback
    except: img = Image.new('RGB', (WIDTH, HEIGHT), (20, 20, 20))

    draw = ImageDraw.Draw(img, 'RGBA')
    # Semi-transparent footer for readability
    draw.rectangle([0, HEIGHT-70, WIDTH, HEIGHT], fill=(0, 0, 0, 180))
    
    # Left side: Status and Track Name
    draw.text((10, HEIGHT-60), f"{status}:", (200, 200, 200))
    draw.text((10, HEIGHT-45), title[:22], (255, 255, 255))
    
    # Bottom Left: Volume
    draw.text((10, HEIGHT-20), f"Vol: {int(vol*100)}%", (0, 255, 0))

    # --- Battery Indicator (Bottom Right) ---
    try:
        level = I2C_BUS.read_byte_data(BAT_ADDR, REG_BAT)
        level = min(level, 100) # Ensure it doesn't exceed 100%
        bat_color = (0, 255, 0) if level > 20 else (255, 0, 0)
        draw.text((175, HEIGHT-20), f"Bat: {level}%", bat_color)
    except:
        pass # Battery detached or communication error

    disp.display(img)

def play_random():
    global current_song_name, current_folder, is_paused
    is_paused = False
    songs = [os.path.join(r, f) for r, d, fs in os.walk(MUSIC_PATH) for f in fs if f.lower().endswith(('.mp3', '.wav'))]
    if songs:
        path = random.choice(songs)
        current_song_name, current_folder = os.path.basename(path), os.path.dirname(path)
        mixer.music.load(path)
        mixer.music.play()
        update_ui(current_song_name, current_folder)

def toggle_pause():
    global is_paused
    if is_paused:
        mixer.music.unpause()
        is_paused = False
        update_ui(current_song_name, current_folder, "Playing")
    else:
        mixer.music.pause()
        is_paused = True
        update_ui(current_song_name, current_folder, "Paused")

# --- Button Logic ---
btn_next.when_pressed = play_random
btn_pause.when_pressed = toggle_pause
btn_vup.when_pressed = lambda: (globals().update(vol=min(1, vol+0.05)), mixer.music.set_volume(vol), update_ui(current_song_name, current_folder, "Paused" if is_paused else "Playing"))
btn_vdn.when_pressed = lambda: (globals().update(vol=max(0, vol-0.05)), mixer.music.set_volume(vol), update_ui(current_song_name, current_folder, "Paused" if is_paused else "Playing"))

# --- Main Runtime Loop ---
play_random()
while True:
    # Safe Shutdown: Hold Volume Up + Volume Down for 3 seconds
    if btn_vup.is_pressed and btn_vdn.is_pressed:
        start = time.time()
        while btn_vup.is_pressed and btn_vdn.is_pressed:
            if time.time() - start > 3:
                # Flash red before shutdown
                img_off = Image.new('RGB', (WIDTH, HEIGHT), (150, 0, 0))
                ImageDraw.Draw(img_off).text((70, 110), "SHUTTING DOWN...", (255, 255, 255))
                disp.display(img_off)
                time.sleep(1)
                call("sudo shutdown -h now", shell=True)
            time.sleep(0.1)
    
    # Check if song ended (and not paused) to play next
    if not mixer.music.get_busy() and not is_paused:
        play_random()
    
    time.sleep(0.5)
