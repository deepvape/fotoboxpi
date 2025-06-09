# Fotobox Pi

📸 SelfieStation – Raspberry Pi Fotobox
Die Open Source Fotobox für Hochzeiten, Geburtstage & Partys!
Nimm Fotos auf, teile sie sofort im WLAN, und lass deine Gäste das Event rocken.
Für Raspberry Pi 4, Kamera-Modul v3 und Touchdisplay.
Funktioniert mit physischen Buttons UND Touchscreen!

Features
Vollbild-Selfie-Fotobox für 7"-Touchscreen (1280×720 Pixel)

Countdown mit PNG-Grafiken

Touch und beliebig belegbare GPIO-Knöpfe für Auslösen/Behalten/Neu machen

Automatische Galerie mit Download-Funktion im lokalen WLAN (keine Cloud!)

Offline-Hotspot (WLAN) als Gästeportal, optional mit Captive Portal

Bilder und Thumbnails werden automatisch erstellt und auf USB-Stick kopiert

Vorschau zeigt immer das komplette Foto (nichts wird abgeschnitten!)

Konfigurierbar über config.ini

Sound nach der Aufnahme

1. Komponenten
Raspberry Pi 4 (oder besser)

Raspberry Pi Kamera Modul v3

7-Zoll-Touchscreen (1280×720, Querformat)

USB-Stick (zum Speichern der Bilder)

Physische Taster (optional, z.B. Arcade-Buttons für Auslösen, Behalten, Neu machen)

(Empfohlen: passives oder aktives Gehäuse mit Button-Löchern)

Lautsprecher (für Kamera-Sound, kann USB, 3.5mm oder HDMI sein)

2. Vorbereitungen
A) Betriebssystem & System updaten
bash
Kopieren
sudo apt update
sudo apt upgrade
B) Notwendige Pakete installieren
bash
Kopieren
sudo apt install python3 python3-pip python3-picamera2 python3-pygame python3-gpiozero python3-numpy python3-opencv python3-pil lighttpd hostapd dnsmasq
Optional (bei Fehlern):

bash
Kopieren
sudo apt install libatlas-base-dev
C) Python-Bibliotheken (manuell, falls nötig):
bash
Kopieren
pip3 install opencv-python pillow pygame
D) Kamera aktivieren (nur einmal nötig):
bash
Kopieren
sudo raspi-config
# Interfacing Options -> Kamera aktivieren -> Reboot!
3. Projektstruktur
text
Kopieren
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
Die Countdown-PNGs können z.B. aus großen Ziffern bestehen, die du selbst gestaltest.

4. Konfigurationsdatei (config.ini) Beispiel
ini
Kopieren
[Fotobox]
event_titel = Fotobox 90. Geburtstag
countdown_text = Lächeln!
countdown_seconds = 5
header_text_ready = Mach dich bereit!
footer_text_ready = Touch/Buzzer → Start
footer_text_take = Touch/Buzzer → Foto aufnehmen
footer_text_keep = Behalten
footer_text_new = Neu machen
flip_preview = true          # Vorschau gespiegelt
flip_save = false            # Optional gespeichertes Bild spiegeln

[Design]
top_bg = 30,30,30
mid_bg = 50,50,50
footer_bg = 30,30,30
slideshow_frame_color = 255,215,0
slideshow_shadow_color = 20,20,20

[Kamera]
foto_auflösung = 1920,1080
preview_auflösung = 1280,720

[GPIO]
button_shoot = 22
button_keep = 23
button_new = 24

[Sonstiges]
sound_path = static/kamera.wav
usb_ordner = /media/pi
thumbnail_size = 320,180
5. Rechte setzen
Die Fotobox, das Webverzeichnis, und USB-Ordner brauchen passende Rechte:

bash
Kopieren
sudo chown -R pi:www-data /var/www/html
sudo chmod -R 775 /var/www/html
sudo chown -R pi:pi ~/fotobox
sudo chmod -R 775 ~/fotobox
6. WLAN-Hotspot & Offline-Galerie einrichten
A) Hotspot installieren

bash
Kopieren
sudo apt install hostapd dnsmasq
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
B) Statische IP für wlan0

In /etc/dhcpcd.conf am Ende hinzufügen:

ini
Kopieren
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
C) /etc/dnsmasq.conf (neu anlegen):

conf
Kopieren
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
D) /etc/hostapd/hostapd.conf (neu anlegen):

conf
Kopieren
interface=wlan0
driver=nl80211
ssid=Fotobox
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
(Kein Passwort = offen für Gäste!)

In /etc/default/hostapd ändern:

ini
Kopieren
DAEMON_CONF="/etc/hostapd/hostapd.conf"
E) Webserver installieren

bash
Kopieren
sudo apt install lighttpd
sudo systemctl enable lighttpd
sudo systemctl start lighttpd
F) Neustarten:

bash
Kopieren
sudo systemctl restart dhcpcd hostapd dnsmasq lighttpd
Jetzt finden Gäste im WLAN „Fotobox“ die Galerie unter http://192.168.4.1
Optional: Captive Portal deaktivieren wie oben in der Anleitung.

7. Fotobox starten
A) Start-Skript anlegen
Datei: start-fotobox.sh (im fotobox-Ordner):

bash
Kopieren
#!/bin/bash
cd /home/pi/fotobox
python3 fotobox6.py
Mach es ausführbar:

bash
Kopieren
chmod +x start-fotobox.sh
Starte es per Doppelklick oder im Terminal mit:

bash
Kopieren
./start-fotobox.sh
B) Optional: Desktop-Verknüpfung
Datei: ~/Desktop/Fotobox.desktop

ini
Kopieren
[Desktop Entry]
Name=Fotobox
Comment=Startet das Fotobox-Programm
Exec=/home/pi/fotobox/start-fotobox.sh
Icon=/home/pi/fotobox/static/photo.png
Terminal=true
Type=Application
Categories=Utility;
Ausführbar machen:

bash
Kopieren
chmod +x ~/Desktop/Fotobox.desktop
C) Optional: Autostart nach Boot
Füge am Ende in
~/.config/lxsession/LXDE-pi/autostart
folgende Zeile ein:

swift
Kopieren
@/home/pi/fotobox/start-fotobox.sh
8. Tipp: Buttons anschließen
Button an GPIO wie in der config.ini.

Eine Seite an GPIO-Pin, eine Seite an GND.

Beispiel-Pinout: raspberrypi.pinout.xyz

Funktioniert mit beliebigen Tastern (Arcade, Klingel, …)

9. Troubleshooting
Fehler: Kamera wird nicht gefunden

Kamera-Modul im Pi korrekt gesteckt?

Mit libcamera-hello testen!

Kein Sound?

Ist ein Lautsprecher am Pi?

Funktioniert mit aplay /usr/share/sounds/alsa/Front_Center.wav?

Webseite zeigt keine Bilder?

Rechte prüfen! (Siehe Punkt 5)

Webserver neu starten

Hotspot startet nicht?

Prüfe sudo systemctl status hostapd

Meistens stimmt was in /etc/dhcpcd.conf oder /etc/hostapd/hostapd.conf nicht

10. Anpassungen und Weiterentwicklung
GPIOs, Farben, Texte: Einfach in der config.ini anpassen!

Bessere/andere Countdown-Bilder: PNGs in static/countdown/ ersetzen!

Eigenes Soundfile: als static/kamera.wav ablegen

Lizenz
Open Source (MIT) – Für private und kommerzielle Zwecke frei nutzbar!

Support
Fragen, Wünsche, Bugs?
Einfach ein Issue auf GitHub öffnen oder Patrick direkt anschreiben! 😊


