#!/usr/bin/env python3
"""Masters the V6 review render's sound and derives the 540p review from it.

  python3 scripts/master-v6.py <raw-1080p.mp4> <out-1080p.mp4> <out-540p.mp4>

1) One static gain to −14 LUFS integrated, then a 4×-oversampled peak limiter at −1.3 dBFS so
   the true peak stays ≤ −1 dBTP. Static, not loudnorm's dynamic mode: the founder's pauses,
   the deliberate silences and the mix balance are left exactly as designed. The gain is
   re-measured once (the limiter takes a little loudness). The picture is copied, never
   re-encoded. Audio: AAC-LC 320 kb/s, 48 kHz stereo.
2) 540p: the mastered 1080p scaled (lanczos) to 960×540, H.264 CRF 20, the same mastered audio.
Nothing here changes timing: the voice is the master clock.
"""
import json
import subprocess
import sys

FF = "/opt/homebrew/bin/ffmpeg"
raw, out1080, out540 = sys.argv[1:4]


def measure(path, af=None):
    cmd = [FF, "-hide_banner", "-v", "info", "-i", path] + (["-af", af + ",loudnorm=print_format=json"] if af else ["-af", "loudnorm=print_format=json"]) + ["-f", "null", "-"]
    e = subprocess.run(cmd, capture_output=True, text=True).stderr
    return json.loads(e[e.rfind("{"):e.rfind("}") + 1])


def chain(gain_db):
    return f"volume={gain_db:.2f}dB,aresample=192000,alimiter=limit={10 ** (-1.3 / 20):.4f}:attack=1:release=60:level=disabled,aresample=48000"


m = measure(raw)
print("measured", {k: m[k] for k in ("input_i", "input_tp", "input_lra")})
gain = -14.0 - float(m["input_i"])
r = measure(raw, chain(gain))
gain += -14.0 - float(r["input_i"])  # one correction for what the limiter took
r = measure(raw, chain(gain))
print(f"gain {gain:+.2f} dB → {r['input_i']} LUFS, {r['input_tp']} dBTP, LRA {r['input_lra']}")
p = subprocess.run([FF, "-hide_banner", "-y", "-v", "error", "-i", raw, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy", "-af", chain(gain),
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", out1080], capture_output=True, text=True)
if p.returncode:
    sys.exit(p.stderr[-2000:])
p = subprocess.run([FF, "-hide_banner", "-y", "-v", "error", "-i", out1080, "-vf", "scale=960:540:flags=lanczos", "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "copy", "-movflags", "+faststart", out540],
                   capture_output=True, text=True)
if p.returncode:
    sys.exit(p.stderr[-2000:])
print("wrote", out1080, "and", out540)
