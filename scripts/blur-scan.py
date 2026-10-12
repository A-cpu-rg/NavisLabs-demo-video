#!/usr/bin/env python3
"""Finds smeared frames: per-frame sharpness (variance of the Laplacian on 480×270 grey) compared
with the median of its ±12-frame neighbourhood, and with the sharpest frames (85th percentile)
within ±1.5 s so that a sustained push is caught too. A frame far below either is motion-blurred
(or mid-dissolve / mid-fade). Usage: python3 scripts/blur-scan.py <video.mp4> [out.json]"""
import json
import subprocess
import sys

import numpy as np
from scipy.ndimage import laplace

FF = "/opt/homebrew/bin/ffmpeg"
W, H = 480, 270
p = subprocess.Popen([FF, "-v", "error", "-i", sys.argv[1], "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
sharp = []
while True:
    buf = p.stdout.read(W * H)
    if len(buf) < W * H:
        break
    f = np.frombuffer(buf, dtype=np.uint8).reshape(H, W).astype(np.float32)
    sharp.append(float(laplace(f).var()))
s = np.array(sharp)
flag = []
for i in range(len(s)):
    nb = np.concatenate([s[max(0, i - 12):i], s[i + 1:i + 13]])
    med = np.median(nb)
    wide = np.percentile(s[max(0, i - 45):i + 46], 85)  # sustained blur: compare with the sharpest frames within ±1.5 s
    if (med > 20 and s[i] < 0.45 * med) or (wide > 40 and s[i] < 0.35 * wide):
        flag.append(i)
runs = []
for i in flag:
    if runs and i <= runs[-1][1] + 1:
        runs[-1][1] = i
    else:
        runs.append([i, i])
res = [{"from_s": round(a / 30, 2), "to_s": round(b / 30, 2), "frames": b - a + 1, "min_ratio": round(float(min(s[a:b + 1]) / np.median(np.concatenate([s[max(0, a - 12):a], s[b + 1:b + 13]]))), 2)} for a, b in runs]
print(json.dumps(res))
if len(sys.argv) > 2:
    json.dump({"video": sys.argv[1], "frames": len(s), "soft_frames": res}, open(sys.argv[2], "w"), indent=1)
