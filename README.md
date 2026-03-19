# PirateRadio

This updated README.md now includes the PiSugar 3 hardware specifics, the direct I2C register configuration we discovered, and the "Externally Managed Environment" workaround for the battery library.
Pirate Radio Jukebox 🏴‍☠️📻

A headless, networked music appliance designed for the Raspberry Pi Zero and the Pimoroni Pirate Audio DAC. This project features recursive directory shuffling, automated album art display, and integrated battery monitoring for portable use.
## Hardware Requirements

   - Raspberry Pi Zero: (W, WH, or 2W)
   - Pimoroni Pirate Audio DAC: (3W, Line-out, or Headphone)
   - MicroSD Card: (Class 10 / A1 or A2 recommended)
   - PiSugar 3 (Optional): For portable power.
     Note: This project uses Direct I2C via Register 0x40 for battery telemetry.

## Installation
### 1. Enable I2C & Sound

   Ensure the hardware interfaces are active:
   Bash
   
   sudo raspi-config
   # Interface Options -> I2C -> Yes
   # Interface Options -> SPI -> Yes

### 2. System Dependencies
   
   Install the core libraries. Use the --break-system-packages flag if you are on a newer "Externally Managed" OS (Bookworm+):
   Bash
   
   sudo apt update
   sudo apt install python3-pygame python3-st7789 python3-pil python3-gpiozero python3-smbus i2c-tools samba wsdd -y
   pip3 install pisugar --break-system-packages

### 3. Permissions

   Ensure the pirate user can access the hardware bus:
   Bash
   
   sudo usermod -aG i2c pirate

### 4. Setup Music Share (Samba)

   Add this to the end of /etc/samba/smb.conf to drop music onto the Pi wirelessly:
   Ini, TOML
   
   ```
   [Music]
      path = /home/pirate/Music
      browseable = yes
      read only = no
      guest ok = yes
      public = yes
      writable = yes
      force user = pirate
   ```

## Controls & Interface

Button	Action	Function
A	Top-Left	Volume Up (+5%)
B	Bottom-Left	Volume Down (-5%)
X	Top-Right	Skip to Next Random Song
Y	Bottom-Right	Toggle Play / Pause
A + B	Hold 3s	Safe System Shutdown

## Display Features:

 - Album Art: Automatically looks for .jpg or .png in the current folder.
 - Battery Gauge: Live percentage in the bottom-right (Green > 20%, Red < 20%).
 - Status Overlay: Shows "Playing" or "Paused" with current track title.

## Service Configuration

   To make the jukebox start automatically on boot, create /etc/systemd/system/pirate-player.service:
   Ini, TOML
   
   ```
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
   ```

Enable it with: ```sudo systemctl enable --now pirate-player.service```

📜 License

THE CUDDLEDEATH BEER-WARE LICENSE (Revision 42):
As long as you retain this notice you can do whatever you want with this stuff. If we meet some day, and you think this stuff is worth it, you can buy me a beer in return. - Cuddledeath
