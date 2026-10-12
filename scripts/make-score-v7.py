#!/usr/bin/env python3
"""V7 score: six stems synthesized in-project, composed on the founder's measured voice.

  public/music/temp/v7/{bed,pulse,harmony,rhythm,texture,resolve}.wav   48 kHz stereo, the film's length
  public/music/temp/v7/score-mixdown.wav                                 a reference sum (not played by the film)

Layers (the brief's six):
  bed      atmospheric bed — low drone, air, distant shimmer; never dead silence until the end
  pulse    low cinematic pulse — soft kick with body, sub, analog bass (harmonics so it reads on laptop speakers)
  harmony  warm harmonic texture — detuned analog-style pads, strings-like, slow filter movement
  rhythm   technical rhythmic layer — plucked 16ths with ping-pong delay, soft ticks (restrained percussion)
  texture  transition textures — reverse swells into reveals, digital micro-textures, the permission tone
  resolve  emotional resolution — soft mallet/bell motifs at the human and final moments

Everything is placed on anchors read from the built film data (navislabs_v8_voice_timeline.json,
navislabs_v8_film_spec.json beats): the music opens on "Navis", drops back on "A person decides.",
returns on "Then the company acts.", slows for the permission check, resolves as the run completes,
lifts on "One understanding.", resolves on "Two ways in.", almost stops on "NavisLabs." and leaves a
soft tail under the tagline. Key D major / B minor, 92 BPM. No samples, no external audio: every
sound is generated here, so the stems carry no third-party rights. The mix (ducking, dips) is
applied in Remotion by keyframed volume curves (src/components/AudioLayer.tsx).
A final, recorded/licensed score drops into public/music/final/v7/ (stems, or score.wav).
"""
import json
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "music", "temp", "v7")
SR = 48000
rng = np.random.default_rng(7)

spec = json.load(open(os.path.join(ROOT, "navislabs_v8_film_spec.json")))
tl = json.load(open(os.path.join(ROOT, "navislabs_v8_voice_timeline.json")))
END = spec["format"]["duration_s"]
B = spec["timing"]["beats"]
SC = {s["id"]: (s["from_s"], s["to_s"]) for s in spec["scenes"]}
LINES = {(c["id"], i): (ln["start_s"], ln["end_s"]) for c in tl["chunks"] for i, ln in enumerate(c["lines"])}
N = int(round(END * SR))
BPM = 92.0
BEAT_S = 60.0 / BPM


def LS(c, i):
    return LINES[(c, i)][0]


def LE(c, i):
    return LINES[(c, i)][1]


# ------------------------------------------------------------------ helpers
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def hz(name):
    n, o = (name[:-1], int(name[-1]))
    return 440.0 * 2 ** ((NOTE[n] + 12 * (o + 1) - 69) / 12)


def stereo(x, pan=0.0):
    pan = np.clip(pan, -1, 1)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * l, x * r], axis=1) * np.sqrt(2)


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), "low", fs=SR, output="sos"), x, axis=0)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos"), x, axis=0)


def peaking(x, f0, gain_db, q=0.8):
    """RBJ peaking EQ (used to leave the founder's 2–4 kHz presence band open)."""
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b0, b1, b2 = 1 + al * a, -2 * np.cos(w0), 1 - al * a
    a0, a1, a2 = 1 + al / a, -2 * np.cos(w0), 1 - al / a
    sos = np.array([[b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0]])
    return sosfilt(sos, x, axis=0)


_TABLES = {}


def saw_table(nh):
    if nh not in _TABLES:
        ph = np.arange(4096) / 4096
        t = np.zeros(4096)
        for k in range(1, nh + 1):
            t += np.sin(2 * np.pi * k * ph) / k * (1 - (k / (nh + 1)) ** 2)  # gently rolled-off band-limited saw
        _TABLES[nh] = t / np.abs(t).max()
    return _TABLES[nh]


def osc(f, n, kind="saw", drift=0.0, phase=None):
    """Band-limited wavetable oscillator; f may wobble slightly (analog drift)."""
    t = np.arange(n) / SR
    ff = f * (1 + drift * np.sin(2 * np.pi * (0.13 + 0.07 * rng.random()) * t + rng.random() * 6.28))
    ph = ((rng.random() if phase is None else phase) + np.cumsum(ff) / SR) % 1.0
    if kind == "sine":
        return np.sin(2 * np.pi * ph)
    if kind == "tri":
        return 2 * np.abs(2 * ph - 1) - 1
    tab = saw_table(max(1, min(48, int(15000 / max(f, 20)))))
    idx = ph * 4096
    i0 = idx.astype(np.int64) % 4096
    fr = idx - np.floor(idx)
    return tab[i0] * (1 - fr) + tab[(i0 + 1) % 4096] * fr


def env_adsr(n, a, d, s, r, hold=None):
    """Attack/decay/sustain then release over the last r seconds."""
    e = np.full(n, s)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na, endpoint=False) ** 1.5 if na else e[:na]
    if nd and na < n:
        m = min(nd, n - na)
        e[na:na + m] = 1 - (1 - s) * np.linspace(0, 1, m) ** 0.7
    if nr and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr) ** 1.6
    return e


def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))


def make_ir(rt60, seed, predelay=0.02, bright=4500.0, width=1.0):
    r = np.random.default_rng(seed)
    n = int(rt60 * SR)
    noise = r.standard_normal((n, 2))
    noise[:, 1] = width * noise[:, 1] + (1 - width) * noise[:, 0]
    e = np.exp(-6.91 * np.arange(n) / n)[:, None]
    ir = noise * e
    dark = lp(ir, bright * 0.35, 2)
    w = np.linspace(0, 1, n)[:, None] ** 0.6
    ir = lp(ir, bright, 2) * (1 - w) + dark * w
    ir = np.vstack([np.zeros((int(predelay * SR), 2)), ir])
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True))


IR_HALL = make_ir(3.6, 11, 0.03, 5000)
IR_ROOM = make_ir(1.4, 12, 0.012, 6500)


def reverb(x, ir, wet):
    y = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)
    return x * (1 - wet) + y * wet * 0.9


def pingpong(x, delay_s, fb=0.35, mix=0.25, n_echo=5, damp=3500):
    y = x.copy()
    d = int(delay_s * SR)
    src = lp(x, damp, 1)
    for k in range(1, n_echo + 1):
        g = mix * fb ** (k - 1)
        sh = np.zeros_like(x)
        if k * d < len(x):
            sh[k * d:] = src[: len(x) - k * d]
        sh = sh[:, ::-1] if k % 2 else sh
        y += sh * g
    return y


def put(buf, sig, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    if i < 0:
        sig, i = sig[-i:], 0
    m = min(len(sig), len(buf) - i)
    buf[i:i + m] += sig[:m] * gain


def db(x):
    return 10 ** (x / 20)


def automate(buf, points):
    """Multiply a stem by a piecewise-linear gain curve [(t, dB), …]."""
    t = np.arange(len(buf)) / SR
    ts, gs = zip(*points)
    g = np.interp(t, ts, gs)
    buf *= (10 ** (g / 20))[:, None]
    return buf


# ------------------------------------------------------------------ harmony
CH = {
    "Dmaj9": ("D2", ["D3", "F#3", "A3", "C#4", "E4"]),
    "Dmaj9/F#": ("F#2", ["D3", "A3", "C#4", "E4", "F#4"]),
    "Bm9": ("B1", ["B2", "D3", "F#3", "A3", "C#4"]),
    "Bm11": ("B1", ["B2", "D3", "F#3", "A3", "E4"]),
    "Gmaj9": ("G1", ["G2", "B2", "D3", "F#3", "A3"]),
    "Gmaj9#11": ("G1", ["G2", "B2", "D3", "F#3", "C#4"]),
    "Gmaj7": ("G2", ["G3", "B3", "D4", "F#4"]),
    "Em9": ("E2", ["E3", "G3", "B3", "D4", "F#4"]),
    "Aadd9": ("A1", ["A2", "C#3", "E3", "B3", "E4"]),
    "Asus": ("A1", ["A2", "D3", "E3", "B3"]),
    "D/A": ("A1", ["A2", "D3", "F#3", "A3", "E4"]),
    "Gm6": ("G1", ["G2", "Bb2", "D3", "E3"]),  # borrowed, darker: the refusal
    "dyad": ("A1", ["A2", "E3"]),
}


def pad_chord(name, dur, level=1.0, bright=1600.0, attack=0.9, release=2.2, voices=3, width=0.7, bass=True):
    bass_note, notes = CH[name]
    n = int((dur + release) * SR)
    out = np.zeros((n, 2))
    for j, nm in enumerate(notes):
        f = hz(nm)
        for v in range(voices):
            det = (v - (voices - 1) / 2) * 0.0045
            x = osc(f * (1 + det), n, "saw", drift=0.0012)
            pan = width * ((v / max(1, voices - 1)) * 2 - 1) * (0.6 + 0.4 * (j % 2))
            out += stereo(x, pan) * (0.55 if j else 0.7) / voices
    out = lp(out, bright, 2)
    if bass:
        b = osc(hz(bass_note), n, "tri", drift=0.0008) * 0.55 + osc(hz(bass_note) * 2, n, "sine") * 0.18
        out += stereo(lp(b, 900), 0)
    e = env_adsr(n, attack, 1.2, 0.85, release)
    return out * e[:, None] * level


def place_chords(buf, seq, **kw):
    """seq: [(t_from, t_to, chord, level, brightness)] — overlapping releases crossfade."""
    for a, b, name, lvl, br in seq:
        put(buf, pad_chord(name, b - a, lvl, br, **kw), a)


# ------------------------------------------------------------------ voices
def kick(level=1.0):
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    f = 46 + 70 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    knock = np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.03) * 0.35  # reads on small speakers
    click = bp(rng.standard_normal(n), 1800, 5000) * np.exp(-t / 0.004) * 0.08
    x = np.tanh(1.6 * (body + knock + click)) / np.tanh(1.6)
    return stereo(x * level, 0)


def bass_note(name, dur, level=1.0, cutoff=520):
    n = int((dur + 0.08) * SR)
    f = hz(name)
    x = osc(f, n, "saw", drift=0.0006) * 0.7 + osc(f / 2, n, "sine") * 0.5
    x = lp(x, cutoff, 2)
    x = np.tanh(1.8 * x) / np.tanh(1.8)
    e = env_adsr(n, 0.008, 0.18, 0.55, 0.07)
    return stereo(x * e * level, 0)


def pluck(name, level=1.0, pan=0.0, dark=900, bright=4200, decay=0.22):
    n = int(0.6 * SR)
    f = hz(name)
    x = osc(f, n, "saw") * 0.6 + osc(f * 1.003, n, "saw") * 0.4
    t = np.arange(n) / SR
    y = lp(x, bright, 2) * np.exp(-t / (decay * 0.35)) + lp(x, dark, 2) * np.exp(-t / decay)
    y *= np.minimum(1, t / 0.003)
    return stereo(y * level, pan)


def tick(level=1.0, pan=0.0, hi=True):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    x = (bp(rng.standard_normal(n), 6000 if hi else 3500, 12000 if hi else 8000) * np.exp(-t / (0.006 if hi else 0.012)))
    return stereo(x * level, pan)


def mallet(name, level=1.0, pan=0.0, decay=2.4):
    """Soft FM mallet/bell (1:2 ratio, decaying index) — warm, not a piano."""
    n = int((decay * 2.2) * SR)
    t = np.arange(n) / SR
    fc = hz(name)
    idx = 2.2 * np.exp(-t / 0.18) + 0.25
    y = np.sin(2 * np.pi * fc * t + idx * np.sin(2 * np.pi * 2 * fc * t))
    y += 0.25 * np.sin(2 * np.pi * fc * 3.01 * t) * np.exp(-t / 0.35)
    y *= np.exp(-t / decay) * np.minimum(1, t / 0.004)
    return stereo(y * level, pan)


def noise_swell(dur, lo=300, hi=6000, level=1.0, rise=2.4):
    n = int(dur * SR)
    x = np.stack([rng.standard_normal(n), rng.standard_normal(n)], axis=1)
    x = bp(x, lo, hi)
    e = (np.arange(n) / n) ** rise
    return x * e[:, None] * level


def reverse_swell(chord, dur=1.6, level=1.0):
    p = pad_chord(chord, 0.7, 1.0, 2400, attack=0.01, release=0.6, voices=2, bass=False)
    p = reverb(p, IR_HALL, 0.85)[: int(dur * SR)]
    if len(p) < int(dur * SR):
        p = np.vstack([p, np.zeros((int(dur * SR) - len(p), 2))])
    r = p[::-1]
    r *= (np.linspace(0, 1, len(r)) ** 2)[:, None]
    return r * level


# ------------------------------------------------------------------ stems
bed, pulse, harmony, rhythm, texture, resolve = (np.zeros((N, 2)) for _ in range(6))
NAVIS = LS("P2", 0)  # "Navis"
DEV = SC["S10"][0]
HERO = SC["S17"][0]
THESIS = SC["S18"][0]

# ---- BED: drone + air + shimmer, shaped per act -------------------------------------------
t = np.arange(N) / SR
drone = (osc(hz("D2"), N, "tri", 0.0006) * 0.5 + osc(hz("A2"), N, "sine", 0.0009) * 0.35 + osc(hz("D3") * 1.002, N, "sine") * 0.18)
drone = lp(drone, 700, 2) * (1 + 0.15 * np.sin(2 * np.pi * 0.07 * t))
air = bp(np.stack([rng.standard_normal(N), rng.standard_normal(N)], axis=1), 2500, 9000) * 0.09
air *= (1 + 0.4 * np.sin(2 * np.pi * 0.05 * t + 1.3))[:, None]
rumble = lp(rng.standard_normal(N), 90, 2) * 0.6
bed += stereo(drone, 0) * 0.8 + air + stereo(rumble, 0) * 0.5
shimmer = np.zeros((N, 2))
for k, (nm, a) in enumerate([("C#6", 2.4), ("D6", 2.9), ("A5", 6.6), ("F#6", 7.4), ("E6", 8.2)]):
    put(shimmer, mallet(nm, 0.12, (-0.6, 0.6, -0.3, 0.4, 0.0)[k], 3.5), a)
bed += reverb(shimmer, IR_HALL, 0.8)
bed = reverb(bed, IR_HALL, 0.35)
bed = automate(bed, [(0, -60), (0.4, -20), (3.6, -19), (6.2, -17), (9.77, -13), (11.6, -13), (12.9, -15), (13.2, -40), (NAVIS - 0.02, -40), (NAVIS, -12),
                     (SC["S05"][0], -14), (SC["S09"][1], -14), (DEV, -15), (SC["S16"][0], -14), (HERO, -12), (THESIS, -10), (B["endLockup"] - 0.3, -10),
                     (LS("P8", 0) - 0.05, -26), (LS("P8", 1) - 0.4, -24), (LE("P8", 1) + 0.3, -22), (END - 0.6, -60), (END, -90)])

# ---- HARMONY ------------------------------------------------------------------------------
A1 = []  # Act 1: only a dark, low colour under 'by hand' (heavier), held under 'without it'
place_chords(harmony, [(LS("P1", 2) - 0.2, 13.05, "Bm11", 0.45, 520)], attack=1.4, release=0.6, voices=2, width=0.4)
seq = [
    (NAVIS - 0.01, SC["S04"][0] + 0.2, "Dmaj9", 1.0, 2400),           # the music opens on "Navis"
    (SC["S04"][0], B["flowMemory"], "Bm11", 0.85, 1900),
    (B["flowMemory"], B["flowIntel"], "Gmaj9#11", 0.9, 2100),         # "remembered, connected…"
    (B["flowIntel"], B["flowLearning"] + 0.2, "Aadd9", 0.9, 2300),
    (B["flowLearning"], SC["S05"][0] + 0.3, "D/A", 0.95, 2400),       # pull back on "next"
    # Act 3 · human
    (SC["S05"][0], SC["S06"][0], "Gmaj9", 0.8, 1700),
    (SC["S06"][0], SC["S07"][0], "Dmaj9/F#", 0.8, 1700),
    (SC["S07"][0], LS("P3", 3), "Em9", 0.8, 1800),
    (LS("P3", 3), SC["S08"][0], "Bm9", 0.8, 1800),                    # every fact has its source
    (SC["S08"][0], LS("P3", 4) + 1.8, "Gmaj7", 0.8, 1700),
    (LS("P3", 4) + 1.8, LS("P3", 5) - 0.3, "Aadd9", 0.8, 1700),
    (LS("P3", 5) - 0.3, LS("P3", 6) - 0.05, "dyad", 0.6, 700),         # "A person decides." — a controlled breath
    (LS("P3", 6) - 0.04, B["acrossIn"], "Dmaj9", 1.0, 2300),          # "Then the company acts." — the music returns
    (B["acrossIn"], DEV + 0.2, "Bm11", 0.85, 1900),
    # Act 4 · technical (darker, sparser pads under the rhythm)
    (DEV, SC["S11"][0], "Bm9", 0.6, 1300),
    (SC["S11"][0], B["connectIn"], "Gmaj7", 0.6, 1300),
    (B["connectIn"], SC["S12"][0], "Dmaj9", 0.65, 1500),
    (SC["S12"][0], LS("P4", 4), "Aadd9", 0.6, 1400),
    (LS("P4", 4), SC["S13"][0], "Bm9", 0.6, 1400),
    (SC["S13"][0], LS("P4", 6), "Gmaj9#11", 0.6, 1300),
    (LS("P4", 6), B["permDenied"], "Em9", 0.6, 1300),
    (B["permDenied"], SC["S15"][0], "Gm6", 0.55, 900),                # DENIED: darker, borrowed
    (SC["S15"][0], B["runComplete"], "Bm9", 0.6, 1400),
    (B["runComplete"], SC["S16"][0] + 0.3, "Dmaj9", 0.75, 1900),           # the run is on record: a slight resolution
    # Act 5 · scale
    (SC["S16"][0], B["teamIn"], "Gmaj9", 0.55, 1300),                 # one voice: the solo builder
    (B["teamIn"], LS("P5", 2), "Dmaj9/F#", 0.7, 1600),                # the team
    (LS("P5", 2), LE("P5", 2) + 0.4, "Em9", 0.75, 1700),
    (LE("P5", 2) + 0.4, HERO, "Aadd9", 0.85, 2000),                   # the pause after "next session" rises
    (HERO, LS("P5", 4), "Dmaj9", 0.95, 2300),                         # one company
    (LS("P5", 4), LS("P6", 0) - 0.3, "Bm11", 0.85, 2000),
    (LS("P6", 0) - 0.3, LS("P6", 3) - 0.2, "Gmaj9", 0.8, 1800),       # same facts / sources / freshness: held
    (LS("P6", 3) - 0.2, LS("P6", 4) - 0.1, "Aadd9", 0.95, 2300),      # "One understanding." — lift
    (LS("P6", 4) - 0.1, THESIS + 0.4, "Dmaj9", 0.95, 2400),           # "Two ways in." — resolution
    # Act 6 · thesis: slow, deep, wide
    (THESIS, LE("P7", 2) + 0.2, "Bm9", 0.85, 1500),
    (LE("P7", 2) + 0.2, LS("P7", 3) + 0.1, "Gmaj9#11", 0.95, 1900),   # the pause after "Tools change." rises
    (LS("P7", 3) + 0.1, LS("P7", 4), "Dmaj9/F#", 0.85, 1700),
    (LS("P7", 4), LS("P7", 6), "Em9", 0.85, 1800),
    (LS("P7", 6), B["endLockup"] - 0.2, "Gmaj9", 0.9, 1900),
]
place_chords(harmony, seq, attack=0.8, release=1.8, voices=3, width=0.75)
# The tail under the tagline: one soft chord, then silence.
put(harmony, pad_chord("Dmaj9", 1.6, 0.5, 1500, attack=1.0, release=2.4, voices=3, bass=False), LS("P8", 1) - 0.2)
harmony = peaking(harmony, 2800, -3.5, 0.7)  # leave the founder's presence band open
harmony = reverb(harmony, IR_HALL, 0.42)
harmony = automate(harmony, [(0, -12), (NAVIS - 0.05, -12), (NAVIS, -6), (SC["S05"][0], -7), (DEV, -9), (SC["S16"][0], -8), (HERO, -5), (THESIS, -4),
                             (B["endLockup"] - 0.35, -4), (LS("P8", 0) - 0.05, -40), (LS("P8", 1) - 0.25, -14), (END - 0.9, -26), (END, -90)])

# ---- PULSE: kick + sub + analog bass on a 92 BPM grid ----------------------------------------
K = kick()


def grid(a, b, step, offset=0.0):
    x = a + offset
    while x < b - 1e-6:
        yield x
        x += step


BASS_ROOT = [(NAVIS, SC["S04"][0], "D2"), (SC["S04"][0], B["flowMemory"], "B1"), (B["flowMemory"], B["flowIntel"], "G1"), (B["flowIntel"], SC["S05"][0], "A1"),
             (SC["S05"][0], SC["S06"][0], "G1"), (SC["S06"][0], SC["S07"][0], "F#1"), (SC["S07"][0], LS("P3", 3), "E1"), (LS("P3", 3), SC["S08"][0], "B1"),
             (SC["S08"][0], LS("P3", 4) + 1.8, "G1"), (LS("P3", 4) + 1.8, LS("P3", 5), "A1"), (LS("P3", 6), B["acrossIn"], "D2"), (B["acrossIn"], DEV, "B1"),
             (DEV, SC["S11"][0], "B1"), (SC["S11"][0], B["connectIn"], "G1"), (B["connectIn"], SC["S12"][0], "D2"), (SC["S12"][0], LS("P4", 4), "A1"),
             (LS("P4", 4), SC["S13"][0], "B1"), (SC["S13"][0], LS("P4", 6), "G1"), (LS("P4", 6), B["permDenied"], "E1"), (SC["S15"][0], B["runComplete"], "B1"),
             (B["runComplete"], SC["S16"][0], "D2"), (B["teamIn"], LS("P5", 2), "F#1"), (LS("P5", 2), LE("P5", 2) + 0.4, "E1"), (LE("P5", 2) + 0.4, HERO, "A1"),
             (HERO, LS("P5", 4), "D2"), (LS("P5", 4), LS("P6", 0) - 0.3, "B1")]


def root_at(x):
    for a, b, nm in BASS_ROOT:
        if a <= x < b:
            return nm
    return None


# Act 2: the pulse begins one bar after "Navis" (the bloom breathes first), quarter-note heartbeat.
for x in grid(NAVIS + 4 * BEAT_S, SC["S05"][0] - 0.2, BEAT_S):
    k = (x - NAVIS) / (SC["S05"][0] - NAVIS)
    put(pulse, K, x, 0.55 + 0.35 * k)
for x in grid(SC["S04"][0], SC["S05"][0] - 0.3, BEAT_S / 2):
    nm = root_at(x)
    if nm:
        put(pulse, bass_note(nm, BEAT_S / 2 * 0.85, 0.35 + 0.25 * ((x - SC["S04"][0]) / 9)), x)
# Act 3: half-time, warm: kick on bar downbeats, long bass notes.
for x in grid(SC["S05"][0], LS("P3", 5) - 0.4, BEAT_S * 2):
    put(pulse, K, x, 0.45)
for x in grid(SC["S05"][0], LS("P3", 5) - 0.4, BEAT_S * 2):
    nm = root_at(x)
    if nm:
        put(pulse, bass_note(nm, BEAT_S * 1.8, 0.4, 380), x)
for x in grid(LS("P3", 6) - 0.04, DEV - 0.2, BEAT_S):  # the company acts: the pulse returns, on the beat
    put(pulse, K, x, 0.6)
    nm = root_at(x)
    if nm:
        put(pulse, bass_note(nm, BEAT_S * 0.9, 0.45), x)
# Act 4: precise developer rhythm; thinner under the key lines; stops for the permission check.
KEYS4 = [(LS("P4", 5) - 0.1, LE("P4", 6) + 0.2)]
for x in grid(DEV + 0.3, SC["S14"][0] + 0.4, BEAT_S):
    under_key = any(a <= x <= b for a, b in KEYS4)
    put(pulse, K, x, 0.5 if under_key else 0.7)
for x in grid(DEV + 0.3, SC["S14"][0] + 0.4, BEAT_S / 2):
    nm = root_at(x)
    if nm:
        put(pulse, bass_note(nm, BEAT_S / 2 * 0.7, 0.42, 600), x)
for x in grid(SC["S14"][0] + 0.4, B["permDenied"], BEAT_S * 2):  # slow down: half-time while the request is checked
    put(pulse, K, x, 0.45)
for x in grid(SC["S15"][0] + 0.05, SC["S16"][0] - 0.1, BEAT_S):  # the agent does the work
    put(pulse, K, x, 0.6)
    nm = root_at(x)
    if nm:
        put(pulse, bass_note(nm, BEAT_S * 0.45, 0.4, 600), x)
# Act 5: solo (none) → team (heartbeat) → company (full) ; stops under "Same facts…"
for x in grid(B["teamIn"], LE("P5", 2) + 0.4, BEAT_S * 2):
    put(pulse, K, x, 0.4)
for x in grid(LE("P5", 2) + 0.4, LS("P6", 0) - 0.4, BEAT_S):
    k = min(1, (x - LE("P5", 2)) / 3)
    put(pulse, K, x, 0.4 + 0.3 * k)
    nm = root_at(x)
    if nm:
        put(pulse, bass_note(nm, BEAT_S * 0.9, 0.35 + 0.15 * k, 480), x)
# Act 6: no rhythm — a deep sub swell under the thesis.
sub = osc(hz("B0"), int(6 * SR), "sine") * 0.6 + osc(hz("B1"), int(6 * SR), "sine") * 0.2
put(pulse, stereo(sub * env_adsr(int(6 * SR), 2.0, 1.0, 0.8, 2.5), 0), THESIS)
sub2 = osc(hz("D1"), int(8 * SR), "sine") * 0.6 + osc(hz("D2"), int(8 * SR), "sine") * 0.22
put(pulse, stereo(sub2 * env_adsr(int(8 * SR), 2.5, 1.0, 0.8, 3.0), 0), LE("P7", 2))
pulse = reverb(pulse, IR_ROOM, 0.12)
pulse = automate(pulse, [(0, -8), (END - 1, -8), (END, -90)])

# ---- RHYTHM: plucked arps + ticks -------------------------------------------------------------
ARP = {"Dmaj9": ["D4", "A4", "C#5", "E5", "F#5", "E5", "C#5", "A4"], "Bm11": ["B3", "F#4", "A4", "D5", "E5", "D5", "A4", "F#4"],
       "Gmaj9#11": ["G3", "D4", "F#4", "A4", "C#5", "A4", "F#4", "D4"], "Aadd9": ["A3", "E4", "B4", "C#5", "E5", "C#5", "B4", "E4"],
       "D/A": ["A3", "D4", "F#4", "A4", "E5", "A4", "F#4", "D4"], "Bm9": ["B3", "D4", "F#4", "A4", "C#5", "A4", "F#4", "D4"],
       "Gmaj7": ["G3", "B3", "D4", "F#4", "B4", "F#4", "D4", "B3"], "Em9": ["E4", "G4", "B4", "D5", "F#5", "D5", "B4", "G4"],
       "Gmaj9": ["G3", "B3", "D4", "F#4", "A4", "F#4", "D4", "B3"], "Dmaj9/F#": ["F#3", "A3", "D4", "E4", "A4", "E4", "D4", "A3"]}


def chord_at(x):
    for a, b, nm, *_ in seq:
        if a <= x < b:
            return nm
    return None


arp = np.zeros((N, 2))
step = BEAT_S / 4


def arp_run(a, b, level, every=1, start_level=None):
    i = 0
    for x in grid(a, b, step):
        nm = chord_at(x)
        if nm in ARP and i % every == 0:
            note = ARP[nm][(i // every) % 8]
            k = 1.0 if start_level is None else start_level + (level - start_level) * min(1, (x - a) / max(0.1, b - a))
            acc = 1.0 if i % 4 == 0 else 0.72
            put(arp, pluck(note, (level if start_level is None else k) * acc, 0.35 * np.sin(i * 0.9)), x)
        i += 1


arp_run(B["iconsIn"], B["flowMemory"], 0.35, every=2, start_level=0.12)          # the systems arrive: 8ths, growing
arp_run(B["flowMemory"], B["flowLearning"] + 0.1, 0.5, every=1, start_level=0.3)  # memory → context → intelligence: 16ths
arp_run(LS("P3", 6) - 0.04, B["acrossIn"] + 0.6, 0.28, every=2)                  # the company acts
arp_run(DEV + 0.3, LS("P4", 5) - 0.2, 0.55, every=1)                             # the developer section
arp_run(LS("P4", 5) - 0.2, LE("P4", 6) + 0.2, 0.22, every=2)                     # thinner under the key lines
arp_run(LE("P4", 6) + 0.2, SC["S14"][0] + 0.3, 0.5, every=1)
arp_run(SC["S15"][0] + 0.05, B["runComplete"] + 0.4, 0.45, every=1)                   # the work, then on record
arp_run(SC["S16"][0] + 0.1, B["teamIn"], 0.25, every=4)                          # solo: one voice
arp_run(B["teamIn"], LE("P5", 2) + 0.4, 0.3, every=2)                            # team: more
arp_run(LE("P5", 2) + 0.4, LS("P6", 0) - 0.4, 0.4, every=1)                      # company: the ensemble
rhythm += pingpong(arp, BEAT_S * 0.75, fb=0.38, mix=0.32)
tk = np.zeros((N, 2))
for a, b, lvl in [(B["flowMemory"], B["flowLearning"], 0.25), (DEV + 0.3, LS("P4", 5) - 0.2, 0.3), (LE("P4", 6) + 0.2, SC["S14"][0] + 0.3, 0.3),
                  (SC["S15"][0] + 0.05, SC["S16"][0] - 0.1, 0.25), (LE("P5", 2) + 0.4, LS("P6", 0) - 0.4, 0.22)]:
    for i, x in enumerate(grid(a, b, BEAT_S / 2)):
        put(tk, tick(lvl * (1.0 if i % 2 else 0.55), 0.45 if i % 2 else -0.3), x + BEAT_S / 4 if i % 2 == 0 else x)
rhythm += tk
rhythm = peaking(rhythm, 2800, -3.0, 0.8)
rhythm = reverb(rhythm, IR_ROOM, 0.22)
rhythm = automate(rhythm, [(0, -10), (END, -10)])

# ---- TEXTURE: reverse swells into reveals, micro-textures, the permission tone ------------------
put(texture, reverse_swell("Dmaj9", 1.7, 1.0), NAVIS - 1.7)                     # into "Navis"
for cut, chord in [(SC["S05"][0], "Gmaj9"), (DEV, "Bm9"), (HERO, "Dmaj9"), (THESIS, "Bm9")]:
    put(texture, reverse_swell(chord, 1.1, 0.55), cut - 1.1)
    put(texture, noise_swell(0.9, 400, 5000, 0.05, 3.0), cut - 0.9)
# Digital micro-texture: sparse, quiet glints during the data flow and the developer section.
for a, b, dens in [(B["signalsOut"], SC["S05"][0] - 0.5, 0.45), (DEV + 0.5, SC["S14"][0], 0.25), (SC["S15"][0], SC["S16"][0], 0.25)]:
    for x in grid(a, b, BEAT_S / 4):
        if rng.random() < dens:
            n = int(0.03 * SR)
            tt = np.arange(n) / SR
            f = rng.choice([hz("A6"), hz("D7"), hz("E7"), hz("F#7")])
            g = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.008) * 0.12
            put(texture, stereo(g, rng.uniform(-0.8, 0.8)), x)
# DENIED: a low-frequency tonal shift — serious, not a game error. D → C# in the low register, dark cluster.
n = int(2.2 * SR)
tt = np.arange(n) / SR
f = hz("D2") + (hz("C#2") - hz("D2")) * np.clip(tt / 0.6, 0, 1)
tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR) + 0.25 * np.sin(2 * np.pi * np.cumsum(f * 3) / SR)
tone = np.tanh(1.5 * tone) * env_adsr(n, 0.08, 0.4, 0.7, 1.2)
cluster = lp(osc(hz("G2"), n, "saw") + osc(hz("Ab2"), n, "saw") * 0.7, 380) * env_adsr(n, 0.2, 0.4, 0.6, 1.2) * 0.35
put(texture, stereo(tone * 0.55 + cluster, 0), B["permDenied"] - 0.02)
texture = reverb(texture, IR_HALL, 0.4)
texture = automate(texture, [(0, -6), (END - 0.5, -6), (END, -90)])

# ---- RESOLVE: mallet motifs at the human and final moments ----------------------------------
for t0, notes, lvl in [
    (LS("P3", 0) + 0.2, ["F#5", "A5", "D6"], 0.35),          # inside a company — people
    (LS("P3", 6) - 0.02, ["A5", "C#6", "E6", "F#6"], 0.36),  # then the company acts
    (B["runComplete"] - 0.05, ["D5", "F#5", "A5"], 0.32),         # the run is on record
    (LS("P6", 3) - 0.15, ["E5", "A5", "C#6"], 0.42),         # one understanding
    (LS("P6", 4) - 0.05, ["F#5", "D6"], 0.48),               # two ways in
    (LS("P7", 3) + 0.05, ["D5", "A5"], 0.3),                 # what your company knows
    (LS("P8", 1) - 0.1, ["D6"], 0.1),                        # the tail under the tagline: barely there
]:
    for k, nm in enumerate(notes):
        put(resolve, mallet(nm, lvl * (0.85 ** k), (-0.35, 0.35, 0.0, 0.2)[k % 4], 2.6), t0 + k * BEAT_S / 2)
resolve = peaking(resolve, 2800, -3.0, 0.8)
resolve = reverb(resolve, IR_HALL, 0.5)
resolve = automate(resolve, [(0, -6), (END - 0.6, -6), (END, -90)])

# ------------------------------------------------------------------ write
os.makedirs(OUT, exist_ok=True)
STEMS = {"bed": bed, "pulse": pulse, "harmony": harmony, "rhythm": rhythm, "texture": texture, "resolve": resolve}


def write_wav(path, x):
    y = np.clip(x, -1, 1)
    pcm = (y * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


peak = max(np.abs(x).max() for x in STEMS.values())
scale = 0.89 / peak  # one shared scale keeps the stems' relative balance as composed
for k, x in STEMS.items():
    hp_x = hp(x, 28, 2)  # no sub-sonic rumble
    write_wav(os.path.join(OUT, f"{k}.wav"), hp_x * scale)
mix = sum(hp(x, 28, 2) for x in STEMS.values())
write_wav(os.path.join(OUT, "score-mixdown.wav"), mix * (0.89 / np.abs(mix).max()))
print(f"stems {list(STEMS)} · {END:.2f} s · scale {20 * np.log10(scale):+.1f} dB · {OUT}")
