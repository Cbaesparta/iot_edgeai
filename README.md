# Jetson Camera Auto-Run (No Login Needed)

Yes, this is possible.

With the setup below, Jetson will:

- boot normally
- wait for camera device
- start AI detection backend automatically
- start dashboard automatically
- run without user login

## What You Have

- Jetson Orin
- USB camera (Logitech)

That is enough for a LAN-only smart surveillance pipeline.

## One-Time Setup on Jetson

Run these commands on Jetson inside the project directory.

```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv mosquitto mosquitto-clients
python3 -m pip install -r requirements.txt
chmod +x scripts/install_autostart.sh
sudo bash scripts/install_autostart.sh
```

## What install_autostart.sh Does

- creates and installs systemd services:
  - jetson-ai-backend.service
  - jetson-ai-dashboard.service
- enables mosquitto broker
- enables both services at boot
- starts services immediately
- waits for /dev/video0 before backend start

## Verify Services

```bash
systemctl status jetson-ai-backend.service
systemctl status jetson-ai-dashboard.service
```

## Access from Phone/Laptop (Same WiFi)

Find Jetson IP:

```bash
hostname -I
```

Open dashboard:

```text
http://JETSON_IP:8501
```

Raw API/stream endpoints:

- http://JETSON_IP:5000/video
- http://JETSON_IP:5000/api/status
- http://JETSON_IP:5000/api/detections
- http://JETSON_IP:5000/api/alerts

## Important Clarification About "Bypass Everything"

- No-login auto-start: yes (implemented via systemd).
- No dashboard auth/login: currently yes (local network only).
- Internet bypass: yes (LAN only).

If you need tighter security later, add local auth or router-level isolation.

## Camera Plug/Unplug Behavior

- On boot: backend waits for camera for up to 120s.
- If camera read fails repeatedly: app attempts camera reopen.
- If service crashes: systemd restarts it automatically.

## Optional: Start Only When Camera Is Plugged

If you want strict hot-plug trigger (start exactly when USB camera is inserted), we can add a udev rule next.

## Jetson as WiFi Hotspot (Phone and Laptop Connect Directly)

You can make Jetson broadcast its own WiFi and view everything without a separate router.

1) One-time hotspot setup:

```bash
chmod +x scripts/setup_hotspot.sh scripts/disable_hotspot.sh
sudo bash scripts/setup_hotspot.sh JetsonCamNet Jetson1234 wlan0
```

2) Connect phone and laptop to WiFi SSID:

- SSID: JetsonCamNet
- Password: Jetson1234

3) Open on phone/laptop browser:

- Dashboard: http://10.42.0.1:8501
- Stream: http://10.42.0.1:5000/video

4) If your AP IP is different, check it:

```bash
ip -4 addr show wlan0
```

5) Disable hotspot autoconnect later (optional):

```bash
sudo bash scripts/disable_hotspot.sh
```

Notes:

- setup_hotspot.sh enables autoconnect, so hotspot comes back after reboot.
- Backend and dashboard services still auto-start from systemd.
- Some USB WiFi chipsets cannot do client+AP at the same time; hotspot mode may disconnect Jetson from existing WiFi.
