#!/usr/bin/env python3
"""QC for NavisLabs SOCIAL V1 (4:5).

  python3 scripts/qc-social-v1.py <social.mp4> <stems_dir> <out.json>

Picture: format, frames, black runs, duplicate-frame runs (each classified: a planned hold,
V7's own static frames, or UNEXPECTED), sharpness drops (soft frames).
Audio: integrated LUFS / true peak (ebur128), clipped samples, silence gaps, loudness jumps
(intended or not), voice-to-music under speech and under key lines (from the social stems),
voice onsets vs the plan (sync).
"""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
from scipy.ndimage import laplace
from scipy.signal import lfilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF, FP = "/opt/homebrew/bin/ffmpeg", "/opt/homebrew/bin/ffprobe"
vid, stems, out = sys.argv[1:4]
plan = json.load(open(os.path.join(ROOT, "src", "social", "navislabs_social_v1_plan.json")))
FPS, END = plan["fps"], plan["duration_s"]
SR = 48000
res = {}

pr = json.loads(subprocess.run([FP, "-v", "error", "-show_streams", "-show_format", "-of", "json", vid], capture_output=True, text=True).stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video")
a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
res["format"] = {"width": v["width"], "height": v["height"], "fps": v["r_frame_rate"], "codec": v["codec_name"], "profile": v.get("profile"), "pix_fmt": v["pix_fmt"],
                 "frames": int(v.get("nb_frames", 0)), "video_s": float(v["duration"]), "audio_s": float(a["duration"]), "audio_codec": a["codec_name"],
                 "audio_rate": a["sample_rate"], "channels": a["channels"], "video_kbps": round(int(v.get("bit_rate", 0)) / 1000), "size_mb": round(int(pr["format"]["size"]) / 1e6, 1)}

# ---- picture: per-frame luma, hash, sharpness (270×338 grey)
Wd, Hd = 270, 338
p = subprocess.Popen([FF, "-v", "error", "-i", vid, "-vf", f"scale={Wd}:{Hd},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
luma, hashes, sharp, p995 = [], [], [], []
while True:
    buf = p.stdout.read(Wd * Hd)
    if len(buf) < Wd * Hd:
        break
    f = np.frombuffer(buf, dtype=np.uint8).reshape(Hd, Wd)
    luma.append(float(f.mean()))
    p995.append(float(np.percentile(f, 99.5)))
    hashes.append(hashlib.md5(f.tobytes()).hexdigest())
    sharp.append(float(laplace(f.astype(np.float32)).var()))
luma, sharp, p995 = np.array(luma), np.array(sharp), np.array(p995)


def runs(mask):
    out_, cur = [], None
    for i, m in enumerate(mask):
        if m:
            cur = [i, i] if cur is None else [cur[0], i]
        elif cur:
            out_.append(cur)
            cur = None
    if cur:
        out_.append(cur)
    return out_


def shot_at(fr):
    t = fr / FPS
    return next((s for s in plan["shots"] if s["at"] <= t < s["at"] + s["dur"]), plan["shots"][-1])


# "Black" = dark AND empty (nothing brighter than a dim background); a dark end card with its mark is not black.
res["black_runs_s"] = [[round(a_ / FPS, 2), round(b_ / FPS, 2), round((b_ - a_ + 1) / FPS, 2), shot_at(a_)["id"]] for a_, b_ in runs((luma < 12) & (p995 < 30))]
# Held frames must decode exactly like the live frame before them (no brightness jump at the cut).
holds = []
for sh in plan["shots"]:
    if sh["layout"] == "still":
        n0 = round(sh["at"] * FPS)
        holds.append({"shot": sh["id"], "cut_s": sh["at"], "luma_before": round(luma[n0 - 1], 2), "luma_after": round(luma[n0], 2), "step": round(luma[n0] - luma[n0 - 1], 2)})
res["hold_cuts"] = holds
dup = runs([i > 0 and hashes[i] == hashes[i - 1] for i in range(len(hashes))])
classified = []
for a_, b_ in dup:
    n = b_ - a_ + 1
    sh = shot_at(a_)
    if sh["layout"] == "still":
        kind = f"planned hold ({sh['id']})"
    elif n >= 2:
        kind = f"V7's own static frames in '{sh['id']}' (the V7 picture does not change here)"
    else:
        kind = "single repeated frame"
    classified.append({"from_s": round((a_ - 1) / FPS, 3), "to_s": round(b_ / FPS, 3), "frames": n + 1, "kind": kind})
# A repeated frame exactly at a cut would be an editing error.
cut_frames = {round(s["at"] * FPS) for s in plan["shots"]}
res["duplicate_runs"] = classified
res["duplicates_at_cuts"] = [c for c in classified if round(c["from_s"] * FPS) + 1 in cut_frames or round(c["to_s"] * FPS) in cut_frames and c["frames"] <= 2]
soft = []
for i in range(len(sharp)):
    nb = np.concatenate([sharp[max(0, i - 12):i], sharp[i + 1:i + 13]])
    wide = np.percentile(sharp[max(0, i - 45):i + 46], 85)
    if (np.median(nb) > 20 and sharp[i] < 0.45 * np.median(nb)) or (wide > 40 and sharp[i] < 0.35 * wide):
        soft.append(i)
res["soft_frame_runs_s"] = [[round(a_ / FPS, 2), round(b_ / FPS, 2), shot_at(a_)["id"]] for a_, b_ in runs([i in set(soft) for i in range(len(sharp))])]

# ---- audio
def load(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


B1, A1 = [1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585]
B2, A2 = [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]
kw = lambda x: lfilter(B2, A2, lfilter(B1, A1, x, axis=0), axis=0)  # noqa: E731
lp = lambda p_: -0.691 + 10 * np.log10(max(p_, 1e-20))  # noqa: E731


def wl(k, wins):
    acc = n = 0
    for a_, b_ in wins:
        seg = k[int(a_ * SR):int(b_ * SR)]
        acc += (seg ** 2).sum()
        n += len(seg)
    return round(lp(acc / n), 2) if n else -120.0


mx = load(vid)
e = subprocess.run([FF, "-hide_banner", "-nostats", "-i", vid, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
summ = e[e.rfind("Summary:"):]
res["loudness"] = {"integrated_lufs": float(summ.split("I:")[1].split("LUFS")[0]), "true_peak_dbtp": float(summ.split("Peak:")[1].split("dBFS")[0]),
                   "lra_lu": float(summ.split("LRA:")[1].split("LU")[0]), "clipped_samples": int((np.abs(mx) >= 0.999).sum()), "sample_peak": round(float(np.abs(mx).max()), 3)}
hop = int(0.05 * SR)
n = len(mx) // hop
rms = 20 * np.log10(np.sqrt((mx[:n * hop].mean(axis=1).reshape(n, hop) ** 2).mean(axis=1)) + 1e-12)
first = plan["voice"][0]["speech_start"]
gaps = []
for a_, b_ in runs(rms < -60):
    ta, tb = a_ * 0.05, (b_ + 1) * 0.05
    if tb - ta >= 0.3:
        why = "pre-roll before the first word" if ta < first else ("the silent end" if tb >= END - 0.7 else "UNEXPECTED")
        gaps.append({"from_s": round(ta, 2), "to_s": round(tb, 2), "why": why})
res["silence_gaps"] = gaps
st = {k_: load(os.path.join(stems, f"social-{k_}.wav")) for k_ in ("voice", "music", "sfx")}
K = {k_: kw(x) for k_, x in st.items()}
speech = [(x["speech_start"], x["speech_end"]) for x in plan["voice"]]
keyw = [(x["speech_start"], x["speech_end"]) for x in plan["voice"] if x["key"]] + [tuple(w) for x in plan["voice"] for w in x["key_windows"]]
pauses = [(b_ + 0.2, c_ - 0.2) for (_, b_), (c_, _) in zip(speech, speech[1:]) if c_ - b_ > 0.7]
v_sp = wl(K["voice"], speech)
res["separation"] = {"voice_lufs_under_speech": v_sp, "music_lufs_under_speech": wl(K["music"], speech), "voice_minus_music_lu": round(v_sp - wl(K["music"], speech), 2),
                     "voice_minus_music_key_lines_lu": round(v_sp - wl(K["music"], keyw), 2), "music_rise_in_pauses_lu": round(wl(K["music"], pauses) - wl(K["music"], speech), 2),
                     "voice_peak_minus_sfx_peak_db": round(20 * np.log10(np.abs(st["voice"]).max() / (np.abs(st["sfx"]).max() + 1e-12)), 2)}
# Loudness jumps (400 ms, 100 ms hop) — classify by the voice / music / SFX stems.
km = kw(mx)
win, h = int(0.4 * SR), int(0.1 * SR)
ms = (km ** 2).sum(axis=1)
c = np.concatenate([[0], np.cumsum(ms)])
idx = np.arange(0, len(ms) - win, h)
Lm = -0.691 + 10 * np.log10(np.maximum((c[idx + win] - c[idx]) / win, 1e-20))


def blk(k, t):
    seg = k[int(t * SR):int((t + 0.4) * SR)]
    return lp((seg ** 2).sum(axis=1).mean()) if len(seg) else -120.0


jumps = []
cuts = [s["at"] for s in plan["shots"]]
for i in range(1, len(Lm)):
    d = Lm[i] - Lm[i - 1]
    if abs(d) > 9 and max(Lm[i], Lm[i - 1]) > -45:
        t0, t1 = idx[i - 1] / SR, idx[i] / SR
        dv, dm, ds = (blk(K[k_], t1) - blk(K[k_], t0) for k_ in ("voice", "music", "sfx"))
        if t1 >= END - 2.0 and dm <= -6 and abs(dv) < 4:
            why = "the score's final decay into the silent end"
        elif abs(dv) >= 8 and abs(dm) < 4:
            why = "the founder's voice starts/stops (music steady)"
        elif abs(ds) >= 8 and abs(dv) < 4:
            why = "an SFX on a visible action"
        elif any(abs(t1 - x) < 0.6 for x in cuts) and abs(dm) >= 6:
            why = "a music edit on a picture cut"
        else:
            why = "UNEXPECTED"
        jumps.append({"t_s": round(t1 + 0.2, 2), "step_lu": round(float(d), 1), "why": why})
res["loudness_jumps"] = {"count": len(jumps), "unexpected": [j for j in jumps if j["why"] == "UNEXPECTED"], "all": jumps}
vo = st["voice"].mean(axis=1)
env = 20 * np.log10(np.sqrt(np.convolve(vo ** 2, np.ones(240) / 240, "same")) + 1e-12)
ons = []
for x in plan["voice"]:
    a_ = int((x["speech_start"] - 0.3) * SR)
    seg = env[a_:a_ + int(0.6 * SR)]
    got = (a_ + int(np.argmax(seg > -40))) / SR if (seg > -40).any() else None
    ons.append({"line": x["id"], "plan_s": x["speech_start"], "measured_s": round(got, 3) if got else None, "diff_ms": round((got - x["speech_start"]) * 1000, 1) if got else None})
res["voice_sync"] = {"onsets": ons, "max_abs_diff_ms": max(abs(o["diff_ms"]) for o in ons if o["diff_ms"] is not None), "audio_minus_video_ms": round((res["format"]["audio_s"] - res["format"]["video_s"]) * 1000, 1)}
with open(out, "w") as f:
    json.dump(res, f, indent=1)
    f.write("\n")
print(json.dumps({k_: res[k_] for k_ in ("format", "black_runs_s", "loudness", "silence_gaps", "separation")}, indent=1))
print("hold cuts:", [(h["shot"], h["step"]) for h in holds], "| duplicate runs:", len(classified), "| at cuts:", res["duplicates_at_cuts"], "| soft runs:", len(res["soft_frame_runs_s"]), "| unexpected jumps:", res["loudness_jumps"]["unexpected"], "| sync max ms:", res["voice_sync"]["max_abs_diff_ms"])
