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
BEAT_COOLDOWN = 0.25  # seconds

# === INIT ===
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Music Visualizer")

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)
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

prev_energy = 0.0
beat_flash = 0
last_beat_time = 0
beat_times = []
bpm = 0

# Safe default buffers (CRITICAL)
last_left = np.zeros(frames_per_tick)
last_right = np.zeros(frames_per_tick)
last_fft_l = np.zeros(BARS)
last_fft_r = np.zeros(BARS)
pulse_radius = 80
last_pulse_radius = 80

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

    # === AUDIO PROCESS ===
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

        # FFT
        fft_l = np.abs(np.fft.rfft(left))[:BARS]
        fft_r = np.abs(np.fft.rfft(right))[:BARS]

        fft_l /= np.max(fft_l) + 1e-6
        fft_r /= np.max(fft_r) + 1e-6

        # FFT smoothing
        fft_l = 0.7 * last_fft_l + 0.3 * fft_l
        fft_r = 0.7 * last_fft_r + 0.3 * fft_r

        # Beat detection
        energy = np.sum(left ** 2 + right ** 2)
        now = time.time()

        if (
            energy > prev_energy * 1.4
            and now - last_beat_time > BEAT_COOLDOWN
        ):
            beat_flash = 220
            last_beat_time = now
            beat_times.append(now)

            if len(beat_times) > 10:
                beat_times.pop(0)

            if len(beat_times) >= 2:
                bpm = int(60 / np.mean(np.diff(beat_times)))

        prev_energy = energy
        beat_flash = max(0, beat_flash - 10)

        pulse_radius = min(250, int(80 + energy * 6000))

        # Save frozen state
        last_left = left
        last_right = right
        last_fft_l = fft_l
        last_fft_r = fft_r
        last_pulse_radius = pulse_radius

    else:
        left = last_left
        right = last_right
        fft_l = last_fft_l
        fft_r = last_fft_r
        pulse_radius = last_pulse_radius

    # === DRAW ===
    screen.fill((8, 8, 20))
    bar_width = WIDTH // BARS
    mid_y = HEIGHT // 2

    # FFT bars (Spotify-style stereo)
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

    # Full-width waveform
    waveform_y = int(HEIGHT * 0.75)
    samples = len(left)
    points = []

    for x in range(WIDTH):
        idx = min(samples - 1, int(x * samples / WIDTH))
        y = waveform_y + int(left[idx] * 120)
        points.append((x, y))

    pygame.draw.lines(screen, (0, 255, 200), False, points, 2)

    # Beat glow shader
    if beat_flash > 0:
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        glow.fill((255, 255, 255, beat_flash))
        screen.blit(glow, (0, 0))

    # Center pulse
    pygame.draw.circle(
        screen,
        (255, 80, 120),
        (WIDTH // 2, HEIGHT // 2),
        pulse_radius,
        4
    )

    # BPM display
    bpm_text = font.render(f"BPM: {bpm}", True, (255, 255, 255))
    screen.blit(bpm_text, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

# === CLEANUP ===
wf.close()
pygame.quit()
sys.exit()
