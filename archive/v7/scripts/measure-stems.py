#!/usr/bin/env python3
"""Measures the film's audio stems separately (ITU-R BS.1770 K-weighting, EBU R128 gating).

  python3 scripts/measure-stems.py <label> <voice.wav> <music.wav> <sfx.wav> [mix.mp4|wav] [--timeline navislabs_v7_voice_timeline.json] [--out file.json]

For each stem: integrated loudness (LUFS), sample peak. Then, against the measured speech
windows (the voice timeline): the voice's and the music's loudness while the founder speaks,
the music's loudness in the founder's pauses, and the voice-to-music ratio under speech (LU).
Stems are rendered by Remotion with the `stem` prop (audio only), before mastering; the
mastering gain (scripts/master-audio.py) applies equally to all of them.
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import lfilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = "/opt/homebrew/bin/ffmpeg"
SR = 48000

args = sys.argv[1:]
opts = {}
while "--timeline" in args or "--out" in args:
    for k in ("--timeline", "--out"):
        if k in args:
            i = args.index(k)
            opts[k] = args[i + 1]
            del args[i:i + 2]
label, files = args[0], args[1:]
names = ["voice", "music", "sfx", "mix"][: len(files)]
tl = json.load(open(os.path.join(ROOT, opts.get("--timeline", "navislabs_v7_voice_timeline.json"))))


def load(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


# BS.1770 K-weighting at 48 kHz (pre-filter shelf + RLB high-pass).
B1, A1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
B2, A2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]


def kweight(x):
    return lfilter(B2, A2, lfilter(B1, A1, x, axis=0), axis=0)


def power_blocks(k, step=0.1, win=0.4):
    n, h = int(win * SR), int(step * SR)
    ms = (k ** 2).sum(axis=1)
    c = np.concatenate([[0], np.cumsum(ms)])
    starts = np.arange(0, max(1, len(ms) - n), h)
    return starts / SR, (c[starts + n] - c[starts]) / n


def lufs(p):
    return -0.691 + 10 * np.log10(p) if p > 0 else -120.0


def integrated(k):
    _, p = power_blocks(k)
    p = p[lufs_arr(p) > -70]
    if not len(p):
        return -120.0
    rel = lufs(p.mean()) - 10
    p = p[lufs_arr(p) > rel]
    return round(lufs(p.mean()), 2) if len(p) else -120.0


def lufs_arr(p):
    return -0.691 + 10 * np.log10(np.maximum(p, 1e-20))


def window_loudness(k, windows):
    """Ungated mean K-weighted loudness over a set of time windows."""
    acc, n = 0.0, 0
    for a, b in windows:
        seg = k[int(a * SR):int(b * SR)]
        if len(seg):
            acc += (seg ** 2).sum(axis=1).sum()
            n += len(seg)
    return round(lufs(acc / n), 2) if n else -120.0


stems = {nm: load(f) for nm, f in zip(names, files)}
L = min(len(x) for x in stems.values())
K = {nm: kweight(x[:L]) for nm, x in stems.items()}
speech = [(ln["start_s"], ln["end_s"]) for c in tl["chunks"] for ln in c["lines"]]
key = [(ln["start_s"], ln["end_s"]) for c in tl["chunks"] for ln in c["lines"] if ln.get("key")]
pauses = [(c["lines"][i]["end_s"] + 0.2, c["lines"][i + 1]["start_s"] - 0.2) for c in tl["chunks"] for i, ln in enumerate(c["lines"][:-1]) if ln["pause_after"]]
pauses += [(a["speech_end_s"] + 0.2, b["speech_start_s"] - 0.2) for a, b in zip(tl["chunks"], tl["chunks"][1:])]
pauses = [(a, b) for a, b in pauses if b - a > 0.3]

out = {"label": label, "files": dict(zip(names, files)), "stems": {}}
for nm, k in K.items():
    out["stems"][nm] = {"integrated_lufs": integrated(k), "sample_peak_dbfs": round(20 * np.log10(np.abs(stems[nm][:L]).max() + 1e-12), 2)}
if "voice" in K and "music" in K:
    v_sp, m_sp = window_loudness(K["voice"], speech), window_loudness(K["music"], speech)
    out["under_speech"] = {"voice_lufs": v_sp, "music_lufs": m_sp, "voice_to_music_lu": round(v_sp - m_sp, 2),
                           "music_under_key_lines_lufs": window_loudness(K["music"], key)}
    # Small speakers (laptop / phone): a 180 Hz – 12 kHz band-pass before K-weighting.
    from scipy.signal import butter, sosfilt
    band = butter(4, [180, 12000], "band", fs=SR, output="sos")
    vs_, ms_ = kweight(sosfilt(band, stems["voice"][:L], axis=0)), kweight(sosfilt(band, stems["music"][:L], axis=0))
    out["small_speaker"] = {"voice_to_music_lu": round(window_loudness(vs_, speech) - window_loudness(ms_, speech), 2)}
    out["music_in_pauses_lufs"] = window_loudness(K["music"], pauses)
    out["music_rise_in_pauses_lu"] = round(out["music_in_pauses_lufs"] - m_sp, 2)
    # Music presence per film act (ungated loudness of the music stem alone).
    acts = [(0, 13.98), (13.98, 28.5), (28.5, 52.93), (52.93, 83.3), (83.3, 104.7), (104.7, 118.2), (118.2, L / SR)]
    out["music_by_act_lufs"] = [{"from_s": a, "to_s": round(b, 2), "lufs": window_loudness(K["music"], [(a, b)])} for a, b in acts]
if "sfx" in K and "voice" in K:
    out["sfx_vs_voice_peak_db"] = round(out["stems"]["sfx"]["sample_peak_dbfs"] - out["stems"]["voice"]["sample_peak_dbfs"], 2)
print(json.dumps(out, indent=1))
if "--out" in opts:
    with open(opts["--out"], "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
