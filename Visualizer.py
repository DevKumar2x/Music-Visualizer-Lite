import pygame
import wave
import numpy as np
import sys

AUDIO_FILE = "Ek_din01.wav"
WINDOW_SIZE = (1000, 800)
FPS = 60

# === INIT ===
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Music Visualizer Lite")

pygame.mixer.music.load(AUDIO_FILE)

wf = wave.open(AUDIO_FILE, 'rb')
frame_rate = wf.getframerate()
frames_per_tick = int(frame_rate / FPS)

pygame.mixer.music.play()
clock = pygame.time.Clock()

# === MAIN LOOP ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    data = wf.readframes(frames_per_tick)
    if len(data) == 0:
        break

    audio_data = np.frombuffer(data, dtype=np.int16)
    volume = np.linalg.norm(audio_data) / len(audio_data)

    intensity = min(int(volume * 15), 255)
    color = (intensity, 80, 255 - intensity)

    screen.fill((0, 0, 0))
    radius = max(50, intensity * 2)
    pygame.draw.circle(
        screen,
        color,
        (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2),
        radius
    )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
wf.close()
sys.exit()
