#!/usr/bin/env python3
"""What text does SOCIAL V1 actually show? — a claims scan over every retained V7 frame.

  python3 scripts/scan-social-claims.py <ocr-binary> <out.json> [step_s]

<ocr-binary> is a build of scripts/ocr-vision.swift (macOS Vision text recognition):
  swiftc -O scripts/ocr-vision.swift -o <scratch>/ocr

For each shot of src/social/navislabs_social_v1_plan.json, V7 frames are sampled every `step_s`
(holds once), read with OCR in V7 pixels, and every text box is mapped through the shot's
framing (cx, cy, s at that V7 time; split panels; clip_bottom / clip_right / side_fade /
top_cut masks) to decide whether a viewer of the 4:5 cut can see it. Visible text is checked
for integrations that are not live yet (navislabs_v8_launch_state.json), V7's CRM detail and the
dates V8 corrected. Read-only: V7 is never modified.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = "/opt/homebrew/bin/ffmpeg"
V7 = os.path.join(ROOT, "out", "navislabs-v7-review-1080p.mp4")
ocr_bin, out = sys.argv[1], sys.argv[2]
STEP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
plan = json.load(open(os.path.join(ROOT, "src", "social", "navislabs_social_v1_plan.json")))
state = json.load(open(os.path.join(ROOT, "src", "data", "navislabs_v8_launch_state.json")))
upcoming = [x["label"] for x in state["integrations"]["FILM_LAUNCH_INTEGRATIONS"] if x["status"] != "live"]
PATTERNS = {f"upcoming integration: {u}": re.escape(u.split()[0]) for u in upcoming}
PATTERNS.update({"Jira ticket id": r"\bKVR-\d+", "CRM detail": r"\bCRM\b|Opportunity", "date V8 corrected (renewal call Oct 8)": r"\bOct 9\b",
                 "date V8 corrected (6 days ago)": r"\b9 days ago\b"})


def key_at(keys, t):
    if not keys:
        return None
    if t <= keys[0]["src"]:
        return keys[0]
    for a, b in zip(keys, keys[1:]):
        if t <= b["src"]:
            p = (t - a["src"]) / max(b["src"] - a["src"], 1e-9)
            return {c: a[c] + (b[c] - a[c]) * p for c in ("cx", "cy", "s")}
    return keys[-1]


samples = []  # (shot, social_t, v7_t)
for sh in plan["shots"]:
    if sh["layout"] == "still":
        samples.append((sh, sh["at"], sh["src_in"]))
        continue
    n = max(1, int(sh["dur"] / STEP))
    for i in range(n + 1):
        lt = min(i * STEP, sh["dur"] - 0.02)
        samples.append((sh, sh["at"] + lt, sh["src_in"] + lt))

tmp = tempfile.mkdtemp(prefix="social-claims-")
paths = []
for i, (_, _, vt) in enumerate(samples):
    p = os.path.join(tmp, f"{i:04d}.png")
    subprocess.run([FF, "-v", "error", "-y", "-ss", f"{vt:.3f}", "-i", V7, "-frames:v", "1", p], check=True)
    paths.append(p)
boxes = {p: [] for p in paths}
def read(batch):
    res = subprocess.run([ocr_bin, *batch], capture_output=True, text=True).stdout
    for line in res.splitlines():
        f, bb, text = line.split("\t", 2)
        boxes[f].append(([int(v) for v in bb.split(",")], text))


for j in range(0, len(paths), 20):
    read(paths[j:j + 20])
# A frame with no text at all is re-read on its own (a failed batch must not look like a clean shot).
for p in [p for p in paths if not boxes[p]]:
    read([p])
empty = [i for i, p in enumerate(paths) if not boxes[p]]


def visible_regions(sh, vt):
    """[(map_fn, (x0, y0, x1, y1) visible output rect)] for this shot at V7 time vt."""
    regs = []
    if sh["layout"] == "split":
        for pnl in sh["panels"]:
            h = pnl["y1"] - pnl["y0"]
            regs.append((lambda x, y, p=pnl, h=h: (540 + (x - p["cx"]) * p["s"], p["y0"] + h / 2 + (y - p["cy"]) * p["s"]), (0, pnl["y0"], 1080, pnl["y1"])))
        return regs
    k = key_at(sh["keys"], 0 if sh["layout"] == "still" else vt)
    x1 = min(1080, sh.get("clip_right", 1080) - 12)
    x0 = sh.get("side_fade", 0) / 2
    x1 = min(x1, 1080 - sh.get("side_fade", 0) / 2)
    y1 = sh.get("clip_bottom", 1350) - 8
    y0 = 0
    if sh.get("top_fade"):
        y0 = sh["oy"] - (k["cy"] - sh.get("top_cut", 0)) * k["s"] + sh["top_fade"] / 2
    regs.append((lambda x, y, k=k, oy=sh["oy"]: (540 + (x - k["cx"]) * k["s"], oy + (y - k["cy"]) * k["s"]), (x0, y0, x1, y1)))
    return regs


hits, seen_text, heights = [], {}, {}
for (sh, st, vt), p in zip(samples, paths):
    for (bx0, by0, bx1, by1), text in boxes[p]:
        for fn, (rx0, ry0, rx1, ry1) in visible_regions(sh, vt):
            ax, ay = fn(bx0, by0)
            bx, by = fn(bx1, by1)
            ix = max(0.0, min(bx, rx1) - max(ax, rx0))
            iy = max(0.0, min(by, ry1) - max(ay, ry0))
            area = max((bx - ax) * (by - ay), 1e-6)
            if ix * iy / area < 0.3:
                continue
            seen_text.setdefault(sh["id"], set()).add(text)
            if len(text) >= 3:
                heights.setdefault(sh["id"], []).append(by - ay)
            for name, pat in PATTERNS.items():
                if re.search(pat, text, re.I):
                    # Text under ~10 output px tall (≈ 3.3 px on a phone) cannot be read by a viewer.
                    hits.append({"social_s": round(st, 2), "shot": sh["id"], "v7_s": round(vt, 2), "issue": name, "text": text,
                                 "output_box": [round(ax), round(ay), round(bx), round(by)], "text_px": round(by - ay, 1), "legible": by - ay >= 10})
res = {"about": "Visible-text claims scan of SOCIAL V1 (scripts/scan-social-claims.py).", "step_s": STEP, "samples": len(samples),
       "frames_without_text": [{"shot": samples[i][0]["id"], "v7_s": round(samples[i][2], 2)} for i in empty],
       "patterns": PATTERNS, "hits": hits,
       # On-screen UI text height (output px; a 4:5 feed post is ~390 pt wide on a phone → × 0.36 for points).
       "ui_text_px_by_shot": {k: {"boxes": len(v), "median": round(float(sorted(v)[len(v) // 2]), 1), "p90": round(float(sorted(v)[int(len(v) * 0.9)]), 1),
                                  "share_ge_30px": round(sum(x >= 30 for x in v) / len(v), 2)} for k, v in heights.items()}, "visible_text_by_shot": {k: sorted(v) for k, v in seen_text.items()}}
with open(out, "w") as f:
    json.dump(res, f, indent=1)
    f.write("\n")
print(f"{len(samples)} samples ({len(empty)} without any text) · {len(hits)} hits ({sum(h['legible'] for h in hits)} legible)")
for h in hits:
    if not h["legible"]:
        continue
    print(f"  {h['social_s']:6.2f}s {h['shot']:16s} V7 {h['v7_s']:7.2f}  {h['issue']:42s} {h['text']!r}")
