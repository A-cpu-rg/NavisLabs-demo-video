#!/usr/bin/env python3
"""V8 room tone — the fourth audio layer (TEMP, synthesized in-project).

  public/sfx/temp/v8/room.wav   48 kHz stereo, the film's length

An extremely subtle digital room: band-limited air (150 Hz – 2.5 kHz pink-ish noise, slowly
breathing), a faint soft drone a fifth apart (D2 / A2) far below the music, and no hiss above
6 kHz or mains hum. It is never heard as noise: the film plays it only in the pauses and
visual-only moments through a keyframed curve (navislabs_v8_audio_map.json → room.curve),
at about −50 LUFS, so the film never drops to dead air. Off under speech and at the silent end.
A recorded/ElevenLabs room tone drops into public/sfx/final/v8/room.wav with no code change.
"""
import json
import os
import wave

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
END = json.load(open(os.path.join(ROOT, "navislabs_v8_film_spec.json")))["format"]["duration_s"]
N = int(round(END * SR))
rng = np.random.default_rng(88)
t = np.arange(N) / SR

white = rng.standard_normal((N, 2))
pink = np.cumsum(white, axis=0)  # brown-ish, then band-limited into a soft pink colour
pink = sosfilt(butter(2, [150, 2500], "band", fs=SR, output="sos"), pink - pink.mean(axis=0), axis=0)
pink /= np.abs(pink).max()
breath = 1 + 0.25 * np.sin(2 * np.pi * 0.045 * t + 0.7) + 0.1 * np.sin(2 * np.pi * 0.11 * t)
drone = 0.18 * np.sin(2 * np.pi * 73.42 * t) + 0.1 * np.sin(2 * np.pi * 110.0 * t + 0.4)
drone *= 1 + 0.2 * np.sin(2 * np.pi * 0.03 * t)
room = pink * 0.5 * breath[:, None] + np.stack([drone, drone * 0.96], axis=1)
room = sosfilt(butter(4, 6000, "low", fs=SR, output="sos"), room, axis=0)
fade = np.minimum(1, np.minimum(t / 1.0, (END - t) / 1.0))
room *= fade[:, None]
room = room / np.abs(room).max() * 0.5
out = os.path.join(ROOT, "public", "sfx", "temp", "v8", "room.wav")
os.makedirs(os.path.dirname(out), exist_ok=True)
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((room * 32767).astype("<i2").tobytes())
print(f"wrote {os.path.relpath(out, ROOT)} ({END:.2f} s)")
