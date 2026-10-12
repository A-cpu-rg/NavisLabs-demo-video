#!/usr/bin/env python3
"""Captions for the V6 film, timed to the founder's actual voiceover.

Writes:
  captions/navislabs-v7.srt                   sidecar captions (one cue per spoken line; long lines split at a comma or dash)
  captions/navislabs-v7.vtt                   the same, WebVTT, placed low in frame (line:88%) so they stay off the UI
  public/captions/navislabs-v7-captions.json  word-level @remotion/captions Caption[] (text, startMs, endMs, timestampMs, confidence)

Source: navislabs_v7_voice_timeline.json — every line's measured start/end and per-word times
(speech bursts matched to the words, syllables spread inside each burst). The words are the
founder-approved script (src/data/navislabs_v7_copy.json). Captions are sidecar files — nothing
is burned into the picture.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
TL = fa.load("navislabs_v7_voice_timeline.json")
MAX_CHARS = 46


def cues_for(line):
    words = line["words"]
    text = line["text"]
    if len(text) <= MAX_CHARS or len(words) < 4:
        return [(words, text)]
    # Split once, at the comma/dash nearest the middle.
    raw = text.split()
    best, mid = None, len(text) / 2
    pos = 0
    for k, w in enumerate(raw[:-1]):
        pos += len(w) + 1
        if w == "—" or re.search(r"[,;:]$", w):
            if best is None or abs(pos - mid) < abs(best[1] - mid):
                best = (k, pos)
    if best is None:
        return [(words, text)]
    left_text = " ".join(raw[: best[0] + 1]).strip()
    right_text = " ".join(raw[best[0] + 1:]).strip()
    n_left = len([w for w in raw[: best[0] + 1] if w != "—"])
    return [(words[:n_left], left_text), (words[n_left:], right_text)]


def ts(sec, sep):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


cues, words_out = [], []
for ch in TL["chunks"]:
    for line in ch["lines"]:
        for ws, text in cues_for(line):
            start = ws[0]["start_s"]
            end = max(ws[-1]["end_s"], start + 0.6)  # a short line still reads
            cues.append({"chunk": ch["id"], "start_s": start, "end_s": end, "text": text})
        for i, w in enumerate(line["words"]):
            words_out.append({"text": (" " if i else "") + w["text"], "startMs": round(w["start_s"] * 1000), "endMs": round(w["end_s"] * 1000), "timestampMs": round(w["start_s"] * 1000), "confidence": None})
# A cue never runs into the next one.
for a, b in zip(cues, cues[1:]):
    a["end_s"] = min(a["end_s"], b["start_s"] - 0.04)

os.makedirs(os.path.join(ROOT, "captions"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "public", "captions"), exist_ok=True)
with open(os.path.join(ROOT, "captions", "navislabs-v7.srt"), "w") as f:
    for i, c in enumerate(cues, 1):
        f.write(f"{i}\n{ts(c['start_s'], ',')} --> {ts(c['end_s'], ',')}\n{c['text']}\n\n")
with open(os.path.join(ROOT, "captions", "navislabs-v7.vtt"), "w") as f:
    f.write("WEBVTT\n\n")
    for i, c in enumerate(cues, 1):
        f.write(f"{c['chunk']}-{i}\n{ts(c['start_s'], '.')} --> {ts(c['end_s'], '.')} line:88% position:50% align:center\n{c['text']}\n\n")
with open(os.path.join(ROOT, "public", "captions", "navislabs-v7-captions.json"), "w") as f:
    json.dump(words_out, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"cues {len(cues)} · words {len(words_out)}")
