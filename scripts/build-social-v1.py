#!/usr/bin/env python3
"""NavisLabs SOCIAL V1 — a 4:5 (1080×1350) social launch cut edited from the approved V7 film.

Writes:
  src/social/navislabs_social_v1_plan.json   everything the NavisSocial composition plays
  captions/social-captions.srt|.vtt          sidecar captions (also burned in by the composition)
  captions/social-captions.json              word-level captions (@remotion/captions format)

Sources (read only — nothing here modifies V7 or V8):
  picture  public/social/v7-proxy-2880.mp4  (1.5× lanczos proxy of out/navislabs-v7-review-1080p.mp4)
  voice    public/voiceover/final/v6/P1–P8.wav — the founder's recordings, cut at measured line
           boundaries (navislabs_v8_voice_timeline.json; same voice timing as V7), never stretched
  music    public/music/final/v8/score.wav — the founder-supplied Eleven Music track, re-edited
  SFX      public/sfx/temp/v7/*.wav — the in-project (temporary) library
Every shot that carries a word-synced visual (logo on "Navis", surfaces on MCP/API/SDK/CLI,
SOURCE/FRESHNESS cuts, Approve & send, the run, the thesis, the end logo) plays the V7 frames
1:1 against the same line, so picture and voice stay in sync by construction.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
W, H = 1080, 1350
tl = json.load(open(os.path.join(ROOT, "navislabs_v8_voice_timeline.json")))
CH = {c["id"]: c for c in tl["chunks"]}
SFXLIB = json.load(open(os.path.join(ROOT, "navislabs_v8_audio_map.json")))["sfx"]["library"]

# ------------------------------------------------------------------ voice map
# (id, chunk, first line, last line, silence before this line's first word, key line?)
LINES = [
    ("L01", "P1", 0, 0, 0.35, False),
    ("L02", "P1", 1, 1, 0.70, False),
    ("L03", "P1", 2, 2, 0.40, False),
    ("L04", "P1", 3, 3, 0.35, False),
    ("L05", "P2", 0, 0, 0.80, False),
    ("L06", "P3", 0, 0, 0.95, False),
    ("L07", "P3", 1, 2, 0.45, False),
    ("L08", "P3", 3, 3, 0.45, False),
    ("L09", "P3", 5, 5, 1.30, True),
    ("L10", "P3", 6, 6, 1.73, True),   # V7's own gap: the click and the held breath
    ("L11", "P4", 0, 0, 0.65, False),
    ("L12", "P4", 2, 2, 0.30, False),
    ("L13", "P4", 3, 4, 0.50, False),
    ("L14", "P4", 5, 5, 0.50, True),
    ("L15", "P4", 6, 6, 0.90, True),
    ("L16", "P4", 8, 9, 0.80, False),
    ("L17", "P6", 0, 4, 0.70, False),  # key words inside: "One understanding." "Two ways in."
    ("L18", "P8", 0, 0, 0.90, True),   # "NavisLabs."
    ("L19", "P8", 1, 1, 1.15, False),  # the tagline (the founder's 1.96 s pause shortened to 1.15 s — a clean cut)
]
END_HOLD = 1.5
PRE, POST = 0.12, 0.20

vo, t = [], 0.0
for lid, cid, a, b, gap, key in LINES:
    c = CH[cid]
    lines = c["lines"]
    s_abs, e_abs = lines[a]["start_s"], lines[b]["end_s"]
    prev_end = lines[a - 1]["end_s"] if a > 0 else c["at_s"]
    next_start = lines[b + 1]["start_s"] if b + 1 < len(lines) else c["at_s"] + c["duration_s"]
    src_in = max(0.0, s_abs - c["at_s"] - PRE, prev_end - c["at_s"] + 0.05)
    src_out = min(c["duration_s"], e_abs - c["at_s"] + POST, next_start - c["at_s"] - 0.05)
    start = t + gap if vo else gap
    at = start - (s_abs - c["at_s"] - src_in)
    words = [{"text": w["text"], "start": round(start + (w["start_s"] - s_abs), 3), "end": round(start + (w["end_s"] - s_abs), 3)}
             for ln in lines[a:b + 1] for w in ln["words"]]
    vo.append({"id": lid, "chunk": cid, "file": c["file"], "src_in": round(src_in, 3), "src_out": round(src_out, 3), "at": round(at, 3),
               "speech_start": round(start, 3), "speech_end": round(start + (e_abs - s_abs), 3), "v7_start": s_abs, "v7_end": e_abs,
               "text": " ".join(ln["text"] for ln in lines[a:b + 1]), "key": key, "words": words,
               "key_windows": ([[round(start + (lines[i]["start_s"] - s_abs), 3), round(start + (lines[i]["end_s"] - s_abs), 3)] for i in (3, 4)] if lid == "L17" else [])})
    t = start + (e_abs - s_abs)
END = round(t + END_HOLD, 3)
L = {v["id"]: v for v in vo}


def S(i):
    return L[i]["speech_start"]


def E(i):
    return L[i]["speech_end"]


def sync(lid, v7_t):
    """Social time at which V7 time v7_t plays when line lid is mapped 1:1 onto its V7 line."""
    return S(lid) + (v7_t - L[lid]["v7_start"])


# ------------------------------------------------------------------ shots
# keys: reframes on the V7 picture, by V7 source time. cx, cy = the V7 point (1920×1080 space)
# placed at output (540, oy); s = output px per V7 px (≥ 1.25 fills the 4:5 frame edge to edge).
DARK, LIGHT, APPBG = "#14130F", "#EEEBE5", "#F3F1ED"
shots = []


def shot(sid, start, end, src_in, keys, bg=DARK, oy=600, layout="frame", **kw):
    shots.append({"id": sid, "at": round(start, 3), "dur": round(end - start, 3), "src_in": round(src_in, 3), "keys": keys, "bg": bg, "oy": oy, "layout": layout, **kw})


def k(src, cx, cy, s):
    return {"src": round(src, 3), "cx": cx, "cy": cy, "s": s}


# 1 · HOOK — the two truths, stacked for 4:5: the person's email above, the agent's file below.
a = 0.0
b = S("L02") - 0.15
shot("hook", a, b, a - S("L01") + 0.60, [], layout="split",
     panels=[{"label": "PEOPLE", "label_y": 96, "y0": 140, "y1": 570, "cx": 495, "cy": 560, "s": 1.62},
             {"label": "AI AGENTS", "label_y": 628, "y0": 672, "y1": 1092, "cx": 1345, "cy": 560, "s": 1.62}])
# 2 · SCATTERED — the truth breaks into the systems where work happens (V7 S01, 1:1 with the line).
a, b = b, S("L02") + 1.70
shot("scatter", a, b, 7.30, [k(7.3, 960, 470, 0.86), k(9.2, 960, 470, 0.90)], oy=560, feather=True)
# 3 · the systems where work happens → signals (V7 S04 data flow).
a, b = b, S("L03") - 0.12
# Only V7's first column is framed: the six LIVE integrations (Gmail, Google Calendar, Google Meet, Google Drive,
# Google Docs, Slack — navislabs_v8_launch_state.json). Salesforce (below Slack) and the second column (Notion,
# Microsoft 365, HubSpot, Jira, GitHub, Zoom) are upcoming and stay out of frame (clip_bottom / clip_right).
shot("systems", a, b, 20.30, [k(20.3, 368, 410, 1.90), k(22.2, 368, 410, 1.94)], bg="#F8F6F3", oy=600, clip_bottom=1062, clip_right=760)
# 4 · People rebuild it by hand (V7 S02, the PEOPLE side; 1:1).
a, b = b, S("L04") - 0.12
shot("by_hand", a, b, a - S("L03") + 9.77, [k(9.6, 470, 480, 1.25), k(11.5, 470, 480, 1.28)], bg=LIGHT)
# 5 · Agents start without it (V7 S02, the AI AGENTS side; 1:1).
a, b = b, S("L05") - 0.90
shot("without", a, b, a - S("L04") + 11.62, [k(11.5, 1400, 480, 1.25), k(13.1, 1400, 480, 1.28)])  # left edge clear of the PEOPLE panel (ends at V7 x 960)
# 6 · NAVIS — the reveal (V7 S03, 1:1: the mark lands on "Navis"; the two products branch).
a, b = b, S("L06") - 0.20
shot("reveal", a, b, a - S("L05") + 14.03, [k(13.1, 960, 470, 1.05), k(16.55, 960, 450, 1.08), k(17.3, 960, 470, 0.76), k(17.9, 960, 470, 0.77)], oy=560, feather=True)
# 7 · Inside a company, the Navis App is for people (V7 S05, 1:1: the organization → Today).
a, b = b, S("L07") - 0.15
shot("app_intro", a, b, a - S("L06") + 28.95, [k(28.7, 810, 540, 1.10), k(30.10, 810, 540, 1.12), k(30.13, 620, 560, 1.22), k(32.3, 640, 570, 1.25)], bg=APPBG, oy=600, feather=True)
# 8 · It shows what changed — and why it matters (V7 S06 → S07, 1:1).
a, b = b, S("L08") - 0.15
shot("why", a, b, a - S("L07") + 32.39,
     [k(32.2, 680, 480, 1.25), k(33.64, 680, 480, 1.27), k(33.67, 850, 480, 1.00), k(34.02, 850, 480, 1.01), k(34.05, 850, 470, 0.95), k(34.62, 850, 470, 0.96), k(34.95, 820, 420, 1.28), k(36.0, 820, 420, 1.30)], bg=APPBG)
# 9 · Every fact has its source, its time, and how fresh it is (V7 S07: the sources arrive; then held on the trace).
a = b
b1 = a + 0.90
shot("sources_a", a, b1, 35.75, [k(35.75, 760, 470, 1.20), k(36.65, 770, 470, 1.22)], bg=APPBG)
b2 = b1 + 0.46
# The trace's last pill (Salesforce, not live yet) and the CRM line beside it are V7's CRM detail: clipped in the
# 15 px gap under the Slack pill, over the App window's own white. Scale is fixed so the clip stays in that gap.
shot("sources_b", b1, b2, 37.36, [k(37.36, 820, 560, 1.26), k(37.82, 820, 560, 1.26)], bg="#FFFFFF", clip_bottom=935, clip_fade=10)
b3 = S("L09") - 1.35
shot("sources_hold", b2, b3, 37.80, [k(0, 820, 560, 1.26), k(b3 - b2, 870, 560, 1.26)], bg="#FFFFFF", layout="still", clip_bottom=935, clip_fade=10)
# 10 · the prepared reply (V7 S08: Navis has drafted it).
a, b = b3, S("L09") + 0.18
shot("prepared", a, b, 43.40, [k(43.4, 820, 560, 1.15), k(44.95, 820, 560, 1.18)], bg=APPBG)
# 11 · A person decides. — the cursor reaches Approve & send; the click (V7 S08 → S09, 1:1).
a, b = b, S("L10") - 0.10
shot("decides", a, b, a - S("L09") + 46.07, [k(46.2, 1080, 520, 1.30), k(49.05, 1060, 540, 1.36)], bg=APPBG)
# 12 · Then the company acts. — sending → Gmail accepted → reply sent (V7 S09, 1:1).
a, b = b, E("L10") + 0.25
shot("acts", a, b, a - S("L10") + 49.15, [k(49.05, 560, 470, 1.30), k(49.29, 560, 470, 1.30), k(49.31, 600, 520, 1.25), k(51.3, 600, 520, 1.27)], bg="#FFFFFF")
# 13 · NAVIS DEVELOPER — hard cut into the developer world (V7 S10: Claude Code gets the task).
a, b0 = b, S("L12") - 0.15
b = min(b0, a + (56.10 - 53.55))
shot("dev", a, b, 53.55, [k(53.55, 880, 470, 1.20), k(56.1, 880, 500, 1.26)])
if b0 > b + 0.04:
    shot("dev_hold", b, b0, 56.05, [k(0, 880, 500, 1.26), k(b0 - b, 880, 510, 1.30)], layout="still")
# 14 · Connect once — MCP, API, SDK or CLI (V7 S11, 1:1: ✓ Connected, then each surface lights on its word).
# The terminal (dark) and the Connect page (light) are two shots so each has its own background.
a, b = b0, S("L13") - 0.15
src_a = a - S("L12") + 58.14
a1 = a + (59.35 - src_a)
shot("connect_term", a, a1, src_a, [k(58.0, 425, 480, 1.30), k(59.35, 425, 480, 1.32)])  # macro anchored on the window's left edge → ✓ Connected
a = a1
shot("connect", a, b, a - S("L12") + 58.14,
     [k(59.33, 1025, 470, 0.84), k(59.62, 1025, 470, 0.84),               # Access surfaces: all four cards (420–1630 fit)
      k(59.65, 690, 390, 1.55), k(60.50, 690, 390, 1.56),                 # MCP (on "MCP"); centres keep neighbour slivers < 60 px
      k(60.53, 1320, 390, 1.55), k(61.42, 1320, 390, 1.56),               # API
      k(61.45, 690, 565, 1.55), k(62.82, 690, 565, 1.56),                 # SDK
      k(62.85, 1320, 565, 1.55), k(63.4, 1320, 565, 1.56),                # CLI
      k(63.43, 1025, 470, 0.84), k(63.7, 1025, 470, 0.85)], bg="#F3F1ED", feather=True, top_fade=24, top_cut=58, side_fade=60)  # hide V7's dark strip above the window
# 15 · The agent asks — and gets the company's context, with sources and freshness (V7 S12, 1:1).
# The table's sixth row ("Opportunity still closes Nov 14 · salesforce · Oct 5") is V7's CRM detail and cites
# Salesforce, which is not live yet: each phase clips just above it. V7 re-frames at 68.24 (sources) and 69.04
# (freshness), so the shot is split there; V7 zooms out at 69.67, so its frame 2087 is held to the cut.
a, b = b, S("L14") - 0.15
src_a = a - S("L13") + 64.20
t_b, t_c, t_h = (a + (x - src_a) for x in (68.24, 69.04, 2087 / 30))
shot("context", a, t_b, src_a, [k(64.05, 890, 560, 1.25), k(68.21, 890, 560, 1.27)], bg="#1A1A1A", clip_bottom=771)
shot("context_sources", t_b, t_c, 68.24, [k(68.24, 1020, 600, 1.15), k(69.01, 1020, 600, 1.16)], bg="#1A1A1A", clip_bottom=698)
shot("context_fresh", t_c, t_h, 69.04, [k(69.04, 760, 600, 1.15), k(2087 / 30, 760, 600, 1.155)], bg="#1A1A1A", clip_bottom=698)
shot("context_hold", t_h, b, 2087 / 30, [k(0, 760, 600, 1.155), k(b - t_h, 760, 600, 1.16)], bg="#1A1A1A", clip_bottom=698, layout="still")
# 16 · Navis isn't the model. It supplies the company's truth. → the permission check (V7 S13 API → S14).
# The S14 macro: credential → organization, and the AUTHORIZED card; held on V7's static frame at 77.50
# (V7's other two cards fade in at 77.55–77.9 and cannot be framed whole in 4:5 — they stay in V7).
a, b = b, S("L16") - 0.15
b1 = a + (77.50 - 72.45)
shot("truth", a, b1, 72.45, [k(72.45, 900, 470, 1.00), k(76.30, 900, 470, 1.04), k(76.34, 580, 314, 1.28), k(77.50, 580, 314, 1.31)], oy=470)
shot("truth_hold", b1, b, 77.50, [k(0, 580, 314, 1.31), k(b - b1, 580, 314, 1.33)], oy=470, layout="still")
# 17 · The agent does the work, and the run is on record (V7 S15, 1:1).
# Three shots, each on its own background: the diff (editor), the agent's work (V7 cuts to the zoomed Claude panel
# at frame 2425; framed on the output below the context table, whose Salesforce row is masked), the run on record
# (the Runs page from frame 2443, once V7's crossfade — which still shows that row — has finished).
a, b = b, E("L16") + 0.15
src_a = a - S("L16") + 79.97
t_w, t_r = a + (2425 / 30 - src_a), a + (2439 / 30 - src_a)
shot("run_diff", a, t_w, src_a, [k(79.8, 950, 560, 1.25), k(2425 / 30, 950, 560, 1.27)], bg="#212121")
shot("run_work", t_w, t_r, 2425 / 30, [k(2425 / 30, 954, 683, 1.00), k(2439 / 30, 954, 683, 1.01)], bg="#1A1A1A", top_cut=520, top_fade=20)
shot("run_record", t_r, b, 2443 / 30, [k(2443 / 30, 990, 676, 1.00), k(83.1, 990, 676, 1.02)], bg="#F0EEEA", feather=True)  # V7's dark strip above the window (to y 76) sits above the frame
# 18–19 · the pull-back to both products, one company → SAME FACTS. SAME SOURCES. SAME FRESHNESS.
# ONE UNDERSTANDING. TWO WAYS IN. (V7 S17, 1:1 + type). V7's bridge spans its full width, so it is shown
# whole (s 0.55); V7 y ≤ 712 always lands above social y 720 (cy = 712 − 330 / s), hiding V7's own small
# thesis line. The picture fades out with the type; the mark arrives 6 frames later.
a, b = b, S("L18") - 0.35
shot("thesis", a, b, a - S("L17") + 97.57,
     [k(97.0, 960, 239, 0.55), k(97.5, 960, 239, 0.55), k(98.2, 960, 112, 0.55), k(101.0, 960, 112, 0.55), k(102.6, 960, 180, 0.62), k(104.7, 960, 188, 0.63)],
     oy=390, feather=True, clip_bottom=720, top_fade=60, fade_out=0.35)
# 20 · NavisLabs. (V7 S18, 1:1: the mark on the word) → the tagline → held.
a, b = b, S("L19") - 0.10
shot("name", a, b, a - S("L18") + 118.80, [k(118.2, 960, 400, 1.12), k(121.0, 960, 400, 1.14)], oy=640, feather=True)
a = b
b1 = a + (122.20 - (a - S("L19") + 121.43))
shot("tagline", a, b1, a - S("L19") + 121.43, [k(121.3, 960, 400, 1.14), k(122.2, 960, 400, 1.145)], oy=640, feather=True)
shot("end_hold", b1, END, 122.20, [k(0, 960, 400, 1.145), k(END - b1, 960, 400, 1.16)], oy=640, feather=True, layout="still")
STILLS = [37.80, 56.05, round(2087 / 30, 3), 77.50, 122.20]

for i, x in enumerate(shots[:-1]):
    assert abs(x["at"] + x["dur"] - shots[i + 1]["at"]) < 0.002, (x["id"], shots[i + 1]["id"])
assert abs(shots[-1]["at"] + shots[-1]["dur"] - END) < 0.002

# ------------------------------------------------------------------ overlays (V7 visual language)
overlays = {
    "thesis_words": [
        {"text": "SAME FACTS.", "at": round(L["L17"]["speech_start"] + 0.0, 3), "group": 0},
        {"text": "SAME SOURCES.", "at": round(S("L17") + (CH["P6"]["lines"][1]["start_s"] - CH["P6"]["lines"][0]["start_s"]), 3), "group": 0},
        {"text": "SAME FRESHNESS.", "at": round(S("L17") + (CH["P6"]["lines"][2]["start_s"] - CH["P6"]["lines"][0]["start_s"]), 3), "group": 0},
        {"text": "ONE UNDERSTANDING.", "at": round(S("L17") + (CH["P6"]["lines"][3]["start_s"] - CH["P6"]["lines"][0]["start_s"]), 3), "group": 1},
        {"text": "TWO WAYS IN.", "at": round(S("L17") + (CH["P6"]["lines"][4]["start_s"] - CH["P6"]["lines"][0]["start_s"]), 3), "group": 1},
    ],
    "thesis_end": round(S("L18") - 0.35, 3),
    "disclosure": {"from": round(S("L19") + 1.2, 3), "text": "Interfaces recreated from the Navis source, shown in the launch configuration. Kaveri Freightworks, its people and all customer data are fictional demo data; some waits shortened. Navis Developer is in private preview."},
}

# ------------------------------------------------------------------ captions (burned in, ≤ 2 lines)
SPLIT = {
    "L01": ["Your people and agents", "see different truths."],
    "L02": ["The truth is scattered across", "the systems where work happens."],
    "L05": ["Navis turns those signals", "into one shared understanding."],
    "L06": ["Inside a company,", "the Navis App is for people."],
    "L07": ["It shows what changed —", "and why it matters."],
    "L08": ["Every fact has its source,", "its time, and how fresh it is."],
    "L11": ["The same company's agents", "use Navis Developer."],
    "L12": ["Connect once — through", "MCP, API, SDK or CLI."],
    "L16": ["The agent does the work,", "and the run is on record."],
    "L19": ["The shared understanding", "for your organization."],
}
cues = []
for v in vo:
    if v["id"] == "L13":
        ws = v["words"]
        cues.append({"start": ws[0]["start"], "end": ws[2]["end"] + 0.1, "lines": ["The agent asks —"], "burn": True})
        cues.append({"start": ws[3]["start"], "end": v["speech_end"], "lines": ["and gets the company's context,", "with sources and freshness."], "burn": True})
        continue
    if v["id"] == "L17":
        for i, ln in enumerate(CH["P6"]["lines"]):
            st = S("L17") + (ln["start_s"] - CH["P6"]["lines"][0]["start_s"])
            cues.append({"start": round(st, 3), "end": round(st + ln["end_s"] - ln["start_s"], 3), "lines": [ln["text"]], "burn": False})
        continue
    lines = SPLIT.get(v["id"], [v["text"]])
    cues.append({"start": v["speech_start"], "end": v["speech_end"], "lines": lines, "burn": v["id"] not in ("L18", "L19")})
for c in cues:
    c["end"] = round(max(c["end"], c["start"] + 0.8), 3)
for a_, b_ in zip(cues, cues[1:]):
    a_["end"] = round(min(a_["end"] + 0.25, b_["start"] - 0.05), 3)
for c in cues:
    assert len(c["lines"]) <= 2 and all(len(x) <= 34 for x in c["lines"]), c

# ------------------------------------------------------------------ music edit (Eleven Music track)
DEV_CUT = shots[[s_["id"] for s_ in shots].index("dev")]["at"]
BOTH = shots[[s_["id"] for s_ in shots].index("thesis")]["at"]
NAME = shots[[s_["id"] for s_ in shots].index("name")]["at"]
music = {
    "file": "music/final/v8/score.wav",
    "segments": [
        {"id": "A · tension → Navis lift → warm App pulse", "at": 0.0, "end": round(DEV_CUT + 0.15, 3), "src": round(18.60 - S("L05"), 3), "fade_in": 0.6, "fade_out": 0.3},
        {"id": "B · developer rhythm → precise energy", "at": round(DEV_CUT - 0.15, 3), "end": round(BOTH + 0.6, 3), "src": 53.10 - 0.15 + 0.0, "fade_in": 0.3, "fade_out": 1.2},
        {"id": "C · wide emotional expansion", "at": round(BOTH - 0.6, 3), "end": round(NAME + 0.5, 3), "src": 92.40, "fade_in": 1.2, "fade_out": 1.0},
        {"id": "D · resolve → near silence", "at": round(NAME - 0.5, 3), "end": END, "src": round(118.75 - (S("L18") - (NAME - 0.5)), 3), "fade_in": 1.0, "fade_out": 0.0},
    ],
}
for sg in music["segments"]:
    sg["src_end"] = round(sg["src"] + (sg["end"] - sg["at"]), 3)
    assert sg["src"] >= 0 and sg["src_end"] <= 125.2, sg

# Curves (dB): duck under every spoken line (−6), deeper under key lines (−12), lifts in gaps,
# the held breath after the click, near-silence after "NavisLabs.", a slow decay under the held end frame.
speech = [(v["speech_start"], v["speech_end"], v["key"]) for v in vo]
keyw = [tuple(w) for v in vo for w in v["key_windows"]]
CLICK = sync("L09", 48.85)


def duck(t_):
    d = 0.0
    for a_, b_, key in speech:
        if a_ - 0.15 <= t_ <= b_ + 0.6:
            kf = (t_ - (a_ - 0.15)) / 0.15 if t_ < a_ else (1.0 if t_ <= b_ else 1 - (t_ - b_) / 0.6)
            d = min(d, kf * (-12.0 if key else -6.0))
    for a_, b_ in keyw:
        if a_ - 0.15 <= t_ <= b_ + 0.6:
            kf = (t_ - (a_ - 0.15)) / 0.15 if t_ < a_ else (1.0 if t_ <= b_ else 1 - (t_ - b_) / 0.6)
            d = min(d, kf * -12.0)
    return d


DIPS = [(CLICK, CLICK + 0.3, -8.0, 0.12, "held breath on Approve & send"),
        (E("L18") + 0.15, S("L19") - 0.15, -18.0, 0.4, "near-silence after 'NavisLabs.'"),
        (END - 0.15, END, -40.0, END - 0.15 - E("L19"), "the score decays under the held end frame"),
        (END - 0.15, END, -96.0, 0.25, "silent last frames")]
GAPS = [(b_[1], c_[0]) for b_, c_ in zip(speech, speech[1:]) if c_[0] - b_[1] >= 1.0]


def shape(t_):
    d = 0.0
    for a_, b_ in GAPS:
        if a_ + 0.3 <= t_ <= b_ - 0.15 and not any(x[0] < b_ and x[1] > a_ for x in DIPS[:2]):
            d = max(d, 2.0 * min(1.0, (t_ - a_ - 0.3) / 0.4, (b_ - 0.15 - t_) / 0.4))
    for a_, b_, db, r, _ in DIPS:
        if a_ - r <= t_ <= b_ + r:
            kf = (t_ - (a_ - r)) / r if t_ < a_ else (1.0 if t_ <= b_ else 1 - (t_ - b_) / r)
            d = min(d, kf * db) if db < 0 else d
    return d


def keyframes(fn, step=0.02, eps=0.15):
    n = int(END / step) + 1
    pts = [(round(i * step, 3), round(fn(i * step), 2)) for i in range(n)] + [(END, round(fn(END), 2))]

    def rdp(p):
        if len(p) < 3:
            return p
        (x0, y0), (x1, y1) = p[0], p[-1]
        best, bi = 0.0, 0
        for i in range(1, len(p) - 1):
            x, y = p[i]
            yl = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            if abs(y - yl) > best:
                best, bi = abs(y - yl), i
        return [p[0], p[-1]] if best <= eps else rdp(p[: bi + 1])[:-1] + rdp(p[bi:])
    kk = rdp(pts)
    return {"t": [a_ for a_, _ in kk], "db": [b_ for _, b_ in kk]}


music["gain_db"] = -6.0
music["curves"] = {"duck": keyframes(duck), "shape": keyframes(shape)}
music["dips"] = [{"from": round(a_, 3), "to": round(b_, 3), "db": db, "why": w} for a_, b_, db, _, w in DIPS]

# ------------------------------------------------------------------ SFX (only on visible actions)
def sx(name, at, why, gain=0.0):
    return {"sfx": name, "file": SFXLIB[name]["temp"], "at": round(at, 3), "gain_db": round(SFXLIB[name]["gain_db"] + gain, 1), "why": why}


sfx = [
    sx("source", sync("L01", 0.75), "the person's view appears", -4), sx("source", sync("L01", 1.60), "the agent's view appears", -4),
    *[sx("data", sync("L02", t_), "a piece of the truth lands in its system", -8) for t_ in (7.44, 7.76, 8.08, 8.40)],
    *[sx("click", sync("L03", t_), "copying a fragment by hand", -8) for t_ in (9.92, 10.37, 10.82)],
    sx("reveal", sync("L05", 13.93), "the Navis mark on 'Navis'"),
    sx("click", sync("L07", 34.56), "Why this matters"),
    sx("approve", CLICK, "Approve & send"),
    sx("sent", sync("L10", 49.35), "sending"), sx("gmail", sync("L10", 49.76), "Gmail accepted the message"),
    sx("whoosh", DEV_CUT - 0.05, "hard cut into the developer world"),
    sx("enter", DEV_CUT + (54.71 - 53.55), "the task is sent to the agent", -2),
    sx("connect", sync("L12", 58.56), "✓ Connected"),
    *[sx("surface", sync("L12", t_), "an access surface lights on its word") for t_ in (59.67, 60.54, 61.46, 62.85)],
    sx("retrieve", sync("L13", 64.25), "the agent asks Navis"),
    *[sx("data", sync("L13", 64.85 + 0.12 * i), "a cited fact arrives", -5) for i in range(6)],
    sx("api", shots[[s_["id"] for s_ in shots].index("truth")]["at"] + (72.73 - 72.45), "the API returns sources and freshness"),
    sx("source", shots[[s_["id"] for s_ in shots].index("truth")]["at"] + (76.97 - 72.45), "ALLOWED", -6),
    sx("source", shots[[s_["id"] for s_ in shots].index("truth")]["at"] + (77.88 - 72.45), "OWN SCOPE", -6),
    sx("run", sync("L16", 79.82), "the agent starts the work"),
    sx("complete", sync("L16", 81.39), "the run is on record: Completed", -2),
    sx("lock", sync("L17", 101.35), "one understanding"),
    sx("end", sync("L18", 118.50), "the end lockup — a very subtle resolve", -2),
]
sfx = [e for e in sfx if 0 <= e["at"] < END - 0.5]

plan = {
    "about": "NavisLabs SOCIAL V1 (4:5) — edited from the approved V7 film. Generated by scripts/build-social-v1.py.",
    "fps": FPS, "width": W, "height": H, "duration_s": END, "frames": round(END * FPS),
    "picture": {"proxy": "social/v7-proxy-2880.mp4", "proxy_scale": 1.5, "source": "out/navislabs-v7-review-1080p.mp4", "holds_v7_s": STILLS, "holds_note": "held frames freeze the proxy video itself (identical decoding to the live frames)"},
    "voice": vo, "shots": shots, "overlays": overlays, "captions": cues, "music": music, "sfx": sfx,
}
os.makedirs(os.path.join(ROOT, "src", "social"), exist_ok=True)
with open(os.path.join(ROOT, "src", "social", "navislabs_social_v1_plan.json"), "w") as f:
    json.dump(plan, f, indent=1, ensure_ascii=False)
    f.write("\n")


def ts(x, sep):
    ms = int(round(x * 1000))
    h_, ms = divmod(ms, 3600000)
    m_, ms = divmod(ms, 60000)
    s_, ms = divmod(ms, 1000)
    return f"{h_:02d}:{m_:02d}:{s_:02d}{sep}{ms:03d}"


os.makedirs(os.path.join(ROOT, "captions"), exist_ok=True)
with open(os.path.join(ROOT, "captions", "social-captions.srt"), "w") as f:
    for i, c in enumerate(cues, 1):
        f.write(f"{i}\n{ts(c['start'], ',')} --> {ts(c['end'], ',')}\n" + "\n".join(c["lines"]) + "\n\n")
with open(os.path.join(ROOT, "captions", "social-captions.vtt"), "w") as f:
    f.write("WEBVTT\n\n")
    for i, c in enumerate(cues, 1):
        f.write(f"{i}\n{ts(c['start'], '.')} --> {ts(c['end'], '.')} line:80% position:50% align:center\n" + "\n".join(c["lines"]) + "\n\n")
words = [{"text": (" " if i else "") + w["text"], "startMs": round(w["start"] * 1000), "endMs": round(w["end"] * 1000), "timestampMs": round(w["start"] * 1000), "confidence": None}
         for v in vo for i, w in enumerate(v["words"])]
with open(os.path.join(ROOT, "captions", "social-captions.json"), "w") as f:
    json.dump(words, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"duration {END:.2f} s ({round(END * FPS)} frames) · lines {len(vo)} · shots {len(shots)} · cues {len(cues)} · sfx {len(sfx)}")
for x in shots:
    print(f"  {x['id']:13s} {x['at']:6.2f}–{x['at'] + x['dur']:6.2f}  V7 {x['src_in']:6.2f}  {x['layout']}")
