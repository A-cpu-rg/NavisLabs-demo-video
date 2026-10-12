#!/usr/bin/env python3
"""Prepares the founder-supplied Eleven Music track for the film (V8).

  python3 scripts/prepare-music-v8.py [source.mp3]

Source (default): ~/Downloads/ElevenLabs_NavisLabs_Platform_Introduction.mp3 — instrumental,
127.84 s, 44.1 kHz stereo MP3 (ID3 title "NavisLabs Platform Introduction").

1. The original is copied byte-for-byte to public/music/source/v8/ (provenance; never edited).
2. public/music/final/v8/score.wav: −1.5 dB of headroom (the source peaks at +0.4 dBTP), resampled to 48 kHz (high-quality swr: 64-tap, cutoff 0.97), placed at 0.000 s with no
   time-stretch and no pitch change, a gentle −2.5 dB presence carve at 3 kHz (Q 1.0) so the
   founder's consonants sit above the music (dialogue intelligibility), trimmed to the film's
   length with a 0.8 s fade into the film's silent end.
Ducking, lifts and dips are applied in the film by keyframed volume curves (AudioLayer.tsx).
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = "/opt/homebrew/bin/ffmpeg"
src = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Downloads/ElevenLabs_NavisLabs_Platform_Introduction.mp3")
spec = json.load(open(os.path.join(ROOT, "navislabs_v8_film_spec.json")))
END = spec["format"]["duration_s"]
if not os.path.isfile(src):
    sys.exit(f"music source not found: {src}")
os.makedirs(os.path.join(ROOT, "public", "music", "source", "v8"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "public", "music", "final", "v8"), exist_ok=True)
keep = os.path.join(ROOT, "public", "music", "source", "v8", os.path.basename(src))
shutil.copy2(src, keep)
out = os.path.join(ROOT, "public", "music", "final", "v8", "score.wav")
af = f"volume=-1.5dB,aresample=48000:filter_size=64:phase_shift=10:cutoff=0.97,equalizer=f=3000:t=q:w=1.0:g=-2.5,atrim=0:{END:.3f},afade=t=out:st={END - 0.8:.3f}:d=0.8"
subprocess.run([FF, "-v", "error", "-y", "-i", src, "-af", af, "-ac", "2", "-c:a", "pcm_s16le", out], check=True)
probe = json.loads(subprocess.run(["/opt/homebrew/bin/ffprobe", "-v", "error", "-show_format", "-of", "json", out], capture_output=True, text=True).stdout)
print(f"kept {os.path.relpath(keep, ROOT)} · wrote {os.path.relpath(out, ROOT)} ({float(probe['format']['duration']):.3f} s)")
