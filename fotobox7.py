import os
import pygame
import time
import shutil
import configparser
from picamera2 import Picamera2
from gpiozero import Button
from datetime import datetime
from PIL import Image
import numpy as np
import cv2

# ==== HARDCODED DISPLAY-GRÖSSE ====
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

# ==== CONFIG EINLESEN ====
def str2tuple(s):
    return tuple(int(x.strip()) for x in s.split(","))

config = configparser.ConfigParser()
config.read("config.ini")

# Fotobox
EVENT_TITEL = config["Fotobox"]["event_titel"]
COUNTDOWN_TEXT = config["Fotobox"]["countdown_text"]
COUNTDOWN_SECONDS = config["Fotobox"].getint("countdown_seconds")
HEADER_TEXT_READY = config["Fotobox"]["header_text_ready"]
FOOTER_TEXT_READY = config["Fotobox"]["footer_text_ready"]
FOOTER_TEXT_TAKE = config["Fotobox"]["footer_text_take"]
FOOTER_TEXT_KEEP = config["Fotobox"]["footer_text_keep"]
FOOTER_TEXT_NEW = config["Fotobox"]["footer_text_new"]
FLIP_PREVIEW = config["Fotobox"].getboolean("flip_preview", fallback=True)
FLIP_SAVE = config["Fotobox"].getboolean("flip_save", fallback=False)

# Design
TOP_BG = str2tuple(config["Design"]["top_bg"])
MID_BG = str2tuple(config["Design"]["mid_bg"])
FOOTER_BG = str2tuple(config["Design"]["footer_bg"])
SLIDESHOW_FRAME_COLOR = str2tuple(config["Design"]["slideshow_frame_color"])
SLIDESHOW_SHADOW_COLOR = str2tuple(config["Design"]["slideshow_shadow_color"])

# Kamera
FOTO_AUFLÖSUNG = str2tuple(config["Kamera"]["foto_auflösung"])
PREVIEW_AUFLÖSUNG = str2tuple(config["Kamera"]["preview_auflösung"])

# GPIO
GPIO_SHOOT = int(config["GPIO"]["button_shoot"])
GPIO_KEEP = int(config["GPIO"]["button_keep"])
GPIO_NEW = int(config["GPIO"]["button_new"])

# Sonstiges
SOUND_PATH = config["Sonstiges"]["sound_path"]
USB_ORDNER = config["Sonstiges"]["usb_ordner"]
THUMB_SIZE = str2tuple(config["Sonstiges"]["thumbnail_size"])

# Ordner
FOTO_ORDNER = "bilder"
THUMBNAIL_ORDNER = "thumbnails"
GALERIE_ORDNER = "galerie"
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)

# ==== INITIALISIERUNG ====
pygame.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)
font_big = pygame.font.SysFont("arial", 56, bold=True)
font_mid = pygame.font.SysFont("arial", 40)
font_footer = pygame.font.SysFont("arial", 36, bold=True)
button_shoot = Button(GPIO_SHOOT)
button_keep = Button(GPIO_KEEP)
button_new = Button(GPIO_NEW)

def load_icon(name, size=56):
    icon = pygame.image.load(os.path.join("static", f"{name}.png"))
    return pygame.transform.smoothscale(icon, (size, size))
icons = {
    "party": load_icon("party", 56),
    "photo": load_icon("photo", 56),
    "check": load_icon("check", 40),
    "back": load_icon("back", 40),
}

countdown_images = {}
for i in range(1, COUNTDOWN_SECONDS + 1):
    img = pygame.image.load(f"static/countdown/{i}.png")
    countdown_images[i] = pygame.transform.smoothscale(img, (200, 200))

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(
    main={"size": PREVIEW_AUFLÖSUNG, "format": "YUV420"}
)
capture_config = picam2.create_still_configuration(
    main={"size": FOTO_AUFLÖSUNG, "format": "RGB888"}
)

# ==== HILFSFUNKTIONEN ====
def finde_usb_stick():
    for name in os.listdir(USB_ORDNER):
        pfad = os.path.join(USB_ORDNER, name)
        if os.path.ismount(pfad):
            print("USB-Stick gefunden:", pfad)
            return pfad
    print("Kein USB-Stick gefunden!")
    return None

def kopiere_bild_auf_usb(dateipfad, usb_pfad):
    try:
        ziel = os.path.join(usb_pfad, "Fotobox-Bilder")
        if not os.path.exists(ziel):
            os.makedirs(ziel)
        shutil.copy(dateipfad, ziel)
        print("Bild auf Stick kopiert:", dateipfad, "→", ziel)
    except Exception as e:
        print(f"Fehler beim Kopieren auf USB: {e}")

def erstelle_thumbnail(original_path, thumb_path):
    if not os.path.exists(THUMBNAIL_ORDNER):
        os.makedirs(THUMBNAIL_ORDNER)
    try:
        img = Image.open(original_path)
        img.thumbnail(THUMB_SIZE)
        img.save(thumb_path, "JPEG")
    except Exception as e:
        print(f"Thumbnail Fehler: {e}")

def lade_bilder():
    if not os.path.exists(FOTO_ORDNER):
        os.makedirs(FOTO_ORDNER)
    bilder = [os.path.join(FOTO_ORDNER, f) for f in os.listdir(FOTO_ORDNER) if f.lower().endswith(".jpg")]
    bilder.sort()
    return bilder

def lade_thumbnails():
    if not os.path.exists(THUMBNAIL_ORDNER):
        os.makedirs(THUMBNAIL_ORDNER)
    thumbs = []
    for f in os.listdir(THUMBNAIL_ORDNER):
        if f.lower().endswith(".jpg"):
            path = os.path.join(THUMBNAIL_ORDNER, f)
            try:
                with Image.open(path) as img:
                    img.verify()
                thumbs.append(path)
            except Exception:
                print(f"Defektes Thumbnail entfernt: {path}")
                try:
                    os.remove(path)
                except Exception:
                    pass
    thumbs.sort()
    return thumbs

def erstelle_galerie_html(bilder, zielordner):
    with open(os.path.join(zielordner, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>{EVENT_TITEL} – Galerie</title>
<meta name="viewport" content="width=480">
<style>
body {{ margin:0; background:rgb{MID_BG}; font-family:sans-serif; }}
.header {{ background:rgb{TOP_BG}; color:white; text-align:center; padding:24px 0; font-size:2em; }}
.galerie {{ display:flex; flex-wrap:wrap; justify-content:center; background:rgb{MID_BG}; min-height:400px; }}
.bildbox {{ margin:12px; background:#222; border-radius:12px; overflow:hidden; box-shadow:0 4px 12px #1115; }}
.bildbox img {{ width:180px; display:block; }}
.footer {{ background:rgb{FOOTER_BG}; color:gold; text-align:center; padding:18px 0; font-size:1.2em; }}
a.download {{ display:block; margin-top:6px; color:gold; font-size:1em; text-decoration:none; }}
</style>
</head>
<body>
<div class="header">{EVENT_TITEL}</div>
<div class="galerie">
""")
        for bild in bilder[::-1]:
            bildname = os.path.basename(bild)
            thumb_path = f"thumbnails/{bildname}"
            orig_path = f"bilder/{bildname}"
            f.write(f"""<div class="bildbox">
<img src="{thumb_path}" alt="">
<a class="download" href="{orig_path}" download>⬇️ Download</a>
</div>""")
        f.write(f"""</div>
<div class="footer">Powered by SelfieStation | Viel Spaß mit den Fotos!</div>
</body></html>
""")

def draw_top(text, icon=None):
    pygame.draw.rect(screen, TOP_BG, (0,0,DISPLAY_WIDTH,80))
    text_surf = font_big.render(text, True, WHITE)
    screen.blit(text_surf, (DISPLAY_WIDTH//2 - text_surf.get_width()//2, 18))
    if icon:
        screen.blit(icons[icon], (DISPLAY_WIDTH//2 + text_surf.get_width()//2 + 10, 18))

def draw_footer(text, icon=None):
    pygame.draw.rect(screen, FOOTER_BG, (0,DISPLAY_HEIGHT-80,DISPLAY_WIDTH,80))
    text_surf = font_footer.render(text, True, GOLD)
    screen.blit(text_surf, (DISPLAY_WIDTH//2 - text_surf.get_width()//2, DISPLAY_HEIGHT-60))
    if icon:
        screen.blit(icons[icon], (DISPLAY_WIDTH//2 + text_surf.get_width()//2 + 10, DISPLAY_HEIGHT-60))

def draw_slideshow(thumbnails):
    pygame.draw.rect(screen, MID_BG, (0,80,DISPLAY_WIDTH,DISPLAY_HEIGHT-160))
    if not thumbnails:
        info = font_mid.render("Noch keine Fotos...", True, GOLD)
        screen.blit(info, (DISPLAY_WIDTH//2 - info.get_width()//2, DISPLAY_HEIGHT//2-50))
        screen.blit(icons["party"], (DISPLAY_WIDTH//2 + info.get_width()//2 + 16, DISPLAY_HEIGHT//2-52))
        return
    idx = int(time.time() // 2) % len(thumbnails)
    bild = pygame.image.load(thumbnails[idx])
    bild = pygame.transform.smoothscale(bild, (480, 270))
    shadow_rect = pygame.Rect(DISPLAY_WIDTH//2 - 245 + 12, DISPLAY_HEIGHT//2 - 135 + 12, 480, 270)
    pygame.draw.rect(screen, SLIDESHOW_SHADOW_COLOR, shadow_rect, border_radius=28)
    border_rect = pygame.Rect(DISPLAY_WIDTH//2 - 245, DISPLAY_HEIGHT//2 - 135, 480, 270)
    pygame.draw.rect(screen, SLIDESHOW_FRAME_COLOR, border_rect, border_radius=28, width=10)
    screen.blit(bild, (DISPLAY_WIDTH//2 - 240, DISPLAY_HEIGHT//2 - 130))

def play_sound():
    try:
        pygame.mixer.music.load(SOUND_PATH)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Soundfehler: {e}")

# ==== NEU: KAMERA-PREVIEW IMMER GANZES BILD VISIBLE (Letterboxing) ====
def scale_and_letterbox(frame):
    # Optional: flip preview
    if FLIP_PREVIEW:
        frame = cv2.flip(frame, 1)
    # Bild zu RGB falls nötig (je nach Picamera-Ausgabe)
    if len(frame.shape) == 3 and frame.shape[2] == 3:
        rgb = frame
    else:
        rgb = cv2.cvtColor(frame, cv2.COLOR_YUV2RGB_I420)
    # Seitenverhältnisse berechnen
    fh, fw = rgb.shape[0], rgb.shape[1]
    fr = fw / fh
    dr = DISPLAY_WIDTH / DISPLAY_HEIGHT
    if fr > dr:
        # Bild breiter als Display (Balken oben/unten)
        new_w = DISPLAY_WIDTH
        new_h = int(DISPLAY_WIDTH / fr)
    else:
        # Bild schmaler/höher als Display (Balken links/rechts)
        new_h = DISPLAY_HEIGHT
        new_w = int(DISPLAY_HEIGHT * fr)
    scaled = cv2.resize(rgb, (new_w, new_h))
    surf = pygame.surfarray.make_surface(np.rot90(scaled))
    x = (DISPLAY_WIDTH - new_w) // 2
    y = (DISPLAY_HEIGHT - new_h) // 2
    screen.fill(MID_BG)
    screen.blit(surf, (x, y))
    return x, y, new_w, new_h

def countdown_animation():
    start_time = time.time()
    count_from = COUNTDOWN_SECONDS
    while True:
        now = time.time()
        seconds_left = count_from - int(now - start_time)
        if seconds_left <= 0:
            break
        frame = picam2.capture_array()
        scale_and_letterbox(frame)
        if seconds_left in countdown_images:
            screen.blit(countdown_images[seconds_left], (DISPLAY_WIDTH//2 - 100, DISPLAY_HEIGHT//2 - 100))
        draw_footer(COUNTDOWN_TEXT, icon="photo")
        pygame.display.flip()
        pygame.time.wait(25)

def fotomodus():
    # 1. "Mach dich bereit!" wartet auf Tap/Buzzer
    picam2.configure(preview_config)
    picam2.start()
    ready = True
    while ready:
        frame = picam2.capture_array()
        scale_and_letterbox(frame)
        draw_top(HEADER_TEXT_READY, icon="party")
        draw_footer(FOOTER_TEXT_READY, icon="photo")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                ready = False
            if event.type == pygame.QUIT:
                picam2.stop()
                return
        if button_shoot.is_pressed:
            ready = False
        pygame.time.wait(20)
    # 2. Countdown
    countdown_animation()
    picam2.stop()
    # 3. Foto aufnehmen!
    picam2.configure(capture_config)
    picam2.start()
    foto_dateiname = f"foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    foto_pfad = os.path.join(FOTO_ORDNER, foto_dateiname)
    picam2.capture_file(foto_pfad)
    play_sound()
    picam2.stop()
    # 4. Vorschau: behalten/neu
    # --- Foto laden, skalieren, ggf. spiegeln ---
    bild = pygame.image.load(foto_pfad)
    if FLIP_SAVE:
        pil_img = Image.open(foto_pfad)
        pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
        pil_img.save(foto_pfad)
        bild = pygame.image.load(foto_pfad)
    bild = pygame.transform.scale(bild, (DISPLAY_WIDTH, DISPLAY_HEIGHT-160))
    behalten = None
    while behalten is None:
        screen.fill(MID_BG)
        draw_top("Foto behalten?", icon="photo")
        screen.blit(bild, (0, 80))
        # Behalten Button
        pygame.draw.rect(screen, (0,220,0), (100,DISPLAY_HEIGHT-90,250,60))
        t1 = font_footer.render(FOOTER_TEXT_KEEP, True, WHITE)
        screen.blit(t1, (170, DISPLAY_HEIGHT-82))
        screen.blit(icons["check"], (110, DISPLAY_HEIGHT-88))
        # Neu Button
        pygame.draw.rect(screen, (220,20,60), (DISPLAY_WIDTH-350,DISPLAY_HEIGHT-90,250,60))
        t2 = font_footer.render(FOOTER_TEXT_NEW, True, WHITE)
        screen.blit(t2, (DISPLAY_WIDTH-300, DISPLAY_HEIGHT-82))
        screen.blit(icons["back"], (DISPLAY_WIDTH-340, DISPLAY_HEIGHT-88))
        pygame.display.flip()
        # --- BUTTON-LOGIK ---
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 100 < x < 350 and DISPLAY_HEIGHT-90 < y < DISPLAY_HEIGHT-30:
                    behalten = True
                elif DISPLAY_WIDTH-350 < x < DISPLAY_WIDTH-100 and DISPLAY_HEIGHT-90 < y < DISPLAY_HEIGHT-30:
                    behalten = False
            if event.type == pygame.QUIT:
                behalten = False
        # --- Physische Knöpfe ---
        if button_keep.is_pressed:
            behalten = True
        elif button_new.is_pressed:
            behalten = False
        pygame.time.wait(50)
    # --- Behalten-Feedback/Sperre ---
    if behalten:
        thumbnail_pfad = os.path.join(THUMBNAIL_ORDNER, foto_dateiname)
        erstelle_thumbnail(foto_pfad, thumbnail_pfad)
        stick = finde_usb_stick()
        if stick:
            kopiere_bild_auf_usb(foto_pfad, stick)
        bilder = lade_bilder()
        erstelle_galerie_html(bilder, GALERIE_ORDNER)
        try:
            shutil.copy(os.path.join(GALERIE_ORDNER, "index.html"), "/var/www/html/index.html")
            shutil.copytree(FOTO_ORDNER, "/var/www/html/bilder", dirs_exist_ok=True)
            shutil.copytree(THUMBNAIL_ORDNER, "/var/www/html/thumbnails", dirs_exist_ok=True)
        except Exception as e:
            print(f"Fehler beim Kopieren in Webverzeichnis: {e}")
        # --- Feedback für 1 Sekunde ---
        screen.fill(MID_BG)
        t = font_big.render("Foto gespeichert!", True, GOLD)
        screen.blit(t, (DISPLAY_WIDTH//2 - t.get_width()//2, DISPLAY_HEIGHT//2 - 28))
        pygame.display.flip()
        pygame.time.wait(1000)
    else:
        if os.path.exists(foto_pfad):
            try:
                os.remove(foto_pfad)
            except Exception as e:
                print(f"Fehler beim Löschen Foto: {e}")
        # --- Feedback für 0.5 Sekunde ---
        screen.fill(MID_BG)
        t = font_big.render("Neues Foto...", True, GOLD)
        screen.blit(t, (DISPLAY_WIDTH//2 - t.get_width()//2, DISPLAY_HEIGHT//2 - 28))
        pygame.display.flip()
        pygame.time.wait(500)
        return fotomodus()  # Neu machen

def mainloop():
    for ordner in [FOTO_ORDNER, GALERIE_ORDNER, THUMBNAIL_ORDNER]:
        if not os.path.exists(ordner):
            os.makedirs(ordner)
    bilder = lade_bilder()
    thumbnails = lade_thumbnails()
    erstelle_galerie_html(bilder, GALERIE_ORDNER)
    try:
        shutil.copy(os.path.join(GALERIE_ORDNER, "index.html"), "/var/www/html/index.html")
        shutil.copytree(FOTO_ORDNER, "/var/www/html/bilder", dirs_exist_ok=True)
        shutil.copytree(THUMBNAIL_ORDNER, "/var/www/html/thumbnails", dirs_exist_ok=True)
    except Exception as e:
        print(f"Fehler beim Initial-Kopieren in Webverzeichnis: {e}")
    while True:
        screen.fill((0,0,0))
        draw_top(EVENT_TITEL, icon="party")
        thumbnails = lade_thumbnails()
        draw_slideshow(thumbnails)
        draw_footer(FOOTER_TEXT_TAKE, icon="photo")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                fotomodus()
        if button_shoot.is_pressed:
            fotomodus()
        pygame.time.wait(50)

if __name__ == "__main__":
    mainloop()
