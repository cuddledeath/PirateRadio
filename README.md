# PirateRadio
PirateRadio: Turn your Pi Zero into a dedicated, networked audio appliance. Drag-and-drop music via Samba, enjoy auto-scaling album art on the IPS display, and control it all with a beer-ware licensed Python core.

Pirate Radio Jukebox

A headless, networked music appliance designed for the Raspberry Pi Zero and the Pimoroni Pirate Audio DAC. This project turns your Pi into a dedicated shuffle-player that supports album art, physical button controls, and a wireless Samba share for easy music management.
Features

    Plug and Play: Automatically starts playing music on boot.

    Recursive Shuffle: Scans all subdirectories in your Music folder.

    State-Aware Playback: Dedicated pause logic ensures the jukebox does not skip to the next song when you hit pause.

    Album Art Support: Displays .jpg or .png files found in song folders, fitted perfectly to the 240x240 screen.

    Networked: Drag-and-drop music management via Samba (SMB).

    Physical Controls: Volume, Skip, and Play/Pause via onboard buttons.

    Safe Shutdown: Avoid SD card corruption with a hardware button combo (Vol+ and Vol-).

    Custom Branding: Supports a custom logo.png boot splash.

Installation
1. Hardware Requirements

    Raspberry Pi Zero (W, WH, or 2W)

    Pimoroni Pirate Audio DAC (3W, Line-out, or Headphone)

    MicroSD Card with Raspberry Pi OS (Lite recommended)

2. System Dependencies

Install the required Python libraries and networking tools:
Bash

sudo apt update
sudo apt install python3-pygame python3-st7789 python3-pil python3-gpiozero samba wsdd -y

3. Setup Music Share

Configure Samba to allow wireless file transfers:

    mkdir -p /home/pirate/Music

    Add the following to the end of /etc/samba/smb.conf:

Ini, TOML

[Music]
   path = /home/pirate/Music
   browseable = yes
   read only = no
   guest ok = yes
   public = yes
   writable = yes
   force user = pirate

    Restart Samba: sudo systemctl restart smbd

4. Deploy the Script

Place pirate_player.py into /home/pirate/.
5. Enable Auto-Start

Create a systemd service to ensure the jukebox runs at boot:

    Create the file: sudo nano /etc/systemd/system/pirate-player.service

    Paste the service configuration:

Ini, TOML

[Unit]
Description=Pirate Audio Player
After=sound.target network.target smbd.service

[Service]
ExecStart=/usr/bin/python3 /home/pirate/pirate_player.py
WorkingDirectory=/home/pirate
Restart=always
User=pirate

[Install]
WantedBy=multi-user.target

    Enable it: sudo systemctl enable --now pirate-player.service

Controls
Button	Label	Function
A	Top-Left	Volume Up (+5%)
B	Bottom-Left	Volume Down (-5%)
X	Top-Right	Skip to Next Random Song
Y	Bottom-Right	Toggle Play / Pause
A + B	Left Side	Hold 3s for Safe Shutdown
Library Organization

For the best experience, organize your music as follows:

    Music/logo.png: (Optional) 240x240 image shown at boot.

    Music/Artist/Album/: Drop your MP3s here.

    Music/Artist/Album/cover.jpg: Drop a square image here to show album art.

License

THE CUDDLEDEATH BEER-WARE LICENSE (Revision 42):
As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return. - Cuddledeath
