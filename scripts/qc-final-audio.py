#!/usr/bin/env python3
"""Final audio QC for the V8 review master and its stems.

  python3 scripts/qc-final-audio.py <master.mp4> <stems_dir> [out.json]

Measures (BS.1770 K-weighting for loudness):
  · voice / music / SFX / room stems: integrated loudness, peaks; voice-to-music under speech and
    under the key lines; small-speaker balance; music lift in the pauses
  · master: integrated LUFS, true peak (ffmpeg ebur128, 4× oversampled), clipped samples
  · silence gaps in the master (< −60 dBFS RMS for ≥ 0.3 s), each classified as intended or not
  · volume jumps: 400 ms loudness steps > 9 LU between consecutive 100 ms blocks, intended or not
  · A/V sync: audio vs video stream length, and each voice chunk's onset in the rendered voice
    stem vs the timeline (founder voice = master clock)
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import butter, lfilter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF, FP = "/opt/homebrew/bin/ffmpeg", "/opt/homebrew/bin/ffprobe"
SR = 48000
master, stems_dir = sys.argv[1], sys.argv[2]
out_path = sys.argv[3] if len(sys.argv) > 3 else None
tl = json.load(open(os.path.join(ROOT, "navislabs_v8_voice_timeline.json")))
amap = json.load(open(os.path.join(ROOT, "navislabs_v8_audio_map.json")))
spec = json.load(open(os.path.join(ROOT, "navislabs_v8_film_spec.json")))
END = spec["format"]["duration_s"]
B = spec["timing"]["beats"]


def load(p):
    raw = subprocess.run([FF, "-v", "error", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


B1, A1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
B2, A2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]


def kw(x):
    return lfilter(B2, A2, lfilter(B1, A1, x, axis=0), axis=0)


def lufs_p(p):
    return -0.691 + 10 * np.log10(max(p, 1e-20))


def integrated(k):
    n, h = int(0.4 * SR), int(0.1 * SR)
    ms = (k ** 2).sum(axis=1)
    c = np.concatenate([[0], np.cumsum(ms)])
    st = np.arange(0, max(1, len(ms) - n), h)
    p = (c[st + n] - c[st]) / n
    p = p[(-0.691 + 10 * np.log10(np.maximum(p, 1e-20))) > -70]
    if not len(p):
        return -120.0
    rel = lufs_p(p.mean()) - 10
    p = p[(-0.691 + 10 * np.log10(np.maximum(p, 1e-20))) > rel]
    return round(lufs_p(p.mean()), 2)


def wl(k, windows):
    acc = n = 0
    for a, b in windows:
        seg = k[int(a * SR):int(b * SR)]
        acc += (seg ** 2).sum()
        n += len(seg)
    return round(lufs_p(acc / n), 2) if n else -120.0


res = {"master": os.path.relpath(master, ROOT), "stems_dir": os.path.relpath(stems_dir, ROOT)}
st = {k: load(os.path.join(stems_dir, f"v8-{k}.wav")) for k in ("voice", "music", "sfx", "room")}
K = {k: kw(v) for k, v in st.items()}
speech = [(ln["start_s"], ln["end_s"]) for c in tl["chunks"] for ln in c["lines"]]
key = [(w["from_s"], w["to_s"]) for w in amap["speech"] if w["key"]]
gaps = [(a + 0.2, b - 0.2) for (_, a), (b, _) in zip(speech, speech[1:]) if b - a > 0.6]
res["stems"] = {k: {"integrated_lufs": integrated(K[k]), "sample_peak_dbfs": round(20 * np.log10(np.abs(st[k]).max() + 1e-12), 2)} for k in st}
v_sp, m_sp, m_key = wl(K["voice"], speech), wl(K["music"], speech), wl(K["music"], key)
band = butter(4, [180, 12000], "band", fs=SR, output="sos")
vs_, ms_ = kw(sosfilt(band, st["voice"], axis=0)), kw(sosfilt(band, st["music"], axis=0))
res["separation"] = {"voice_lufs_under_speech": v_sp, "music_lufs_under_speech": m_sp, "voice_minus_music_lu": round(v_sp - m_sp, 2),
                     "voice_minus_music_key_lines_lu": round(v_sp - m_key, 2), "voice_minus_music_small_speaker_lu": round(wl(vs_, speech) - wl(ms_, speech), 2),
                     "music_rise_in_pauses_lu": round(wl(K["music"], gaps) - m_sp, 2), "room_in_pauses_lufs": wl(K["room"], gaps),
                     "voice_minus_sfx_peak_db": round(res["stems"]["voice"]["sample_peak_dbfs"] - res["stems"]["sfx"]["sample_peak_dbfs"], 2)}

# Master
mx = load(master)
e = subprocess.run([FF, "-hide_banner", "-nostats", "-i", master, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
summ = e[e.rfind("Summary:"):]
I = float(summ.split("I:")[1].split("LUFS")[0])
TP = float(summ.split("Peak:")[1].split("dBFS")[0])
LRA = float(summ.split("LRA:")[1].split("LU")[0])
res["master_loudness"] = {"integrated_lufs": I, "true_peak_dbtp": TP, "lra_lu": LRA, "clipped_samples": int((np.abs(mx) >= 0.999).sum()), "sample_peak": round(float(np.abs(mx).max()), 3)}

# Silence gaps
hop = int(0.05 * SR)
n = len(mx) // hop
rms = 20 * np.log10(np.sqrt((mx[:n * hop].mean(axis=1).reshape(n, hop) ** 2).mean(axis=1)) + 1e-12)
sil, cur = [], None
for i, x in enumerate(rms):
    if x < -60:
        cur = [i, i] if cur is None else [cur[0], i]
    elif cur:
        sil.append(cur)
        cur = None
if cur:
    sil.append(cur)
INTENDED_SIL = [(0.0, tl["chunks"][0]["speech_start_s"] + 0.05, "pre-roll: the film opens on the founder's first word"), (END - 1.6, END + 0.1, "the silent end after the tagline")]
res["silence_gaps"] = []
for a, b in sil:
    ta, tb = a * 0.05, (b + 1) * 0.05
    if tb - ta < 0.3:
        continue
    why = next((w for lo, hi, w in INTENDED_SIL if ta >= lo - 0.2 and tb <= hi), None)
    res["silence_gaps"].append({"from_s": round(ta, 2), "to_s": round(tb, 2), "intended": why is not None, "why": why or "UNEXPECTED"})

# Volume jumps (400 ms loudness, 100 ms hop)
km = kw(mx)
win, h = int(0.4 * SR), int(0.1 * SR)
ms = (km ** 2).sum(axis=1)
c = np.concatenate([[0], np.cumsum(ms)])
idx = np.arange(0, len(ms) - win, h)
L = -0.691 + 10 * np.log10(np.maximum((c[idx + win] - c[idx]) / win, 1e-20))
INTENDED_JUMP = [(B["logoTile"] - 0.6, B["logoTile"] + 0.8, "the music opens on 'Navis'")]
INTENDED_JUMP += [(ln["start_s"] - 0.4, ln["start_s"] + 0.3, "a spoken line starts") for c_ in tl["chunks"] for ln in c_["lines"]]
INTENDED_JUMP += [(ln["end_s"] - 0.3, ln["end_s"] + 0.5, "a spoken line ends") for c_ in tl["chunks"] for ln in c_["lines"]]
INTENDED_JUMP += [(e_["at"] - 0.1, e_["at"] + 0.4, f"SFX: {e_['why']}") for e_ in json.load(open(os.path.join(ROOT, "navislabs_v8_sfx_map.json")))["categories"] for e_ in [dict(at=x["at_s"], why=x["why"]) for x in e_["events"]]]
INTENDED_JUMP += [(END - 1.5, END, "the silent end")]
Kv, Km = K["voice"], K["music"]


def blk(k, t):
    seg = k[int(t * SR):int((t + 0.4) * SR)]
    return lufs_p((seg ** 2).sum(axis=1).mean()) if len(seg) else -120.0


jumps = []
for i in range(1, len(L)):
    d = L[i] - L[i - 1]
    if abs(d) > 9 and max(L[i], L[i - 1]) > -45:
        t = idx[i] / SR + 0.2
        why = next((w for lo, hi, w in INTENDED_JUMP if lo <= t <= hi), None)
        if why is None:
            t0, t1 = idx[i - 1] / SR, idx[i] / SR
            dv, dm = blk(Kv, t1) - blk(Kv, t0), blk(Km, t1) - blk(Km, t0)
            if abs(dv) >= 8 and abs(dm) < 3:
                why = "the founder's own phrasing (a pause inside a line; the voice is locked, the music is steady)"
        jumps.append({"t_s": round(t, 2), "step_lu": round(float(d), 1), "intended": why is not None, "why": why or "UNEXPECTED"})
res["volume_jumps"] = {"count": len(jumps), "unexpected": [j for j in jumps if not j["intended"]], "intended_examples": [j for j in jumps if j["intended"]][:12]}

# A/V sync
pr = json.loads(subprocess.run([FP, "-v", "error", "-show_streams", "-of", "json", master], capture_output=True, text=True).stdout)
vdur = float(next(s_ for s_ in pr["streams"] if s_["codec_type"] == "video")["duration"])
adur = float(next(s_ for s_ in pr["streams"] if s_["codec_type"] == "audio")["duration"])
vo = st["voice"].mean(axis=1)
env = 20 * np.log10(np.sqrt(np.convolve(vo ** 2, np.ones(240) / 240, "same")) + 1e-12)
onsets = []
for ch in tl["chunks"]:
    exp = ch["speech_start_s"]
    a = int((exp - 0.3) * SR)
    seg = env[a:a + int(0.6 * SR)]
    hit = np.argmax(seg > -40) if (seg > -40).any() else None
    got = (a + hit) / SR if hit is not None else None
    onsets.append({"chunk": ch["id"], "timeline_speech_start_s": round(exp, 3), "measured_onset_s": round(got, 3) if got else None, "diff_ms": round((got - exp) * 1000, 1) if got else None})
res["av_sync"] = {"video_s": round(vdur, 3), "audio_s": round(adur, 3), "audio_minus_video_ms": round((adur - vdur) * 1000, 1), "voice_onsets": onsets,
                  "max_abs_onset_diff_ms": max(abs(o["diff_ms"]) for o in onsets if o["diff_ms"] is not None)}
print(json.dumps(res, indent=1))
if out_path:
    with open(out_path, "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
