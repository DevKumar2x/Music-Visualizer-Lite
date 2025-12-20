import pygame
import wave
import numpy as np
import sys
import time

# === CONFIG ===
AUDIO_FILE = "Music/Ek_din01.wav"
WIDTH, HEIGHT = 1280, 800
FPS = 60
BARS = 80

# === INIT ===
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Music Visualizer")

clock = pygame.time.Clock()
fullscreen = False

# === AUDIO ===
pygame.mixer.music.load(AUDIO_FILE)
wf = wave.open(AUDIO_FILE, 'rb')

rate = wf.getframerate()
channels = wf.getnchannels()
frames_per_tick = int(rate / FPS)

pygame.mixer.music.play()

# === STATE ===
paused = False

prev_energy = 0
beat_flash = 0
beat_times = []
bpm = 0

last_audio = None
last_fft_l = None
last_fft_r = None
last_left = None
last_right = None

# === MAIN LOOP ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_SPACE:
                pygame.mixer.music.pause()
                paused = True

            if event.key == pygame.K_RETURN:
                pygame.mixer.music.unpause()
                paused = False

            if event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # ==== AUDIO READ ====
    if not paused:
        data = wf.readframes(frames_per_tick)
        if len(data) == 0:
            break

        audio = np.frombuffer(data, dtype=np.int16)

        if channels == 2:
            left = audio[::2] / 32768.0
            right = audio[1::2] / 32768.0
        else:
            left = right = audio / 32768.0

        # ==== FFT ====
        fft_l = np.abs(np.fft.rfft(left))[:BARS]
        fft_r = np.abs(np.fft.rfft(right))[:BARS]

        fft_l /= np.max(fft_l) + 1e-6
        fft_r /= np.max(fft_r) + 1e-6

        # ==== BEAT & BPM ====
        energy = np.sum(left ** 2 + right ** 2)
        now = time.time()

        if energy > prev_energy * 1.4:
            beat_flash = 220
            beat_times.append(now)

            if len(beat_times) > 10:
                beat_times.pop(0)

            if len(beat_times) >= 2:
                intervals = np.diff(beat_times)
                bpm = int(60 / np.mean(intervals))

        prev_energy = energy
        beat_flash = max(0, beat_flash - 10)

        # Save last state
        last_audio = audio
        last_left = left
        last_right = right
        last_fft_l = fft_l
        last_fft_r = fft_r

    else:
        # Freeze visuals
        left = last_left
        right = last_right
        fft_l = last_fft_l
        fft_r = last_fft_r

    if left is None:
        continue

    # ==== DRAW ====
    screen.fill((8, 8, 20))
    bar_width = WIDTH // BARS
    mid_y = HEIGHT // 2

    if fft_l is None or fft_r is None:
        continue

    # --- FFT BARS (SPOTIFY STYLE) ---
    for i in range(BARS):
        hl = int(fft_l[i] * 300)
        hr = int(fft_r[i] * 300)

        x = i * bar_width
        color = (
            min(255, int(fft_l[i] * 400)),
            min(255, int(fft_r[i] * 400)),
            255
        )

        pygame.draw.rect(screen, color, (x, mid_y - hl, bar_width - 2, hl))
        pygame.draw.rect(screen, color, (x, mid_y, bar_width - 2, hr))

    # --- FULL WIDTH WAVEFORM ---
    waveform_y = int(HEIGHT * 0.75)
    samples = len(left)
    points = []

    for x in range(WIDTH):
        idx = int(x * samples / WIDTH)
        y = waveform_y + int(left[idx] * 120)
        points.append((x, y))

    pygame.draw.lines(screen, (0, 255, 200), False, points, 2)

    # --- BEAT GLOW ---
    if beat_flash > 0:
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        glow.fill((255, 255, 255, beat_flash))
        screen.blit(glow, (0, 0))

    # --- CENTER PULSE ---
    radius = min(250, int(80 + prev_energy * 6000))
    pygame.draw.circle(
        screen,
        (255, 80, 120),
        (WIDTH // 2, HEIGHT // 2),
        radius,
        4
    )

    # --- BPM DISPLAY ---
    font = pygame.font.SysFont("consolas", 22)
    bpm_text = font.render(f"BPM: {bpm}", True, (255, 255, 255))
    screen.blit(bpm_text, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

# === CLEANUP ===
wf.close()
pygame.quit()
sys.exit()
