# 📸 Fotobox Pi

# 📸 SelfieStation – Raspberry Pi Fotobox

Die **Open Source Fotobox** für Hochzeiten, Geburtstage & Partys!  
Nimm Fotos auf, teile sie sofort im WLAN, und lass deine Gäste das Event rocken.  
**Für Raspberry Pi 4, Kamera-Modul v3 und Touchdisplay (1280x720, Querformat)**  
**Funktioniert mit physischen Buttons UND Touchscreen!**

---

## ✨ Features

- **Vollbild-Selfie-Fotobox** für 7"-Touchscreen (1280×720 Pixel)
- **Countdown mit PNG-Grafiken**
- **Touch und beliebig belegbare GPIO-Knöpfe** für Auslösen/Behalten/Neu machen
- **Automatische Galerie mit Download-Funktion** im lokalen WLAN (keine Cloud!)
- **Offline-Hotspot (WLAN)** als Gästeportal, optional mit Captive Portal
- **Bilder und Thumbnails werden automatisch erstellt und auf USB-Stick kopiert**
- **Vorschau zeigt immer das komplette Foto (nichts wird abgeschnitten!)**
- **Konfigurierbar über `config.ini`**
- **Sound nach der Aufnahme**

---

## 🛠️ Komponenten

- Raspberry Pi 4 (oder besser)
- Raspberry Pi Kamera Modul v3
- 7-Zoll-Touchscreen (1280×720, Querformat) (https://www.berrybase.de/raspberry-pi-touch-display-2)
- USB-Stick (zum Speichern der Bilder)
- Physische Taster (optional, z.B. Arcade-Buttons für Auslösen, Behalten, Neu machen)
- Lautsprecher (USB, 3.5mm oder HDMI)

---

## 🚀 Installation & Setup

### 1. System vorbereiten

```bash
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3-picamera2 python3-pygame python3-gpiozero python3-numpy python3-opencv python3-pil lighttpd hostapd dnsmasq
```

> Falls Fehlermeldungen bzgl. `numpy` oder `pygame` kommen, auch versuchen:
>
> ```bash
> sudo apt install libatlas-base-dev
> pip3 install opencv-python pillow pygame
> ```

### 2. Kamera aktivieren

```bash
sudo raspi-config
# Interfacing Options -> Kamera aktivieren -> Reboot!
```

### 3. Projekt-Ordnerstruktur

```text
fotobox/
  |-- fotobox6.py         # Das Hauptskript
  |-- config.ini          # Deine Konfigurationsdatei
  |-- static/
       |-- party.png
       |-- photo.png
       |-- check.png
       |-- back.png
       |-- kamera.wav
       |-- countdown/
             |-- 1.png
             |-- 2.png
             |-- 3.png
             |-- 4.png
             |-- 5.png
```

---

## ⚙️ Konfigurationsdatei (`config.ini`) Beispiel

```ini
[Fotobox]
event_titel = Fotobox 90. Geburtstag    # Event Namen einstellen
countdown_text = Lächeln!  # Text einstellen oder einfach lassen
countdown_seconds = 5 # Countdown kannst du nur kürzer machen, würde ich auf 5 lassen
header_text_ready = Mach dich bereit! # Text beim Fotomachen oben
footer_text_ready = Touch/Buzzer → Start # Text auf Startseite unten
footer_text_take = Touch/Buzzer → Foto aufnehmen # Text bei Fotomachen Seite
footer_text_keep = Behalten # Behalten Text
footer_text_new = Neu machen # Neumachen Text
flip_preview = true          # Vorschau gespiegelt
flip_save = false            # Optional gespeichertes Bild spiegeln

[Design]
top_bg = 30,30,30  # Background Design Oben
mid_bg = 50,50,50 # Background Design Mitte
footer_bg = 30,30,30 # Background Design unten
slideshow_frame_color = 255,215,0 # Startbildschirm bei der Slideshow die Rahmen Farbe
slideshow_shadow_color = 20,20,20 # Startbildschirm bei der Slideshow die Schatten Farbe

[Kamera]
foto_auflösung = 1920,1080 # FullHD Auflösung ich habe aber 4608,2592 (4608 × 2592 Pixel) genommen
preview_auflösung = 1280,720 # Vorschau Auflösung

[GPIO]
button_shoot = 22 # GPIO Button für Foto schießen, frei wählbar
button_keep = 23 # GPIO Button für Foto behalten, frei wählbar
button_new = 24 # GPIO Button für Foto neumachen, frei wählbar

[Sonstiges]
sound_path = static/kamera.wav # Kamera Sound in Wav Format
usb_ordner = /media/pi # Dort muss dein Raspberry Pi Benutzer rein
thumbnail_size = 320,180 # Thumbnail Größe
```

---

## 🖼️ Rechte für Bilder & Galerie setzen

```bash
sudo chown -R pi:www-data /var/www/html
sudo chmod -R 775 /var/www/html
sudo chown -R pi:pi ~/fotobox
sudo chmod -R 775 ~/fotobox
```

---

## 📡 WLAN-Hotspot & Offline-Galerie einrichten

### A) Hotspot installieren & aktivieren

```bash
sudo apt install hostapd dnsmasq
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
```

### B) Statische IP für wlan0

In `/etc/dhcpcd.conf` am Ende hinzufügen:

```ini
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

### C) `/etc/dnsmasq.conf` (neu anlegen)

```conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

### D) `/etc/hostapd/hostapd.conf` (neu anlegen)

```conf
interface=wlan0
driver=nl80211
ssid=Fotobox
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
```
*(Kein Passwort = offen für Gäste!)*

In `/etc/default/hostapd` ändern:

```bash
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

### E) Webserver installieren

```bash
sudo apt install lighttpd
sudo systemctl enable lighttpd
sudo systemctl start lighttpd
```

### F) Neustarten

```bash
sudo systemctl restart dhcpcd hostapd dnsmasq lighttpd
```

**Jetzt finden Gäste im WLAN „Fotobox“ die Galerie unter http://192.168.4.1**  


---

## ▶️ Fotobox starten

### A) Start-Skript anlegen
Wichtig /home/pi <-- muss euer Pfad hin wo Fotobox liegt

Datei: `start-fotobox.sh` im fotobox-Ordner:

```bash
#!/bin/bash
cd /home/pi/fotobox
python3 fotobox.py
```

Ausführbar machen:

```bash
chmod +x start-fotobox.sh
```

Starten:

```bash
./start-fotobox.sh
```

### B) Optional: Desktop-Verknüpfung

Wichtig /home/pi <-- muss euer Pfad hin wo Fotobox liegt

Datei: `~/Desktop/Fotobox.desktop`

```ini
[Desktop Entry]
Name=Fotobox
Comment=Startet das Fotobox-Programm
Exec=/home/pi/fotobox/start-fotobox.sh
Icon=/home/pi/fotobox/static/photo.png
Terminal=true
Type=Application
Categories=Utility;
```

Ausführbar machen:

```bash
chmod +x ~/Desktop/Fotobox.desktop
```

### C) Optional: Autostart
Wichtig /home/pi <-- muss euer Pfad hin wo Fotobox liegt

Eintragen in  
`~/.config/lxsession/LXDE-pi/autostart`  
am Ende der Datei:

```bash
@/home/pi/fotobox/start-fotobox.sh
```

---

## 🔌 Buttons anschließen

- Button wie in der `config.ini` an GPIO, eine Seite an GND.
- Pinout: https://pinout.xyz/
- Funktioniert mit Arcade-Button, Taster, etc.

---

## 🩺 Troubleshooting

**Kamera wird nicht gefunden**

```bash
libcamera-hello
```
(Kamera richtig gesteckt & in `raspi-config` aktiviert?)

**Kein Sound?**

```bash
aplay /usr/share/sounds/alsa/Front_Center.wav
```

**Webseite zeigt keine Bilder?**

- Rechte prüfen (siehe oben)
- Webserver neu starten

**Hotspot startet nicht?**

```bash
sudo systemctl status hostapd
```
- Meistens stimmt was in `/etc/dhcpcd.conf` oder `/etc/hostapd/hostapd.conf` nicht

---

## ✏️ Anpassungen und Weiterentwicklung

- **GPIOs, Farben, Texte:** in der `config.ini` ändern!
- **Countdown-Bilder:** PNGs in `static/countdown/` ersetzen!
- **Sound:** Soundfile als `static/kamera.wav` ablegen

---

## 📜 Lizenz

MIT License – Für private und kommerzielle Zwecke frei nutzbar.

---

## 💬 Support

Fragen, Wünsche, Bugs?  
Issue auf GitHub öffnen – oder mich direkt anschreiben! 😊

Das Skript ist komplett mit ChatGPT geschrieben. Dort könnt ihr auch Fragen stellen 😊

---

**Viel Spaß mit deiner eigenen Fotobox!**
