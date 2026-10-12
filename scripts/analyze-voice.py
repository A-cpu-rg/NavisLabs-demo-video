#!/usr/bin/env python3
"""Measures the founder's final voiceover (P1–P8) and aligns the approved script to it.

Reads   public/voiceover/final/v6/P1.wav … P8.wav (48 kHz mono, converted from the
        founder's ElevenLabs takes; originals kept in public/voiceover/source/v6/)
Writes  navislabs_v6_voice_analysis.json — per chunk: duration, loudness, speech start/end,
        every pause, and each script line's start/end inside the chunk.

Alignment: speech segments come from an RMS envelope (10 ms hops); each script line is
assigned a contiguous run of segments by dynamic programming so that the measured line
lengths match the lines' syllable counts as closely as possible, and every [pause] in the
script falls on one of the chunk's long silences. No speech recognition is involved: the
words are the founder-approved script; the audio decides where they sit.
"""
import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
COPY = fa.load("src/data/navislabs_v8_copy.json")
HOP = 0.01


def read(p):
    with wave.open(p) as w:
        n, sr, sw = w.getnframes(), w.getframerate(), w.getsampwidth()
        raw = w.readframes(n)
    if sw == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        x = (b[:, 0].astype(np.int32) | (b[:, 1].astype(np.int32) << 8) | (b[:, 2].astype(np.int32) << 16))
        x = np.where(x >= 1 << 23, x - (1 << 24), x).astype(np.float64) / (1 << 23)
    else:
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768
    return x, sr


def loudness(p):
    err = subprocess.run(["/opt/homebrew/bin/ffmpeg", "-v", "info", "-i", p, "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(err[err.rfind("{"):err.rfind("}") + 1])
    return float(j["input_i"]), float(j["input_tp"])


def segments(x, sr, rel_db=-26.0, min_gap=0.03, min_seg=0.04):
    hop = int(HOP * sr)
    frames = len(x) // hop
    rms = np.sqrt(np.array([np.mean(x[i * hop:(i + 1) * hop] ** 2) for i in range(frames)]) + 1e-12)
    db = 20 * np.log10(rms)
    thr = np.percentile(db, 95) + rel_db
    on = db > thr
    segs, i = [], 0
    while i < frames:
        if on[i]:
            j = i
            while j < frames and on[j]:
                j += 1
            segs.append([i * HOP, j * HOP])
            i = j
        else:
            i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < min_gap:
            merged[-1][1] = s[1]
        else:
            merged.append(s)
    return [s for s in merged if s[1] - s[0] >= min_seg], db, thr


def align(lines, segs):
    """lines: [{text, pause_after}] → contiguous segment blocks (DP)."""
    n, m = len(lines), len(segs)
    syl = [max(1, fa.syllables(l["text"])) for l in lines]
    speech = sum(s[1] - s[0] for s in segs)
    rate = speech / sum(syl)
    INF = float("inf")
    cost = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    cost[0][0] = 0.0
    for i in range(1, n + 1):
        for j in range(i, m - (n - i) + 1):
            for k in range(i - 1, j):
                if cost[i - 1][k] == INF:
                    continue
                # Voiced time only: the gaps between MCP, API, SDK and CLI are not syllables.
                dur = sum(s[1] - s[0] for s in segs[k:j])
                c = math.log(max(dur, 0.05) / (syl[i - 1] * rate)) ** 2
                # A sentence-length silence (≥ 0.55 s) does not sit inside one line.
                c += sum(2.0 * max(0.0, segs[t + 1][0] - segs[t][1] - 0.55) for t in range(k, j - 1))
                if j < m:
                    gap = segs[j][0] - segs[j - 1][1]
                    if lines[i - 1]["pause_after"]:
                        c += 0 if gap >= 1.0 else 4.0
                    elif gap >= 1.2:
                        c += 4.0  # a long silence inside the script's flow must be a [pause]
                    c -= 0.15 * min(gap, 0.6)  # prefer cutting lines at real gaps
                total = cost[i - 1][k] + c
                if total < cost[i][j]:
                    cost[i][j], back[i][j] = total, k
    out, j = [], m
    for i in range(n, 0, -1):
        k = back[i][j]
        out.append({"start": round(segs[k][0], 3), "end": round(segs[j - 1][1], 3)})
        j = k
    return out[::-1]


chunks = []
for ch in COPY["chunks"]:
    p = os.path.join(ROOT, "public", ch["final"])
    x, sr = read(p)
    dur = len(x) / sr
    segs, db, thr = segments(x, sr)
    lufs, tp = loudness(p)
    lines = [{"text": l["text"], "pause_after": l.get("pause_after", False)} for l in ch["lines"]]
    al = align(lines, segs)
    pauses = [{"from": round(a[1], 3), "to": round(b[0], 3), "s": round(b[0] - a[1], 3)} for a, b in zip(segs, segs[1:]) if b[0] - a[1] >= 0.15]
    chunks.append({
        "id": ch["id"], "file": ch["final"], "duration_s": round(dur, 3), "integrated_lufs": lufs, "true_peak_dbtp": tp,
        "speech_start_s": round(segs[0][0], 3), "speech_end_s": round(segs[-1][1], 3),
        "segments": [[round(a, 3), round(b, 3)] for a, b in segs], "pauses": pauses,
        "lines": [{"text": l["text"], "start_s": a["start"], "end_s": a["end"], "pause_after": l["pause_after"]} for l, a in zip(lines, al)],
    })
    print(f"{ch['id']}: {dur:6.2f}s speech {segs[0][0]:.2f}–{segs[-1][1]:.2f} · {lufs} LUFS · {len(segs)} segments")
    for l, a in zip(lines, al):
        print(f"    {a['start']:6.2f}–{a['end']:6.2f}  {l['text']}{'   [pause]' if l['pause_after'] else ''}")

with open(os.path.join(ROOT, "navislabs_v6_voice_analysis.json"), "w") as f:
    json.dump({"about": "Measured founder voiceover P1–P8 (scripts/analyze-voice.py). Times are seconds inside each chunk.", "total_s": round(sum(c["duration_s"] for c in chunks), 3), "chunks": chunks}, f, indent=1)
    f.write("\n")
print("total", round(sum(c["duration_s"] for c in chunks), 2))
