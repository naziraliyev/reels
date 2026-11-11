"""Original background music generator for reels (no copyrighted material).

Usage: python3 music.py OUT.wav DURATION_SECONDS [SEED] [STYLE]

Each topic direction has its own sound, so the channel's videos are recognisable by ear:
  lofi   — Dasturlash (python / js / umumiy): calm lo-fi hip-hop, swung drums, e-piano, vinyl crackle
  sql    — SQL: "deep focus" synth — minor key, steady pulse, 16th arpeggio, sub bass, echo
  flutter— Flutter / Dart: bright, upbeat pop — major key, marimba + bells, claps, shaker
Every run uses a different seed, so melodies/progressions vary inside a style.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
STYLE = (sys.argv[4] if len(sys.argv) > 4 else "lofi").lower()
if STYLE not in ("lofi", "sql", "flutter"):
    STYLE = "lofi"
rng = np.random.default_rng(seed)
n = int(SR * dur)
mix = np.zeros(n)


# ---------------------------------------------------------------- helpers
def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def tvec(length):
    return np.arange(int(SR * length)) / SR


def add(sig, start, buf=None):
    buf = mix if buf is None else buf
    i = int(start * SR)
    if i >= len(buf) or i < 0:
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def lp(x, hz, order=2):
    b, a = butter(order, hz / (SR / 2))
    return lfilter(b, a, x)


def hp(x, hz, order=2):
    b, a = butter(order, hz / (SR / 2), btype="high")
    return lfilter(b, a, x)


def echo(x, delay, fb=0.35, mixamt=0.35, taps=4):
    y = x.copy()
    d = int(SR * delay)
    g = mixamt
    for k in range(1, taps + 1):
        if d * k >= len(x):
            break
        y[d * k:] += g * x[: len(x) - d * k]
        g *= fb
    return y


def noise(length, decay, amp, hpf):
    s = rng.standard_normal(int(SR * length)) * np.exp(-tvec(length) * decay)
    return amp * hp(s, hpf)


def kick(f0=110, f1=45, decay=9, amp=0.55, length=0.35):
    t = tvec(length)
    f = (f0 - f1) * np.exp(-t * 18) + f1
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * decay)


def finish(sig, crackle=0.0, width=220):
    if crackle:
        sig = sig + (rng.random(n) < 0.0008) * rng.standard_normal(n) * crackle
    fade = int(SR * 1.0)
    sig[:fade] *= np.linspace(0, 1, fade)
    sig[-fade * 2:] *= np.linspace(1, 0, fade * 2)
    # same perceived level for every style: normalise RMS, then soft-limit peaks
    sig = sig / (np.sqrt(np.mean(sig ** 2)) + 1e-9) * 0.12
    sig = np.tanh(sig * 1.1) / 1.1
    sig = sig / max(1.0, np.max(np.abs(sig)) / 0.89)
    stereo = np.stack([sig, np.roll(sig, width)], axis=1)
    wavfile.write(out, SR, (stereo * 32767).astype(np.int16))


# ---------------------------------------------------------------- LOFI (Dasturlash)
def style_lofi():
    global mix
    bpm = rng.choice([80, 84, 88, 92])
    beat = 60 / bpm
    swing = beat / 2 * 0.16

    def epiano(freq, length, amp):
        t = tvec(length)
        w = np.sin(2 * np.pi * freq * t + 0.6 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 3))
        w += 0.25 * np.sin(4 * np.pi * freq * t)
        env = np.minimum(1, t / 0.01) * np.exp(-t * 1.1)
        return amp * w * env

    def pluck(freq, length, amp):
        t = tvec(length)
        return amp * (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * 5)

    progs = [
        [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]],  # Am7 Fmaj7 Cmaj7 G7
        [[50, 53, 57, 60], [55, 59, 62, 65], [48, 52, 55, 59], [57, 60, 64, 67]],  # Dm7 G7 Cmaj7 Am7
        [[52, 55, 59, 62], [57, 60, 64, 67], [50, 53, 57, 60], [55, 59, 62, 65]],  # Em7 Am7 Dm7 G7
    ]
    prog = progs[rng.integers(len(progs))]
    bar = beat * 4
    t, k = 0.0, 0
    while t < dur:
        ch = prog[k % len(prog)]
        for m in ch:
            add(epiano(midi(m), bar * 1.05, 0.06), t + rng.random() * 0.02)
        add(epiano(midi(ch[0] - 12), bar * 0.9, 0.16), t)
        for s in range(8):
            if rng.random() < 0.5:
                m = ch[rng.integers(4)] + 12 + rng.choice([0, 0, 2, -3])
                add(pluck(midi(m), beat, 0.05), t + s * beat / 2 + (swing if s % 2 else 0))
        t += bar
        k += 1

    t, step = 0.0, 0
    while t < dur:
        pos = step % 8
        off = swing if pos % 2 else 0
        if pos in (0, 5):
            add(kick(), t + off)
        if pos in (2, 6):
            add(noise(0.18, 22, 0.16, 1200), t)
        add(noise(0.05, 60, 0.04 if pos % 2 else 0.06, 7000), t + off)
        t += beat / 2
        step += 1
    mix = lp(mix, 5500)
    finish(mix, crackle=0.05)
    return bpm


# ---------------------------------------------------------------- SQL (deep focus synth)
def style_sql():
    global mix
    bpm = rng.choice([100, 104, 108])
    beat = 60 / bpm
    progs = [
        [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]],  # Dm Bb F C
        [[45, 48, 52], [41, 45, 48], [48, 52, 55], [43, 47, 50]],  # Am F C G
        [[52, 55, 59], [48, 52, 55], [43, 47, 50], [50, 54, 57]],  # Em C G D
    ]
    prog = progs[rng.integers(len(progs))]
    bar = beat * 4

    def saw_pad(freq, length, amp):
        t = tvec(length)
        w = np.zeros_like(t)
        for det in (-0.12, 0.0, 0.12):  # detuned voices
            f = freq * 2 ** (det / 12)
            w += sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, 7))
        env = np.minimum(1, t / 0.6) * np.minimum(1, (length - t) / 0.5)
        return amp * w * env / 3

    def tri(freq, length, amp):
        t = tvec(length)
        w = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))
        return amp * w * np.exp(-t * 7)

    pad = np.zeros(n)
    arp = np.zeros(n)
    t, k = 0.0, 0
    patterns = [[0, 1, 2, 1], [0, 2, 1, 2], [0, 1, 2, 3]]
    pat = patterns[rng.integers(len(patterns))]
    while t < dur:
        ch = prog[k % len(prog)]
        for m in ch:
            add(saw_pad(midi(m), bar * 1.02, 0.05), t, pad)
        notes = ch + [ch[0] + 12]
        for s in range(16):  # 16th-note arpeggio
            m = notes[pat[s % 4] if s % 8 < 4 else (pat[s % 4] + 1) % 4] + 12
            add(tri(midi(m), beat / 2, 0.075 if s % 4 == 0 else 0.05), t + s * beat / 4, arp)
        for e in range(8):  # pulsing sub bass on 8ths
            tt = tvec(beat / 2 * 0.9)
            sub = 0.2 * np.sin(2 * np.pi * midi(ch[0] - 12) * tt) * np.minimum(1, tt / 0.01) * np.exp(-tt * 4)
            add(sub, t + e * beat / 2)
        t += bar
        k += 1
    mix += lp(pad, 2200)
    mix += echo(lp(arp, 4500), beat * 0.75, fb=0.4, mixamt=0.4)

    t, step = 0.0, 0
    while t < dur:
        if step % 2 == 0:  # steady kick on every beat
            add(kick(90, 42, 10, 0.5, 0.3), t)
        else:  # offbeat hat
            add(noise(0.06, 45, 0.035, 6000), t)
        if step % 16 == 12:
            add(echo(noise(0.12, 30, 0.07, 2500), beat * 0.5, 0.3, 0.3, 2), t)
        t += beat / 2
        step += 1
    mix = lp(mix, 7500)
    finish(mix, crackle=0.0, width=330)
    return bpm


# ---------------------------------------------------------------- FLUTTER (bright pop)
def style_flutter():
    global mix
    bpm = rng.choice([112, 116, 120])
    beat = 60 / bpm
    progs = [
        [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]],  # C G Am F
        [[53, 57, 60], [60, 64, 67], [62, 65, 69], [58, 62, 65]],  # F C Dm Bb
        [[55, 59, 62], [62, 66, 69], [64, 67, 71], [60, 64, 67]],  # G D Em C
    ]
    prog = progs[rng.integers(len(progs))]
    bar = beat * 4

    def marimba(freq, length, amp):
        t = tvec(length)
        w = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 25)
        return amp * w * np.exp(-t * 6) * np.minimum(1, t / 0.003)

    def bell(freq, length, amp):
        t = tvec(length)
        w = np.sin(2 * np.pi * freq * t + 1.2 * np.sin(2 * np.pi * freq * 3.5 * t) * np.exp(-t * 4))
        return amp * w * np.exp(-t * 2.5)

    def stab(freq, length, amp):
        t = tvec(length)
        w = sum(np.sin(2 * np.pi * freq * h * t) / h ** 1.3 for h in (1, 2, 3, 4))
        return amp * w * np.exp(-t * 9) * np.minimum(1, t / 0.005)

    # a catchy 2-bar motif re-used through the track (scale degrees relative to chord root)
    rhythm = [0, 1, 1.5, 2.5, 3, 4, 5, 5.5, 6.5, 7]
    motif = [rng.choice([0, 1, 2]) for _ in rhythm]
    lead = np.zeros(n)
    t, k = 0.0, 0
    while t < dur:
        ch = prog[k % len(prog)]
        for s in (1, 3):  # off-beat chord stabs
            for m in ch:
                add(stab(midi(m), beat * 0.8, 0.045), t + s * beat * 0.5 + (s // 2) * beat)
        for e in range(8):  # bouncy octave bass
            m = ch[0] - 24 + (12 if e % 2 else 0)
            tt = tvec(beat / 2 * 0.85)
            add(0.22 * np.sin(2 * np.pi * midi(m) * tt) * np.minimum(1, tt / 0.005) * np.exp(-tt * 5), t + e * beat / 2)
        half = 0 if k % 2 == 0 else 4
        for r, deg in zip(rhythm, motif):
            if half <= r < half + 4:
                m = ch[deg] + 12
                add(marimba(midi(m), beat, 0.12), t + (r - half) * beat, lead)
        if k % 4 == 3:
            add(bell(midi(ch[2] + 24), bar, 0.05), t + beat * 2, lead)
        t += bar
        k += 1
    mix += echo(lead, beat * 0.5, fb=0.3, mixamt=0.25, taps=2)

    t, step = 0.0, 0
    while t < dur:
        pos = step % 16  # 16th grid
        if pos in (0, 8, 10):
            add(kick(130, 50, 11, 0.5, 0.25), t)
        if pos in (4, 12):  # clap
            c = sum(np.roll(noise(0.16, 18, 0.13, 1500), int(SR * 0.008 * i)) for i in range(3))
            add(c, t)
        add(noise(0.04, 80, 0.035 if pos % 2 else 0.05, 8000), t)  # shaker
        t += beat / 4
        step += 1
    mix = lp(mix, 9000)
    finish(mix, crackle=0.0, width=180)
    return bpm


bpm = {"lofi": style_lofi, "sql": style_sql, "flutter": style_flutter}[STYLE]()
print(f"style={STYLE} bpm={bpm} dur={dur}")
