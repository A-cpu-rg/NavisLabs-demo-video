#!/usr/bin/env python3
"""
Generate the TEMP audio for the NavisLabs launch film.

    python3 scripts/make-temp-audio.py            # everything
    python3 scripts/make-temp-audio.py vo         # voiceover only
    python3 scripts/make-temp-audio.py music sfx  # music and SFX only

Everything written here is a placeholder:
  - voiceover/temp/Lxx.wav  macOS `say` (a neutral system voice), fitted to
    each line's window in navislabs_v5_audio_map.json. NOT the founder's voice.
  - music/temp/score.wav    a synthesized sketch of the six-section score.
  - sfx/temp/*.wav          synthesized keyboard, click, selection and
    confirmation sounds.

Final audio goes in the matching .../final/ paths and wins automatically
(see src/config/audioMap.ts). This script never touches final/ files and needs
no API key. An ElevenLabs script, if added later, must read ELEVENLABS_API_KEY
from the environment and never write the key to disk.

Requires: numpy, /usr/bin/say, ffmpeg.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
MAP = json.load(open(os.path.join(ROOT, os.environ.get("AUDIO_MAP", "navislabs_v6_audio_map.json"))))
SR = 48000
VOICE = os.environ.get("TEMP_VO_VOICE", "Daniel")
RATE = int(os.environ.get("TEMP_VO_RATE", "172"))
FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
FFPROBE = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"
rng = np.random.default_rng(7)


def out(rel):
    p = os.path.join(PUBLIC, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def write_wav(path, data):
    """data: float array, mono (n,) or stereo (n, 2), -1..1."""
    data = np.clip(data, -1, 1)
    if data.ndim == 1:
        data = data[:, None]
    pcm = (data * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(pcm.shape[1])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def duration(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


# ---------------------------------------------------------------- voiceover

def make_vo():
    report = []
    with tempfile.TemporaryDirectory() as tmp:
        for line in MAP["voiceover"]:
            if not line.get("text") or line.get("start_s") is None:
                continue
            aiff = os.path.join(tmp, f"{line['id']}.aiff")
            # `say` reads the text as-is; dashes become pauses, which is what we want.
            subprocess.run(["say", "-v", VOICE, "-r", str(RATE), "-o", aiff, line["text"]], check=True)
            natural = duration(aiff)
            window = line["ceiling_s"] - line["start_s"] - 0.1
            target = window
            tempo = 1.0
            if natural > target:
                tempo = min(natural / target, 1.45)
            dst = out(line["temp"])
            filters = [f"atempo={tempo:.4f}"] if tempo > 1.001 else []
            # Trim leading/trailing silence from `say`, then normalize every
            # line to the same speech loudness (-16 LUFS, -1.5 dBTP).
            filters = ["silenceremove=start_periods=1:start_threshold=-50dB"] + filters + [
                "areverse", "silenceremove=start_periods=1:start_threshold=-50dB", "areverse",
                "loudnorm=I=-16:TP=-1.5:LRA=7"]
            subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", aiff, "-af", ",".join(filters),
                            "-ar", str(SR), "-ac", "1", dst], check=True)
            report.append((line["id"], round(natural, 2), round(tempo, 2), round(duration(dst), 2), round(window, 2)))
    for r in report:
        print("VO %s natural %.2fs  tempo x%.2f  -> %.2fs  (window %.2fs)" % r)


# ---------------------------------------------------------------- SFX

def env(n, attack, decay):
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / decay)


def bandnoise(n, lo, hi):
    x = rng.standard_normal(n)
    f = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    f[(freqs < lo) | (freqs > hi)] = 0
    y = np.fft.irfft(f, n)
    return y / (np.abs(y).max() + 1e-9)


def tone(freq, n, phase=0.0):
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t + phase)


def norm(x, peak=0.9):
    return x / (np.abs(x).max() + 1e-9) * peak


def key_sound(seed_hi, body):
    n = int(0.09 * SR)
    click = bandnoise(n, 1800, seed_hi) * env(n, 0.0004, 0.006)
    thock = tone(body, n) * env(n, 0.001, 0.012) * 0.5
    tail = bandnoise(n, 400, 1800) * env(n, 0.002, 0.02) * 0.15
    return norm(click + thock + tail)


def make_sfx():
    lib = MAP["sfx"]["library"]
    write_wav(out(lib["key"]["temp"]), key_sound(6000, 180))
    write_wav(out(lib["key2"]["temp"]), key_sound(5200, 205))
    write_wav(out(lib["key3"]["temp"]), key_sound(6800, 160))
    # Return key: a heavier, longer thock.
    n = int(0.16 * SR)
    enter = bandnoise(n, 1200, 5000) * env(n, 0.0005, 0.01) + tone(120, n) * env(n, 0.001, 0.03) * 0.8 \
        + bandnoise(n, 200, 1200) * env(n, 0.002, 0.04) * 0.2
    write_wav(out(lib["enter"]["temp"]), norm(enter))
    # Trackpad/mouse click: two tiny transients.
    n = int(0.06 * SR)
    c = bandnoise(n, 2500, 9000) * env(n, 0.0002, 0.0025)
    c2 = np.zeros(n)
    off = int(0.018 * SR)
    c2[off:] = (bandnoise(n, 2000, 7000) * env(n, 0.0002, 0.002))[: n - off] * 0.5
    write_wav(out(lib["click"]["temp"]), norm(c + c2))
    # Selection: a soft high tick with a short shimmer.
    n = int(0.12 * SR)
    s = tone(2400, n) * env(n, 0.001, 0.02) * 0.6 + bandnoise(n, 4000, 10000) * env(n, 0.0005, 0.008) * 0.4
    write_wav(out(lib["select"]["temp"]), norm(s, 0.6))
    # Terminal execution: a low, short electrical blip.
    n = int(0.25 * SR)
    r = (tone(220, n) * 0.5 + tone(440, n) * 0.25) * env(n, 0.004, 0.05) + bandnoise(n, 3000, 8000) * env(n, 0.001, 0.01) * 0.2
    write_wav(out(lib["run"]["temp"]), norm(r, 0.7))
    # Confirmation: two soft sine notes (A5 then E6), no reverb tail drama.
    n = int(0.9 * SR)
    t1 = tone(880, n) * env(n, 0.004, 0.18)
    t2 = np.zeros(n)
    d = int(0.09 * SR)
    t2[d:] = (tone(1318.5, n) * env(n, 0.004, 0.25))[: n - d]
    write_wav(out(lib["confirm"]["temp"]), norm(t1 * 0.6 + t2 * 0.5, 0.6))
    # Sent: three rising notes, softer.
    n = int(1.3 * SR)
    sent = np.zeros(n)
    for i, f in enumerate([659.25, 987.77, 1318.5]):
        d = int(i * 0.075 * SR)
        sent[d:] += (tone(f, n) * env(n, 0.004, 0.3))[: n - d] * (0.6 - i * 0.1)
    write_wav(out(lib["sent"]["temp"]), norm(sent, 0.6))
    # Deny: a short, muted low two-note fall. Not a boom.
    n = int(0.6 * SR)
    deny = tone(196, n) * env(n, 0.003, 0.08) * 0.7
    d = int(0.11 * SR)
    deny[d:] += (tone(146.8, n) * env(n, 0.003, 0.14))[: n - d] * 0.7
    write_wav(out(lib["deny"]["temp"]), norm(deny, 0.6))
    # Notify: one soft, rounded two-note ping (a UI notification).
    n = int(0.7 * SR)
    ping = tone(1046.5, n) * env(n, 0.003, 0.09) * 0.5
    d = int(0.06 * SR)
    ping[d:] += (tone(1568.0, n) * env(n, 0.003, 0.14))[: n - d] * 0.35
    if "notify" in lib:
        write_wav(out(lib["notify"]["temp"]), norm(ping, 0.5))
    # Air: a very soft filtered breath for the two line transitions.
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    shape = np.sin(np.pi * np.clip(t / 1.4, 0, 1)) ** 2
    write_wav(out(lib["air"]["temp"]), norm(bandnoise(n, 300, 2500) * shape, 0.5))
    # --- V4 picture-lock additions (all quiet, physical, no whooshes) ---
    # MCP connect: two short rising sine tones (D6 → A6).
    n = int(0.5 * SR)
    con = tone(1174.7, n) * env(n, 0.003, 0.07) * 0.5
    d = int(0.07 * SR)
    con[d:] += (tone(1760.0, n) * env(n, 0.003, 0.12))[: n - d] * 0.4
    write_wav(out(lib["connect"]["temp"]), norm(con, 0.5))
    # Data retrieval: a soft, short filtered blip.
    n = int(0.22 * SR)
    ret = (tone(660, n) * 0.4 + tone(990, n) * 0.2) * env(n, 0.003, 0.04) + bandnoise(n, 2500, 6000) * env(n, 0.001, 0.015) * 0.15
    write_wav(out(lib["retrieve"]["temp"]), norm(ret, 0.45))
    # Save: one tiny high tick.
    n = int(0.08 * SR)
    write_wav(out(lib["save"]["temp"]), norm(tone(2637, n) * env(n, 0.0008, 0.012), 0.35))
    # Approve: a precise click with a soft body.
    n = int(0.12 * SR)
    ap = bandnoise(n, 2500, 9000) * env(n, 0.0002, 0.003) + tone(880, n) * env(n, 0.002, 0.03) * 0.35
    write_wav(out(lib["approve"]["temp"]), norm(ap, 0.6))
    # Gmail confirmation: a single soft tone.
    n = int(0.6 * SR)
    write_wav(out(lib["gmail"]["temp"]), norm(tone(1318.5, n) * env(n, 0.004, 0.16), 0.45))
    # Brand reveal: a low tonal lift (no hit) — D2 + A2 swelling in and out.
    n = int(2.4 * SR)
    tt = np.arange(n) / SR
    shape = np.sin(np.pi * np.clip(tt / 2.4, 0, 1)) ** 1.5
    br = (np.sin(2 * np.pi * 73.4 * tt) * 0.6 + np.sin(2 * np.pi * 110 * tt) * 0.3 + np.sin(2 * np.pi * 146.8 * tt) * 0.12) * shape
    write_wav(out(lib["brand"]["temp"]), norm(br, 0.55))
    # Data-flow texture: a very soft, slowly modulated band of air (ambience).
    n = int(8.4 * SR)
    tt = np.arange(n) / SR
    tex = bandnoise(n, 900, 3200) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.8 * tt)) * np.clip(tt / 1.0, 0, 1) * np.clip((8.4 - tt) / 1.0, 0, 1)
    write_wav(out(MAP["ambience"]["temp"]), norm(tex, 0.35))
    # Permission denied: quieter than before — a muted low fall.
    n = int(0.6 * SR)
    deny = tone(174.6, n) * env(n, 0.004, 0.07) * 0.6
    d = int(0.12 * SR)
    deny[d:] += (tone(130.8, n) * env(n, 0.004, 0.12))[: n - d] * 0.6
    write_wav(out(lib["deny"]["temp"]), norm(deny, 0.4))
    print("SFX: " + ", ".join(sorted(lib)))


# ---------------------------------------------------------------- music

def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    pitch, octave = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[pitch] + (octave - 4) * 12) / 12)


def smooth(x, k):
    if k <= 1:
        return x
    kern = np.ones(k) / k
    return np.convolve(x, kern, mode="same")


def make_music():
    """A temp score that follows the section times in navislabs_v5_audio_map.json."""
    total = float(MAP.get("duration_s", 100.0))
    N = int(total * SR)
    t = np.arange(N) / SR
    L = np.zeros(N)
    R = np.zeros(N)
    sec = {s["role"]: (s["from_s"], s["to_s"]) for s in MAP["music"]["sections"]}
    if "convergence" in sec:
        # Audio-production arc (restrained → emergence → human → technical →
        # convergence → conviction → resolve), rendered with the V4 generator.
        em, hu, te, co, cv, rs = sec["emergence"], sec["human"], sec["technical"], sec["convergence"], sec["conviction"], sec["resolve"]
        sec = {"ambient": sec["restrained"], "lift": (em[0], em[0] + 4.0), "pulse": (em[0] + 4.0, em[1]), "momentum": hu,
               "technical": te, "human": co, "build": cv, "resolve": rs}

    def add(sig, start, gain=1.0, pan=0.0):
        i = int(start * SR)
        if i >= N:
            return
        j = min(N, i + len(sig))
        seg = sig[: j - i] * gain
        L[i:j] += seg * (1 - max(0, pan))
        R[i:j] += seg * (1 + min(0, pan))

    def pad(freqs, start, end, attack=2.0, release=2.0, detune=0.6):
        n = int((end - start + release) * SR)
        tt = np.arange(n) / SR
        a = np.clip(tt / attack, 0, 1) * np.clip((end - start + release - tt) / release, 0, 1)
        sig = np.zeros(n)
        for f in freqs:
            for dv in (-detune, detune):
                sig += np.sin(2 * np.pi * (f + dv) * tt + rng.uniform(0, 6.28))
                sig += 0.25 * np.sin(2 * np.pi * 2 * (f + dv) * tt)
        return sig * a / (len(freqs) * 2)

    def pluck(f, dur=0.5, bright=0.3):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        sig = np.sin(2 * np.pi * f * tt) + bright * np.sin(2 * np.pi * 2 * f * tt) + 0.1 * np.sin(2 * np.pi * 3 * f * tt)
        return sig * np.clip(tt / 0.004, 0, 1) * np.exp(-tt / (dur / 4))

    def piano(f, dur=3.0):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        sig = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * tt) * np.exp(-tt * (1.2 + 0.9 * k)) for k in range(5))
        return sig * np.clip(tt / 0.003, 0, 1)

    if "momentum" in sec:
        # V4 picture lock: ambient, lift, pulse, momentum, technical, human, build, resolve.
        m1, m2, m3, m4, m5, m6, m7 = sec["ambient"], sec["pulse"], sec["lift"], sec["human"], sec["technical"], sec["build"], sec["resolve"]
        mo = sec["momentum"]
    else:
        m1, m2, m3, m4, m5, m6, m7 = (sec[k] for k in ("ambient", "pulse", "lift", "human", "technical", "build", "resolve"))
        mo = None

    if mo is not None:
        make_music_v4(t, N, L, R, sec, add, pad, pluck, piano, total)
        return

    # ATMOS: a low D drone through the whole film, level shaped by section.
    drone = (np.sin(2 * np.pi * note("D2") * t) * 0.5 + np.sin(2 * np.pi * note("A2") * t) * 0.3
             + np.sin(2 * np.pi * note("D3") * t) * 0.12) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * t))
    air = smooth(rng.standard_normal(N), 60)
    air /= np.abs(air).max()
    lvl = np.interp(t, [0, 3.0, m1[1], m2[1] - 0.8, m3[0], m4[0], m5[0], m6[0], m7[0], 98.4, 100],
                    [0, 0.07, 0.10, 0.12, 0.06, 0.06, 0.06, 0.07, 0.06, 0.0, 0.0])
    L += (drone * 0.8 + air * 0.25) * lvl
    R += (drone * 0.8 - air * 0.25) * lvl

    # ambient (0–15): almost nothing — a few distant glints.
    for _ in range(14):
        st = rng.uniform(2.0, m1[1] - 0.5)
        add(pluck(note(rng.choice(["A5", "D6", "E6"])), 1.1, 0.04), st, 0.012 + 0.02 * st / m1[1], pan=rng.uniform(-0.7, 0.7))

    sixteenth = 60 / 104 / 4
    arp = ["D4", "A4", "F#4", "A4", "E4", "A4", "F#4", "D5"]
    bass = ["D2", "D2", "B1", "G1", "A1", "A1", "D2", "G1"]

    def pulse(a, b, level, every_hat=True, with_bass=True, notes=arp):
        s0, i = a, 0
        while s0 < b:
            g = level(s0)
            if g > 0.01:
                add(pluck(note(notes[i % len(notes)]), 0.32, 0.4), s0, 0.042 * g, pan=0.25 if i % 2 else -0.25)
                if every_hat and i % 2 == 1:
                    hn = int(0.05 * SR)
                    hat = rng.standard_normal(hn) * np.exp(-np.arange(hn) / SR / 0.008)
                    add(hat - smooth(hat, 6), s0, 0.011 * g, pan=0.4)
                if with_bass and i % 16 == 0:
                    add(pad([note(bass[(i // 16) % len(bass)])], s0, s0 + 16 * sixteenth - 0.2, attack=0.05, release=0.3, detune=0.2), s0, 0.09 * g)
            s0 += sixteenth
            i += 1

    # pulse (15–30): a subtle pulse under the problem, no hats, falls away before the reveal.
    pulse(m2[0], m2[1], lambda x: float(np.interp(x, [m2[0], m2[0] + 4, m2[1] - 1.4, m2[1] - 0.6], [0.0, 0.35, 0.45, 0.0])), every_hat=False, with_bass=False, notes=["D4", "A4", "D4", "E4"])

    # lift (30.4–40): a soft low hit on the lockup, then a D add9 swell as the systems connect.
    n = int(2.5 * SR)
    tt = np.arange(n) / SR
    add(np.sin(2 * np.pi * 48 * tt) * np.exp(-tt / 0.5) * np.clip(tt / 0.01, 0, 1), m3[0] + 0.2, 0.2)
    add(pad([note("D3"), note("A3"), note("E4"), note("F#4")], m3[0], m3[1], attack=1.6, release=1.6), m3[0], 0.14)
    add(pad([note("D2")], m3[0], m3[1], attack=1.0, release=1.4), m3[0], 0.1)

    # human (40–57.4): warmer — wide pads, sparse piano.
    span = m4[1] - m4[0]
    prog = [["G3", "B3", "D4", "F#4"], ["D3", "F#3", "A3", "E4"], ["E3", "G3", "B3", "D4"], ["A2", "D3", "E3", "A3"]]
    step = span / len(prog)
    for k, ch in enumerate(prog):
        add(pad([note(c) for c in ch], m4[0] + k * step, m4[0] + (k + 1) * step, attack=1.2, release=1.4), m4[0] + k * step, 0.11)
    for k, nn in enumerate(["D5", "A4", "F#5", "E5", "B4", "D5", "A4", "F#5"]):
        add(piano(note(nn), 3.0), m4[0] + 0.5 + k * span / 8, 0.06, pan=-0.2)

    # technical (57.4–77.6): restrained developer rhythm.
    pulse(m5[0], m5[1], lambda x: float(np.interp(x, [m5[0], m5[0] + 2.0, m5[1] - 0.8, m5[1]], [0.3, 0.95, 0.95, 0])))

    # build (77.6–94): pads gather; the pulse returns softly under the hero shot.
    add(pad([note("D3"), note("A3"), note("D4"), note("E4")], m6[0] + 0.6, m6[1], attack=3.0, release=0.8), m6[0] + 0.6, 0.12)
    add(pad([note("G3"), note("B3"), note("D4"), note("F#4")], 84.0, m6[1], attack=2.0, release=0.8), 84.0, 0.08)
    pulse(81.2, m6[1] - 0.6, lambda x: float(np.interp(x, [81.2, 84.0, 90.5, 93.4], [0.0, 0.6, 0.5, 0.0])), with_bass=False)

    # resolve (94–100): one resolving piano chord on the end card, then silence.
    add(piano(note("D4"), 5.0), m7[0] + 0.1, 0.15)
    add(piano(note("A4"), 5.0), m7[0] + 0.12, 0.08)
    add(pad([note("D3"), note("A3")], m7[0], m7[0] + 2.4, attack=0.6, release=1.6), m7[0], 0.05)

    mix = np.stack([L, R], axis=1)
    gate = np.ones(N)
    for d in MAP["music"]["dips"]:
        gate[int(d["from_s"] * SR):int(d["to_s"] * SR)] = min(1.0, 10 ** (d["db"] / 20))
    gate = smooth(gate, int(0.05 * SR))
    mix *= gate[:, None]
    fade = np.clip(t / 2.0, 0, 1) * np.clip((98.4 - t) / 1.4, 0, 1)
    mix *= fade[:, None]
    mix = np.tanh(mix * 1.6) / np.tanh(1.6)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.7
    write_wav(out(MAP["music"]["temp"]), mix)
    print("Music: %.1fs stereo -> %s" % (total, MAP["music"]["temp"]))


def make_music_v4(t, N, L, R, sec, add, pad, pluck, piano, total=100.0):
    """V4 picture-lock temp score: one continuous arc, leaving room for the voice."""
    a0, lift, pulse_s, mom, tech, hum, build, res = (sec[k] for k in ("ambient", "lift", "pulse", "momentum", "technical", "human", "build", "resolve"))
    # bed: a low D drone, level shaped through the arc (almost silent at the start).
    drone = (np.sin(2 * np.pi * note("D2") * t) * 0.5 + np.sin(2 * np.pi * note("A2") * t) * 0.3) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * t))
    end_fade = max(d["from_s"] for d in MAP["music"]["dips"] if d["db"] <= -90)  # the silent end
    lvl = np.interp(t, [0, 4, a0[1], lift[1], pulse_s[1], mom[1], tech[1], hum[1], build[1], end_fade - 0.6, total], [0, 0.04, 0.06, 0.09, 0.08, 0.08, 0.07, 0.08, 0.09, 0.0, 0.0])
    L += drone * lvl
    R += drone * lvl
    # ambient: a few distant glints.
    for _ in range(8):
        st = rng.uniform(2.0, a0[1] - 0.8)
        add(pluck(note(rng.choice(["A5", "D6", "E6"])), 1.1, 0.04), st, 0.01, pan=rng.uniform(-0.7, 0.7))
    # lift: the brand's low tonal lift (no hit), then a soft D add9 pad.
    add(pad([note("D2"), note("A2")], lift[0] + 0.2, lift[1], attack=0.8, release=1.2), lift[0] + 0.2, 0.10)
    add(pad([note("D3"), note("A3"), note("E4")], lift[0] + 0.6, lift[1] + 1.0, attack=1.2, release=1.2), lift[0] + 0.6, 0.07)
    sixteenth = 60 / 104 / 4
    def arp(a, b, level, notes, hats=False, bass=None):
        s0, i = a, 0
        while s0 < b:
            g = level(s0)
            if g > 0.01:
                add(pluck(note(notes[i % len(notes)]), 0.3, 0.35), s0, 0.04 * g, pan=0.25 if i % 2 else -0.25)
                if hats and i % 2 == 1:
                    hn = int(0.05 * SR)
                    hat = rng.standard_normal(hn) * np.exp(-np.arange(hn) / SR / 0.008)
                    add(hat - smooth(hat, 6), s0, 0.009 * g, pan=0.4)
                if bass and i % 16 == 0:
                    add(pad([note(bass[(i // 16) % len(bass)])], s0, s0 + 16 * sixteenth - 0.2, attack=0.05, release=0.3, detune=0.2), s0, 0.08 * g)
            s0 += sixteenth
            i += 1
    # pulse: subtle, sparse.
    arp(pulse_s[0], pulse_s[1], lambda x: float(np.interp(x, [pulse_s[0], pulse_s[0] + 3, pulse_s[1]], [0.0, 0.35, 0.45])), ["D4", "A4", "D4", "E4"])
    # momentum: technical but light; pads underneath for the human edit.
    arp(mom[0], mom[1], lambda x: float(np.interp(x, [mom[0], mom[0] + 2, mom[1] - 0.6, mom[1]], [0.45, 0.6, 0.6, 0.2])), ["D4", "A4", "F#4", "A4", "E4", "A4", "F#4", "D5"], hats=False)
    add(pad([note("G3"), note("B3"), note("D4")], mom[0], mom[1], attack=2.0, release=1.0), mom[0], 0.06)
    # technical: precise developer rhythm with hats and bass.
    arp(tech[0], tech[1], lambda x: float(np.interp(x, [tech[0], tech[0] + 1.2, tech[1] - 0.6, tech[1]], [0.4, 0.9, 0.9, 0.3])), ["D4", "A4", "F#4", "A4", "E4", "A4", "F#4", "D5"], hats=True, bass=["D2", "D2", "B1", "G1"])
    # human: warmer pads and sparse piano.
    span = hum[1] - hum[0]
    prog = [["G3", "B3", "D4", "F#4"], ["D3", "F#3", "A3", "E4"], ["E3", "G3", "B3", "D4"], ["A2", "D3", "E3", "A3"]]
    for k, ch in enumerate(prog):
        add(pad([note(c) for c in ch], hum[0] + k * span / 4, hum[0] + (k + 1) * span / 4, attack=1.4, release=1.4), hum[0] + k * span / 4, 0.10)
    for k, nn in enumerate(["D5", "A4", "F#5", "E5", "B4", "D5", "A4", "F#5"]):
        add(piano(note(nn), 3.0), hum[0] + 0.6 + k * span / 8, 0.05, pan=-0.2)
    # build: human and technical motifs merge (pads + a soft pulse).
    add(pad([note("D3"), note("A3"), note("D4"), note("E4")], build[0], build[1], attack=2.0, release=0.8), build[0], 0.11)
    arp(build[0] + 1.0, build[1] - 0.6, lambda x: float(np.interp(x, [build[0] + 1.0, build[0] + 3.0, build[1] - 1.0, build[1] - 0.6], [0.0, 0.45, 0.45, 0.0])), ["D4", "A4", "E4", "A4"])
    # resolve: one piano chord on the end card, then silence.
    add(piano(note("D4"), 5.0), res[0] + 0.1, 0.13)
    add(piano(note("A4"), 5.0), res[0] + 0.12, 0.07)
    mix = np.stack([L, R], axis=1)
    gate = np.ones(N)
    for d in MAP["music"]["dips"]:
        gate[int(d["from_s"] * SR):int(d["to_s"] * SR)] = min(1.0, 10 ** (d["db"] / 20))
    gate = smooth(gate, int(0.05 * SR))
    mix *= gate[:, None]
    fade = np.clip(t / 2.0, 0, 1) * np.clip((end_fade - t) / 1.4, 0, 1)
    mix *= fade[:, None]
    mix = np.tanh(mix * 1.6) / np.tanh(1.6)
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.7
    write_wav(out(MAP["music"]["temp"]), mix)
    print("Music (temp): %.1fs stereo -> %s" % (total, MAP["music"]["temp"]))


if __name__ == "__main__":
    parts = sys.argv[1:] or ["vo", "music", "sfx"]
    if "vo" in parts:
        make_vo()
    if "sfx" in parts:
        make_sfx()
    if "music" in parts:
        make_music()
