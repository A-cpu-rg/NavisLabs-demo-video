#!/usr/bin/env python3
"""Masters the SOCIAL V1 render's sound (the picture is copied, never re-encoded).

  python3 scripts/master-social.py <raw.mp4> <out.mp4>

One static gain to −14 LUFS integrated and a 4×-oversampled peak limiter at −1.3 dBFS (true peak
≤ −1 dBTP) — the same static approach as the film master, so the founder's pauses and the music's
dynamics are not reshaped. AAC-LC 320 kb/s, 48 kHz stereo, +faststart for social upload.
"""
import json
import subprocess
import sys

FF = "/opt/homebrew/bin/ffmpeg"
raw, out = sys.argv[1:3]


def measure(af=None):
    a = (af + "," if af else "") + "loudnorm=print_format=json"
    e = subprocess.run([FF, "-hide_banner", "-v", "info", "-i", raw, "-af", a, "-f", "null", "-"], capture_output=True, text=True).stderr
    return json.loads(e[e.rfind("{"):e.rfind("}") + 1])


def chain(g):
    return f"volume={g:.2f}dB,aresample=192000,alimiter=limit={10 ** (-1.3 / 20):.4f}:attack=1:release=60:level=disabled,aresample=48000"


m = measure()
g = -14.0 - float(m["input_i"])
r = measure(chain(g))
g += -14.0 - float(r["input_i"])
r = measure(chain(g))
print(f"measured {m['input_i']} LUFS → gain {g:+.2f} dB → {r['input_i']} LUFS, {r['input_tp']} dBTP")
p = subprocess.run([FF, "-hide_banner", "-y", "-v", "error", "-i", raw, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy", "-af", chain(g),
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", out], capture_output=True, text=True)
if p.returncode:
    sys.exit(p.stderr[-2000:])
print("wrote", out)
