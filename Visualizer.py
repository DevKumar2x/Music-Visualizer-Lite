import pygame
import wave
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL, QUIT

from OpenGL.GL import (
    glCreateShader, glShaderSource, glCompileShader,
    glCreateProgram, glAttachShader, glLinkProgram, glUseProgram,
    glGetUniformLocation, glUniform1f,
    glClear, glEnableClientState, glDisableClientState,
    glVertexPointer, glDrawArrays,
    GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
    GL_COLOR_BUFFER_BIT, GL_FLOAT, GL_LINE_LOOP, GL_VERTEX_ARRAY
)

# === CONFIG ===
AUDIO_FILE = "Music/Ek_din01.wav"
WIDTH, HEIGHT = 1280, 800
FPS = 60
FFT_SIZE = 1024

# === SHADERS (LEGACY SAFE) ===
VERTEX_SHADER = """
#version 120
attribute vec2 position;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 120
uniform float intensity;
void main() {
    vec3 color = vec3(0.2, 0.9, 1.0) * intensity;
    gl_FragColor = vec4(color, 1.0);
}
"""

# === INIT ===
pygame.init()
pygame.mixer.init(44100, -16, 2, 512)
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
clock = pygame.time.Clock()

# === OPENGL ===
def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)
    return shader

vs = compile_shader(VERTEX_SHADER, GL_VERTEX_SHADER)
fs = compile_shader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)

shader = glCreateProgram()
glAttachShader(shader, vs)
glAttachShader(shader, fs)
glLinkProgram(shader)
glUseProgram(shader)

intensity_loc = glGetUniformLocation(shader, "intensity")

# === AUDIO ===
wf = wave.open(AUDIO_FILE, 'rb')
rate = wf.getframerate()
frames_per_tick = rate // FPS

pygame.mixer.music.load(AUDIO_FILE)
pygame.mixer.music.play()

# === ONSET STATE ===
spec_size = FFT_SIZE // 2 + 1
prev_spectrum = np.zeros(spec_size)
band_mean = np.ones(spec_size)
onset_strength = 0.0

# === MAIN LOOP ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    data = wf.readframes(frames_per_tick)
    if len(data) == 0:
        break

    audio = np.frombuffer(data, dtype=np.int16)
    audio = audio[::2] / 32768.0  # left channel only

    # === FFT + PROPER ONSET ===
    spectrum = np.abs(np.fft.rfft(audio, FFT_SIZE))
    spectrum = np.log1p(spectrum)

    band_mean = 0.99 * band_mean + 0.01 * spectrum
    norm = spectrum / (band_mean + 1e-6)

    flux = np.sum(np.maximum(norm - prev_spectrum, 0))
    prev_spectrum = norm
    onset_strength = min(1.0, flux * 2.0)

    # === CIRCULAR OSCILLOSCOPE ===
    samples = len(audio)
    angles = np.linspace(0, 2 * np.pi, samples, endpoint=False)
    radius = 0.4 + audio * 0.25

    x = radius * np.cos(angles)
    y = radius * np.sin(angles)

    points = np.column_stack((x, y)).astype(np.float32)

    # === DRAW ===
    glClear(GL_COLOR_BUFFER_BIT)
    glUniform1f(intensity_loc, 0.5 + onset_strength)

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, points)
    glDrawArrays(GL_LINE_LOOP, 0, len(points))
    glDisableClientState(GL_VERTEX_ARRAY)

    pygame.display.flip()
    clock.tick(FPS)

# === CLEANUP ===
wf.close()
pygame.quit()
