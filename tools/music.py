"""Original lo-fi background music generator for reels (no copyrighted material).
Usage: python3 music.py OUT.wav DURATION_SECONDS [SEED]
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 7)

BPM = rng.choice([84, 88, 92])
beat = 60 / BPM
n = int(SR * dur)
mix = np.zeros(n)

def note(freq, length, amp, kind="pad"):
    t = np.arange(int(SR * length)) / SR
    if kind == "pad":
        w = sum(np.sin(2 * np.pi * freq * k * t) / k ** 1.6 for k in (1, 2, 3))
        env = np.minimum(1, t / 0.25) * np.exp(-t * 0.6)
    elif kind == "pluck":
        w = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)
        env = np.exp(-t * 5)
    else:  # bass
        w = np.sin(2 * np.pi * freq * t)
        env = np.minimum(1, t / 0.02) * np.exp(-t * 1.5)
    return amp * w * env

def add(sig, start):
    i = int(start * SR)
    if i >= n:
        return
    j = min(n, i + len(sig))
    mix[i:j] += sig[: j - i]

def midi(m):
    return 440 * 2 ** ((m - 69) / 12)

# Progressions (minor-ish, calm, "study" mood)
progs = [
    [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]],  # Am7 Fmaj7 Cmaj7 G7
    [[50, 53, 57, 60], [55, 59, 62, 65], [48, 52, 55, 59], [57, 60, 64, 67]],  # Dm7 G7 Cmaj7 Am7
]
prog = progs[rng.integers(len(progs))]
bar = beat * 4
t = 0.0
k = 0
while t < dur:
    ch = prog[k % len(prog)]
    for m in ch:
        add(note(midi(m), bar * 1.1, 0.07, "pad"), t)
    add(note(midi(ch[0] - 12), bar * 0.9, 0.22, "bass"), t)
    # melody plucks from chord tones, pentatonic flavour
    for s in range(8):
        if rng.random() < 0.55:
            m = ch[rng.integers(4)] + 12 + rng.choice([0, 0, 2, -3])
            add(note(midi(m), beat, 0.06, "pluck"), t + s * beat / 2)
    t += bar
    k += 1

# Drums: soft kick, snare-ish noise, hats
def kick():
    tt = np.arange(int(SR * 0.35)) / SR
    f = 110 * np.exp(-tt * 18) + 45
    return 0.55 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)

def noise(length, decay, amp, hp):
    s = rng.standard_normal(int(SR * length)) * np.exp(-np.arange(int(SR * length)) / SR * decay)
    b, a = butter(2, hp / (SR / 2), btype="high")
    return amp * lfilter(b, a, s)

t = 0.0
step = 0
while t < dur:
    pos = step % 8
    if pos in (0, 5):
        add(kick(), t)
    if pos in (2, 6):
        add(noise(0.18, 22, 0.16, 1200), t)
    add(noise(0.05, 60, 0.05 if pos % 2 else 0.07, 7000), t + (0.02 if pos % 2 else 0))
    t += beat / 2
    step += 1

# Warmth: low-pass + vinyl crackle
b, a = butter(2, 6500 / (SR / 2))
mix = lfilter(b, a, mix)
crackle = (rng.random(n) < 0.0008) * rng.standard_normal(n) * 0.05
mix += crackle

# Fade in/out, normalize
fade = int(SR * 1.2)
mix[:fade] *= np.linspace(0, 1, fade)
mix[-fade * 2:] *= np.linspace(1, 0, fade * 2)
mix = mix / np.max(np.abs(mix)) * 0.8
stereo = np.stack([mix, np.roll(mix, 220)], axis=1)
wavfile.write(out, SR, (stereo * 32767).astype(np.int16))
print(f"bpm={BPM} dur={dur}")
