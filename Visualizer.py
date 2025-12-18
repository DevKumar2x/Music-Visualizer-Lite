import pygame
import wave
import numpy as np
import sys

# ================= CONFIG =================
AUDIO_FILE = "Ek_din01.wav"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
BAR_COUNT = 64

# ================= INIT =================
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Advanced Music Visualizer")

clock = pygame.time.Clock()

# ================= LOAD AUDIO =================
pygame.mixer.music.load(AUDIO_FILE)
wf = wave.open(AUDIO_FILE, 'rb')

frame_rate = wf.getframerate()
frames_per_tick = int(frame_rate / FPS)

pygame.mixer.music.play()

# ================= VISUAL STATE =================
prev_energy = 0
beat_flash = 0

# ================= MAIN LOOP =================
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ===== Read Audio =====
    data = wf.readframes(frames_per_tick)
    if len(data) == 0:
        break

    audio = np.frombuffer(data, dtype=np.int16)
    audio = audio / 32768.0  # normalize

    # ================= FFT =================
    fft = np.abs(np.fft.rfft(audio))
    fft = fft[:BAR_COUNT]
    fft = fft / np.max(fft + 1e-6)

    # ================= BEAT DETECTION =================
    energy = np.sum(audio ** 2)
    if energy > prev_energy * 1.3:
        beat_flash = 255
    prev_energy = energy
    beat_flash = max(0, beat_flash - 10)

    # ================= DRAW =================
    screen.fill((5, 5, 10))

    # ---------- Frequency Bars ----------
    bar_width = WINDOW_WIDTH // BAR_COUNT
    for i, value in enumerate(fft):
        height = int(value * 300)
        x = i * bar_width
        y = WINDOW_HEIGHT // 2 - height

        color = (
            min(255, int(value * 400)),
            80,
            255 - int(value * 200)
        )

        pygame.draw.rect(
            screen,
            color,
            (x, y, bar_width - 2, height * 2)
        )

    # ---------- Waveform ----------
    waveform_y = WINDOW_HEIGHT - 200
    step = max(1, len(audio) // WINDOW_WIDTH)

    points = []
    for x in range(WINDOW_WIDTH):
        idx = x * step
        if idx < len(audio):
            y = waveform_y + int(audio[idx] * 120)
            points.append((x, y))

    if len(points) > 1:
        pygame.draw.lines(screen, (0, 200, 255), False, points, 2)

    # ---------- Beat Glow Effect ----------
    if beat_flash > 0:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, beat_flash))
        screen.blit(overlay, (0, 0))

    # ---------- Center Pulse Circle ----------
    radius = int(80 + energy * 4000)
    pygame.draw.circle(
        screen,
        (255, 80, 80),
        (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2),
        min(radius, 200),
        3
    )

    pygame.display.flip()
    clock.tick(FPS)

# ================= CLEANUP =================
wf.close()
pygame.quit()
sys.exit()
