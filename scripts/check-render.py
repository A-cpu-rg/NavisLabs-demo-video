#!/usr/bin/env python3
"""Render QC for the V6 review cut (the V5 version is in archive/v5/scripts/check-render.py).

  python3 scripts/check-render.py <video.mp4> [summary.json]

Measures: streams, duration, frame count, near-black runs, luma jumps, per-channel peak,
clipped samples, integrated loudness / true peak / LRA (ffmpeg loudnorm analysis), the
voice level of every spoken line (from navislabs_v8_voice_timeline.json — the measured
performance), and the bed level in the founder's marked pauses vs under speech (ducking).
"""
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF, FP = "/opt/homebrew/bin/ffmpeg", "/opt/homebrew/bin/ffprobe"
vid = sys.argv[1]
spec = json.load(open(os.path.join(ROOT, "navislabs_v8_film_spec.json")))
tl = json.load(open(os.path.join(ROOT, "navislabs_v8_voice_timeline.json")))
amap = json.load(open(os.path.join(ROOT, "navislabs_v8_audio_map.json")))
FPS = spec["format"]["fps"]

pr = json.loads(subprocess.run([FP, "-v", "error", "-show_streams", "-show_format", "-of", "json", vid], capture_output=True, text=True).stdout)
for st in pr["streams"]:
    print(st["codec_type"], st.get("codec_name"), st.get("width"), st.get("height"), st.get("r_frame_rate"), st.get("nb_frames"), st.get("duration"), st.get("sample_rate"), st.get("channels"))
print("format duration", pr["format"]["duration"], "size", round(int(pr["format"]["size"]) / 1e6, 1), "MB")

# Picture: mean luma per frame.
out = subprocess.run([FF, "-v", "error", "-i", vid, "-vf", "scale=480:270,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-", "-f", "null", "-"], capture_output=True, text=True).stdout
y = np.array([float(l.split("=")[1]) for l in out.splitlines() if "YAVG" in l])
print("frames analysed", len(y), "expected", spec["format"]["frames"])
runs = []
for i in np.where(y < 17)[0]:
    if runs and i == runs[-1][1] + 1:
        runs[-1][1] = i
    else:
        runs.append([int(i), int(i)])
print("near-black runs (s):", [(round(a / FPS, 2), round(b / FPS, 2)) for a, b in runs])
d = np.abs(np.diff(y))
big = [(int(i + 1), round((i + 1) / FPS, 2), round(float(y[i]), 1), round(float(y[i + 1]), 1)) for i in np.where(d > 18)[0]]
print("luma jumps > 18:", big)
# Motion: mean absolute difference between consecutive frames (grey, 320×180). Peaks are cuts,
# dissolves or fast camera moves; a fast move that is not a cut shows up as a run of high values.
out = subprocess.run([FF, "-v", "error", "-i", vid, "-vf", "scale=320:180,format=gray,tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-", "-f", "null", "-"], capture_output=True, text=True).stdout
md = np.array([float(l.split("=")[1]) for l in out.splitlines() if "YAVG" in l])
runs_m, cur = [], []
for i, x in enumerate(md):
    if x > 15:
        cur.append(i)
    elif cur:
        runs_m.append(cur)
        cur = []
if cur:
    runs_m.append(cur)
sustained = [[round(r_[0] / FPS, 2), round(r_[-1] / FPS, 2), round(float(md[r_].max()), 1)] for r_ in runs_m if len(r_) >= 3]
print("sustained fast motion (≥ 3 consecutive frames over 15):", sustained)

# Sound.
st = np.frombuffer(subprocess.run([FF, "-v", "error", "-i", vid, "-ac", "2", "-ar", "48000", "-f", "f32le", "-"], capture_output=True).stdout, dtype=np.float32)
peak = float(np.abs(st).max())
clipped = int((np.abs(st) >= 0.999).sum())
a = st.reshape(-1, 2).mean(axis=1)
print("audio seconds", round(len(a) / 48000, 3), "peak (per channel)", round(peak, 3), "clipped samples", clipped)


def rms(t0, t1):
    seg = a[int(t0 * 48000):int(t1 * 48000)]
    return float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)) if len(seg) else -120.0


vo_rms = {}
for c in tl["chunks"]:
    for i, ln in enumerate(c["lines"]):
        k = f"{c['id']}.{i + 1}"
        vo_rms[k] = round(rms(ln["start_s"], ln["end_s"]), 1)
        print(k, ln["start_s"], ln["end_s"], "rms", vo_rms[k], "dB", "|", ln["text"][:50])
pauses = [(c["id"], i + 1, ln["end_s"], c["lines"][i + 1]["start_s"]) for c in tl["chunks"] for i, ln in enumerate(c["lines"][:-1]) if ln["pause_after"]]
bed_in_pauses = {f"{cid}.{n}": round(rms(s + 0.25, e - 0.25), 1) for cid, n, s, e in pauses if e - s > 0.6}
print("bed level inside the marked pauses:", bed_in_pauses)
tail = amap["music"]["dips"][-1]
tail_rms = round(rms(tail["from_s"] + 0.6, tail["to_s"] - 0.05), 1)
print("silent end", tail["from_s"], "→", tail["to_s"], "rms", tail_rms)
ln_ = subprocess.run([FF, "-v", "info", "-i", vid, "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
lj = json.loads(ln_[ln_.rfind("{"):ln_.rfind("}") + 1])
print("integrated LUFS", lj["input_i"], "true peak", lj["input_tp"], "LRA", lj["input_lra"])

if len(sys.argv) > 2:
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    au = next((s for s in pr["streams"] if s["codec_type"] == "audio"), {})
    speech = [x for x in vo_rms.values()]
    summary = {
        "file": os.path.relpath(vid, ROOT), "size_mb": round(int(pr["format"]["size"]) / 1e6, 1), "duration_s": float(pr["format"]["duration"]),
        "expected_duration_s": spec["format"]["duration_s"], "expected_frames": spec["format"]["frames"],
        "video": {"codec": v.get("codec_name"), "width": v.get("width"), "height": v.get("height"), "fps": v.get("r_frame_rate"), "frames": len(y), "pix_fmt": v.get("pix_fmt"), "color_space": v.get("color_space")},
        "audio_stream": {"codec": au.get("codec_name"), "sample_rate": au.get("sample_rate"), "channels": au.get("channels"), "bit_rate": au.get("bit_rate")},
        "near_black_runs_s": [[round(a_ / FPS, 2), round(b_ / FPS, 2)] for a_, b_ in runs],
        "luma_jumps": [[f, t] for f, t, _, _ in big],
        "motion_peak": round(float(md.max()), 1), "sustained_fast_motion_s": sustained,
        "audio": {"seconds": round(len(a) / 48000, 3), "peak": round(peak, 3), "clipped_samples": clipped,
                  "integrated_lufs": float(lj["input_i"]), "true_peak_dbtp": float(lj["input_tp"]), "lra": float(lj["input_lra"])},
        "vo_rms_db": vo_rms, "vo_rms_range_db": [min(speech), max(speech)],
        "vo_silent_lines": [k for k, r_ in vo_rms.items() if r_ < -45],
        "bed_in_marked_pauses_db": bed_in_pauses, "silent_end_rms_db": tail_rms,
    }
    with open(sys.argv[2], "w") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    print("wrote", sys.argv[2])
