#!/usr/bin/env python3
"""Captions for the V5 script, timed to the locked picture.

Writes:
  captions/navislabs-v5.srt                 sidecar captions (one cue per sentence / clause)
  captions/navislabs-v5.vtt                 the same, WebVTT
  public/captions/navislabs-v5-captions.json  word-level @remotion/captions Caption[] (text, startMs, endMs, timestampMs, confidence)

Source: navislabs_v5_voiceover_screen_map.json (the copy from src/data/navislabs_v5_copy.json).
Each line starts at its locked start; every caption beat (the phrases that must land on a
picture beat) is pinned to its beat; the words in between are spaced by syllables; the line
ends at its planned end. Captions are sidecar files — nothing is burned into the picture.
When the founder's final takes arrive, re-time from the measured audio (word alignment) and
keep the beats inside their tolerances.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
VO = fa.load("navislabs_v5_voiceover_screen_map.json")["voiceover"]
PAUSE = {",": 0.12, ":": 0.15, "—": 0.2, ".": 0.3, "?": 0.3}


def tokens(text):
    # "—" stays attached to the word before it so cues and words stay readable.
    return re.sub(r"\s+—", " —", text).replace(" —", " —").split()


def word_times(line):
    toks = tokens(line["voice_line"])
    clean = [t.replace(" ", " ") for t in toks]
    n = len(toks)
    anchors = {0: line["start_s"]}
    for beat in line["caption_beats"]:
        ph = beat["phrase"].split()
        for i in range(n - len(ph) + 1):
            if [re.sub(r"[^\w'’-]", "", w).lower() for w in clean[i:i + len(ph)]] == [re.sub(r"[^\w'’-]", "", w).lower() for w in ph]:
                anchors[i] = max(anchors.get(i, 0), beat["lands_at_s"]) if i else anchors[0]
                break
        else:
            raise SystemExit(f"{line['id']}: caption beat '{beat['phrase']}' not found")
    end = max(line["end_s"], max(anchors.values()) + 0.4)
    keys = sorted(anchors)
    weights = [fa.syllables(w) * 0.2 + PAUSE.get(w.strip()[-1:], 0) for w in clean]
    starts = [0.0] * n
    for k, a in enumerate(keys):
        b = keys[k + 1] if k + 1 < len(keys) else n
        t0, t1 = anchors[a], (anchors[b] if b < n else end)
        span = sum(weights[a:b]) or 1
        t = t0
        for i in range(a, b):
            starts[i] = t
            t += (t1 - t0) * weights[i] / span
    ends = [starts[i + 1] if i + 1 < n else end for i in range(n)]
    return [{"text": (" " if i else "") + clean[i], "startMs": round(starts[i] * 1000), "endMs": round(ends[i] * 1000), "timestampMs": round(starts[i] * 1000), "confidence": None} for i in range(n)]


def cues(line, words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[.?:—]$", w["text"].strip()):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [{"start": c[0]["startMs"], "end": c[-1]["endMs"], "text": "".join(w["text"] for w in c).strip(), "line": line["id"]} for c in out]


def ts(ms, sep):
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


all_words, all_cues = [], []
for line in VO:
    w = word_times(line)
    assert "".join(x["text"] for x in w).strip() == line["voice_line"], line["id"]
    for beat in line["caption_beats"]:
        first = beat["phrase"].split()[0]
        hit = next(x for x in w if re.sub(r"[^\w'’-]", "", x["text"]).lower() == re.sub(r"[^\w'’-]", "", first).lower() and x["startMs"] >= beat["lands_at_s"] * 1000 - beat["tolerance_s"] * 1000 - 1)
        assert abs(hit["startMs"] / 1000 - beat["lands_at_s"]) <= beat["tolerance_s"] + 1e-6, (line["id"], beat["phrase"], hit)
    all_words += w
    all_cues += cues(line, w)

os.makedirs(os.path.join(ROOT, "captions"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "public", "captions"), exist_ok=True)
with open(os.path.join(ROOT, "captions", "navislabs-v5.srt"), "w") as f:
    for i, c in enumerate(all_cues, 1):
        f.write(f"{i}\n{ts(c['start'], ',')} --> {ts(c['end'], ',')}\n{c['text']}\n\n")
with open(os.path.join(ROOT, "captions", "navislabs-v5.vtt"), "w") as f:
    f.write("WEBVTT\n\n")
    for i, c in enumerate(all_cues, 1):
        f.write(f"{c['line']}-{i}\n{ts(c['start'], '.')} --> {ts(c['end'], '.')}\n{c['text']}\n\n")
with open(os.path.join(ROOT, "public", "captions", "navislabs-v5-captions.json"), "w") as f:
    json.dump(all_words, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"cues {len(all_cues)} · words {len(all_words)} · beats pinned {sum(len(l['caption_beats']) for l in VO)}")
