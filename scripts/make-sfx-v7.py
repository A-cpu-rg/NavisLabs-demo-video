#!/usr/bin/env python3
"""V7 SFX library, synthesized in-project (48 kHz mono WAV → public/sfx/temp/v7/<name>.wav).

Felt, subtle, realistic, premium: physical keys and a trackpad with a small room, small precise
confirmations, a serious low tone for a refusal — no game sounds, no booms, no whoosh on ordinary
moves. Every sound is generated here (no samples), so nothing carries third-party rights.
Each file is peak-normalized to −3 dBFS; the film sets each sound's level in the audio map
(navislabs_v8_audio_map.json → sfx.library[*].gain_db) and per event (src/config/beats.ts).
ElevenLabs Sound Effects versions (scripts/elevenlabs-generate.py) drop into public/sfx/final/v7/
under the same names and replace these with no code change.
"""
import os
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "sfx", "temp", "v7")
SR = 48000
rng = np.random.default_rng(21)


def n_(s):
    return int(s * SR)


def t_(n):
    return np.arange(n) / SR


def lp(x, f, o=2):
    return sosfilt(butter(o, min(f, SR * 0.45), "low", fs=SR, output="sos"), x)


def hp(x, f, o=2):
    return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, o=2):
    return sosfilt(butter(o, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos"), x)


def room(x, rt=0.35, wet=0.18, seed=3):
    r = np.random.default_rng(seed)
    n = n_(rt)
    ir = r.standard_normal(n) * np.exp(-6.91 * t_(n) / rt)
    ir = lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    y = fftconvolve(x, ir)[: len(x)]
    return x * (1 - wet) + y * wet


def hall(x, rt=1.8, wet=0.3, seed=5):
    return room(x, rt, wet, seed)


def pad(x, s):
    return np.concatenate([x, np.zeros(n_(s))])


def mix(*xs):
    """Sum signals of different lengths (shorter ones padded with silence)."""
    out = np.zeros(max(len(x) for x in xs))
    for x in xs:
        out[: len(x)] += x
    return out


def ins(buf, t, sig):
    """Mix sig into buf at t seconds, growing buf if needed."""
    i = n_(t)
    if i + len(sig) > len(buf):
        buf = np.concatenate([buf, np.zeros(i + len(sig) - len(buf))])
    buf[i:i + len(sig)] += sig
    return buf


def tone(f, dur, decay, attack=0.002):
    n = n_(dur)
    t = t_(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / decay) * np.minimum(1, t / attack)


def fm_bell(f, dur, decay, ratio=2.0, index=1.6):
    n = n_(dur)
    t = t_(n)
    idx = index * np.exp(-t / 0.12) + 0.15
    return np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t)) * np.exp(-t / decay) * np.minimum(1, t / 0.003)


def click_transient(dur=0.012, lo=1500, hi=7000, tau=0.0018):
    n = n_(dur)
    return bp(rng.standard_normal(n), lo, hi) * np.exp(-t_(n) / tau)


def key(seed, body_f=210, bright=(2500, 9000)):
    r = np.random.default_rng(seed)
    n = n_(0.12)
    t = t_(n)
    down = bp(r.standard_normal(n), *bright) * np.exp(-t / 0.0025) * 0.9
    thock = np.sin(2 * np.pi * body_f * (1 + 0.04 * r.random()) * t) * np.exp(-t / 0.012) * 0.55
    up = np.zeros(n)
    k = n_(0.045 + 0.01 * r.random())
    up[k:] = (bp(r.standard_normal(n - k), 3000, 9000) * np.exp(-t[: n - k] / 0.0018)) * 0.35
    return room(down + thock + up, 0.25, 0.12, seed)


def norm(x, peak_db=-3.0):
    x = x - np.mean(x[:64]) * 0
    x = x * np.minimum(1, t_(len(x)) / 0.0008)            # no click at the start
    tail = n_(0.01)
    x[-tail:] *= np.linspace(1, 0, tail)                   # nor at the end
    return x / (np.abs(x).max() + 1e-12) * 10 ** (peak_db / 20)


S = {}
# KEYBOARD — four laptop keys (scissor switch, small room).
for i, (f, br) in enumerate([(210, (2500, 9000)), (190, (2200, 8000)), (235, (2800, 9500)), (200, (2000, 7500))]):
    S[f"key{i + 1}"] = key(100 + i, f, br)
# TERMINAL — Enter: a bigger key with more body; checkpoint recorded: two soft ticks and a low confirm.
n = n_(0.25)
t = t_(n)
S["enter"] = room(bp(rng.standard_normal(n), 1800, 8000) * np.exp(-t / 0.003) + np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.02) * 0.8, 0.3, 0.16)
sv = pad(click_transient(0.02, 3000, 9000) * 0.5, 0.3)
sv = ins(sv, 0.07, click_transient(0.02, 3000, 9000) * 0.4)
sv = ins(sv, 0.1, tone(587.3, 0.25, 0.09) * 0.35 + tone(880, 0.25, 0.07) * 0.18)
S["save"] = room(sv, 0.4, 0.2)
# UI CLICK — a trackpad press and release.
c = np.zeros(n_(0.14))
c = ins(c, 0, click_transient(0.012, 1200, 6000, 0.0016))
c = ins(c, 0, tone(260, 0.04, 0.006) * 0.4)
c = ins(c, 0.055, click_transient(0.012, 2000, 8000, 0.0012) * 0.55)
S["click"] = room(c, 0.25, 0.12)
# DATA ARRIVAL — a tiny glassy tick.
S["data"] = hall(mix(tone(2349, 0.18, 0.022) * 0.7, tone(4698, 0.18, 0.01) * 0.25, click_transient(0.006, 5000, 12000) * 0.15), 0.6, 0.18)
# SOURCE APPEAR — a soft chip "pop": a short upward glide with air.
n = n_(0.2)
t = t_(n)
f = 900 + 500 * np.minimum(1, t / 0.04)
S["source"] = hall(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035) * 0.6 + bp(rng.standard_normal(n), 3000, 9000) * np.exp(-t / 0.01) * 0.12, 0.7, 0.2)
# MCP CONNECT — two soft rising tones (connected); a lit surface: one small tick-tone.
x = pad(fm_bell(659.3, 0.5, 0.22, 2.0, 1.2) * 0.6, 0.5)
x = ins(x, 0.09, fm_bell(987.8, 0.5, 0.3, 2.0, 1.0) * 0.55)
S["connect"] = hall(x, 1.4, 0.3)
S["surface"] = hall(mix(tone(1318.5, 0.25, 0.03) * 0.6, tone(2637, 0.25, 0.012) * 0.2, click_transient(0.006, 4000, 10000) * 0.12), 0.8, 0.22)
# API RESPONSE — three quick data glints settling into one tone.
x = np.zeros(n_(0.45))
for k, (tt, ff) in enumerate([(0, 1760), (0.045, 2217.5), (0.09, 2637)]):
    x = ins(x, tt, tone(ff, 0.12, 0.015) * 0.45)
x = ins(x, 0.13, tone(1318.5, 0.3, 0.09) * 0.4)
S["api"] = hall(x, 0.9, 0.22)
# CONTEXT RETRIEVAL — a short stream of fine ticks rising into a soft tone (information gathering).
x = np.zeros(n_(0.65))
for k in range(12):
    tt = 0.03 * k + 0.005 * rng.random()
    x = ins(x, tt, bp(rng.standard_normal(n_(0.03)), 3000 + 300 * k, 9000 + 300 * k) * np.exp(-t_(n_(0.03)) / 0.003) * (0.12 + 0.03 * k))
x = ins(x, 0.34, tone(1174.7, 0.3, 0.1) * 0.35 + tone(1760, 0.3, 0.08) * 0.15)
S["retrieve"] = hall(x, 1.0, 0.25)
# PERMISSION DENIED — serious, low: two soft low notes a semitone apart, dark, no buzzer.
n = n_(0.9)
t = t_(n)
lo = np.sin(2 * np.pi * 146.8 * t) * np.exp(-t / 0.35) + 0.4 * np.sin(2 * np.pi * 293.7 * t) * np.exp(-t / 0.2)
lo2 = np.zeros(n)
k = n_(0.12)
lo2[k:] = (np.sin(2 * np.pi * 138.6 * t[: n - k]) * np.exp(-t[: n - k] / 0.4) + 0.35 * np.sin(2 * np.pi * 277.2 * t[: n - k]) * np.exp(-t[: n - k] / 0.22))
S["deny"] = hall(np.tanh(1.3 * (lo * 0.6 + lo2 * 0.7)) * np.minimum(1, t / 0.006), 1.2, 0.22)
# APPROVE — a crisp press, then a small positive interval.
x = np.zeros(n_(0.6))
x = ins(x, 0, click_transient(0.014, 1500, 7000, 0.002) * 0.8)
x = ins(x, 0, tone(220, 0.05, 0.01) * 0.45)
x = ins(x, 0.06, fm_bell(880, 0.45, 0.16, 2.0, 0.9) * 0.4)
x = ins(x, 0.11, fm_bell(1318.5, 0.45, 0.2, 2.0, 0.8) * 0.32)
S["approve"] = hall(x, 1.1, 0.24)
# SEND — a short, soft upward air (not a whoosh).
n = n_(0.42)
t = t_(n)
nz = rng.standard_normal(n)
x = np.zeros(n)
for i in range(0, n, 480):
    seg = nz[i:i + 480]
    fc = 900 + 4500 * (i / n)
    x[i:i + 480] = bp(seg, fc * 0.6, fc * 1.6)
S["sent"] = hall(x * np.sin(np.pi * t / t[-1]) ** 1.5 * 0.5, 0.8, 0.25)
# GMAIL CONFIRM — a gentle two-tone chime, satisfying but subtle (D6 → A6: in the score's key).
x = pad(fm_bell(1174.7, 0.8, 0.28, 2.0, 1.1) * 0.5, 0.6)
x = ins(x, 0.12, fm_bell(1760, 0.8, 0.4, 2.0, 0.9) * 0.45)
S["gmail"] = hall(x, 1.6, 0.3)
# RUN START — a soft low pulse with a rising tone.
n = n_(0.5)
t = t_(n)
f = 330 + 110 * np.minimum(1, t / 0.18)
S["run"] = hall(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * 0.4 + np.sin(2 * np.pi * 110 * t) * np.exp(-t / 0.08) * 0.5, 1.0, 0.2)
# RUN COMPLETE — a resolving three-note chime (D F# A).
x = pad(np.zeros(1), 1.3)
for k, f in enumerate([587.3, 740.0, 880.0]):
    x = ins(x, 0.07 * k, fm_bell(f, 0.9, 0.32, 2.0, 0.9) * 0.4)
S["complete"] = hall(x, 1.6, 0.3)
# PRODUCT REVEAL — a low bloom with a high harmonic shimmer (under the music's open).
n = n_(2.4)
t = t_(n)
bloom = (np.sin(2 * np.pi * 73.4 * t) * 0.8 + np.sin(2 * np.pi * 146.8 * t) * 0.35 + np.sin(2 * np.pi * 220 * t) * 0.18) * (np.minimum(1, t / 0.18)) * np.exp(-t / 0.9)
sh = sum(fm_bell(f, 2.4, 0.9, 2.0, 0.6) * a for f, a in [(1174.7, 0.12), (1760, 0.08), (2217.5, 0.06)])
S["reveal"] = hall(np.tanh(1.2 * bloom) * 0.8 + sh, 2.2, 0.35)
# TRANSITION — soft filtered air, low and short.
n = n_(0.7)
t = t_(n)
S["air"] = hall(lp(bp(rng.standard_normal(n), 200, 3000), 1800) * np.sin(np.pi * t / t[-1]) ** 2 * 0.6, 1.0, 0.3)
# END REVEAL — a deep, soft tone bloom with a long tail (quiet).
n = n_(3.2)
t = t_(n)
S["end"] = hall((np.sin(2 * np.pi * 73.4 * t) * 0.7 + np.sin(2 * np.pi * 110 * t) * 0.3 + fm_bell(587.3, 3.2, 1.4, 2.0, 0.5) * 0.25) * np.minimum(1, t / 0.25) * np.exp(-t / 1.2), 2.4, 0.35)

# --- V8 additions (still in-project temp sounds) -------------------------------------------
# WHOOSH — a very subtle cinematic air pass for large transitions (band-passed noise, sweeping down).
n = n_(0.75)
t = t_(n)
nz = rng.standard_normal(n)
x = np.zeros(n)
for i in range(0, n, 480):
    fc = 3200 - 2400 * (i / n)
    x[i:i + 480] = bp(nz[i:i + 480], fc * 0.5, fc * 1.4)
S["whoosh"] = hall(x * np.abs(np.sin(np.pi * t / t[-1])) ** 2.2 * 0.5, 1.2, 0.3)
# REVERSE WHOOSH — a soft swell that rises into a reveal.
S["rwhoosh"] = hall((lp(rng.standard_normal(n_(0.9)), 2200) * (t_(n_(0.9)) / 0.9) ** 2.4) * 0.5, 0.8, 0.25)
# SWEEP — connected systems appearing: one soft interface sweep, not a tick per tile.
n = n_(0.6)
t = t_(n)
f = 600 + 1800 * (t / t[-1]) ** 0.7
S["sweep"] = hall(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) * 0.25 + bp(rng.standard_normal(n), 4000, 9000) * np.sin(np.pi * t / t[-1]) ** 2 * 0.08, 1.0, 0.3)
# LOCK — information locking into place (the shared understanding): a soft low thud + two settling tones.
x = pad(tone(110, 0.25, 0.06) * 0.5 + tone(220, 0.25, 0.04) * 0.2, 0.9)
x = ins(x, 0.05, fm_bell(587.3, 0.9, 0.3, 2.0, 0.6) * 0.3)
x = ins(x, 0.12, fm_bell(880, 0.9, 0.35, 2.0, 0.5) * 0.22)
S["lock"] = hall(x, 1.6, 0.3)
# WORKSPACE CREATED — a small, warm confirmation (two notes, A then D).
x = pad(fm_bell(880, 0.6, 0.18, 2.0, 0.7) * 0.4, 0.4)
x = ins(x, 0.09, fm_bell(1174.7, 0.6, 0.24, 2.0, 0.6) * 0.32)
S["workspace"] = hall(x, 1.0, 0.24)

os.makedirs(OUT, exist_ok=True)
for k, x in S.items():
    y = norm(np.asarray(x, dtype=np.float64))
    with wave.open(os.path.join(OUT, f"{k}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype("<i2").tobytes())
print(f"{len(S)} sounds → {OUT}: {', '.join(S)}")
