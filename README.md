# Fotobox Pi

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
- 7-Zoll-Touchscreen (1280×720, Querformat)
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

