#!/usr/bin/env python3
"""V6 audio + sync documents, generated from the film itself.

Writes:
  navislabs_v6_voiceover_screen_map.json   per spoken line: P file, speech start/end, pauses, the
                                           visual beat, camera action, cursor action, SFX, music
                                           state and caption timing — the voice is the master clock
  navislabs_v6_sfx_map.json                every SFX the film plays (from src/config/beats.ts)
  navislabs_v6_music_production_brief.json the final-score brief, locked to the measured voice

Reads the voice timeline, the film spec, the audio map, the interaction state machine, the
captions and the resolved TS config (scripts/dump-config.mjs).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
TL = fa.load("navislabs_v6_voice_timeline.json")
SPEC = fa.load("navislabs_v6_film_spec.json")
AUDIO = fa.load("navislabs_v6_audio_map.json")
MACHINE = fa.load("interaction_state_machine.json")
COPYDOC = fa.load("src/data/navislabs_v6_copy.json")
cfg = json.loads(subprocess.run(["node", os.path.join(ROOT, "scripts", "dump-config.mjs")], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
B = cfg["BEAT"]
END = SPEC["format"]["duration_s"]
SCENES = SPEC["scenes"]
SHOTS = {s["scene"]: s for s in SPEC["shots"]}

# What the camera does in each scene (from the scene files' keyframes, in words).
CAMERA = {
    "S01": "Locked off on PEOPLE | AI AGENTS (0.98 → 1.0 drift through the pause); on 'scattered' a glide out to 0.86 to hold the whole field of systems.",
    "S02": "Static split: the PEOPLE side works, the AI AGENTS side waits; fade to black.",
    "S03": "Static: the mark lands on 'Navis'; the two products branch below it.",
    "S04": "Wipe into the light world; holds on the connected systems, glides right with the pipeline as each stage is named, pulls back to the whole pipeline on 'next'.",
    "S05": "Org intro (no camera); the App window rises wide, hard cut to 'Today at a glance', cut to 'Your attention'.",
    "S06": "Macro cut to What changed, cut to the Acme priority card; settles for the cursor.",
    "S07": "Push into the 'Why Navis surfaced this' drawer as sources arrive; cut to the evidence opened out (wide, still).",
    "S08": "Macro on 'Waiting on you'; back to the card; push into the drawer and the prepared draft; macro on the sentence the person edits; settles on Approve & send.",
    "S09": "Holds on the press; glides to the send states; pulls back left so the right third holds the same event across the company's systems.",
    "S10": "Wipe to dark; push into Claude Code as the task is typed.",
    "S11": "Members (macro on Add member) → dissolve to the terminal → dissolve to Connect › Access surfaces, each surface lit as it is said.",
    "S12": "Push onto the tool result; macro on SOURCE, then FRESHNESS.",
    "S13": "Two panes: the SDK install, then a glide to the API response.",
    "S14": "Static, three credentials; the refusal holds.",
    "S15": "The diff, cut to Runs, cut into the run's timeline.",
    "S16": "Solo sign-up (cursor) → personal workspace → the company's Members → terminal checkpoint → 'Next session' restore, held through the pause.",
    "S17": "Wide hero; macro cuts to same fact / source / freshness on each word; pull back for the thesis.",
    "S18": "Static, quieter: clients swap, the company's record holds; everything clears for the mark, the name, silence, the tagline.",
}


def scene_at(t):
    return next((s for s in SCENES if s["from_s"] <= t < s["to_s"]), SCENES[-1])


def music_at(t):
    sec = next((s for s in AUDIO["music"]["sections"] if s["from_s"] <= t < s["to_s"]), AUDIO["music"]["sections"][-1])
    return f"{sec['id']} {sec['role']}: {sec['brief']}"


cues = []
for line in open(os.path.join(ROOT, "captions", "navislabs-v6.srt")).read().strip().split("\n\n"):
    parts = line.split("\n")
    a, b = parts[1].split(" --> ")
    to_s = lambda x: int(x[0:2]) * 3600 + int(x[3:5]) * 60 + int(x[6:8]) + int(x[9:12]) / 1000  # noqa: E731
    cues.append({"start_s": round(to_s(a), 3), "end_s": round(to_s(b), 3), "text": " ".join(parts[2:])})

rows = []
for ch in TL["chunks"]:
    for li, ln in enumerate(ch["lines"]):
        a, b = ln["start_s"], ln["end_s"]
        sc = scene_at(a)
        nxt = ch["lines"][li + 1]["start_s"] if li + 1 < len(ch["lines"]) else None
        rows.append({
            "chunk": ch["id"], "p_file": f"public/{ch['file']}", "line": li + 1, "text": ln["text"],
            "speech_start_s": a, "speech_end_s": b,
            "pause_after_s": round(nxt - b, 2) if nxt is not None else None, "marked_pause": ln["pause_after"], "key_line": ln["key"],
            "scene": sc["id"], "visual_beat": SHOTS[sc["id"]]["said"] if sc["id"] in SHOTS else sc["beat"],
            "camera": CAMERA[sc["id"]],
            "cursor": [f"{i['control']}: {s['state']} @ {s['at_s']}s" for i in MACHINE["interactions"] if i["cursor"] for s in i["states"] if a - 0.3 <= s["at_s"] <= b + 0.3],
            "sfx": [f"{e['category']} ({e['sfx']}) @ {round(e['at'], 2)}s — {e['why']}" for e in cfg["SFX_EVENTS"] if a - 0.2 <= e["at"] <= b + 0.2],
            "music": music_at(a) + ("; ducked −14 dB (key line)" if ln["key"] else "; ducked −10 dB"),
            "captions": [c for c in cues if c["start_s"] < b + 0.05 and c["end_s"] > a - 0.05],
        })
screen_map = {
    "about": "V6 voiceover screen map: the founder's final performance (P1–P8) is the master clock. Every spoken line with where it lands, what is on screen, the camera, the cursor, the SFX, the music and the captions. Generated by scripts/build-v6-audio.py.",
    "duration_s": END, "chunks": [{k: c[k] for k in ("id", "file", "at_s", "duration_s", "speech_start_s", "speech_end_s", "pauses")} for c in TL["chunks"]],
    "voice_direction": COPYDOC["voice_direction"],
    "lines": rows,
}

# ---- SFX map --------------------------------------------------------------------
CAT_TEXT = {
    "KEYBOARD": "Keystrokes when someone types: the person's sentence, the agent's task, terminal commands.",
    "TERMINAL ENTER": "One Enter as a command or task is sent.",
    "MCP CONNECTION": "'✓ Connected'.",
    "CONTEXT RETRIEVAL": "Navis assembles or returns context.",
    "SOURCE APPEARING": "A signal, fact or record appears with its source.",
    "CURSOR CLICK": "A visible cursor presses a control (never without a visible click).",
    "PERMISSION DENIED": "A key without the permission is refused — quiet, low.",
    "SAVE": "'Checkpoint recorded'.",
    "APPROVE": "Approve & send.",
    "SENDING": "The approved reply is sent.",
    "GMAIL CONFIRMATION": "Gmail accepts the message.",
    "RUN START": "The agent starts the work.",
    "RUN COMPLETE": "The run is recorded as Completed.",
    "PRODUCT TRANSITION": "A move between worlds (soft air, never a swoosh).",
    "NAVISLABS REVEAL": "The mark: the reveal and the end lockup.",
}
lib = AUDIO["sfx"]["library"]
cats = []
for c in cfg["SFX_CATEGORIES"]:
    ev = sorted((e for e in cfg["SFX_EVENTS"] if e["category"] == c), key=lambda e: e["at"])
    cats.append({"category": c, "meaning": CAT_TEXT[c], "count": len(ev), "events": [{"at_s": round(e["at"], 3), "scene": scene_at(e["at"])["id"], "sound": e["sfx"], "gain_db": round(lib[e["sfx"]]["gain_db"] + e.get("gainDb", 0), 1), "why": e["why"]} for e in ev]})
sfx_map = {
    "about": "Every SFX the V6 film plays, generated from src/config/beats.ts (the code that plays them).",
    "rules": ["The founder's voice always wins: SFX at least 12 dB below speech.", "Only for visible actions; silence on purpose.", "No whooshes on ordinary moves, no booms, no trailer hits."],
    "categories": cats, "silences": [{"from_s": round(w["from"], 2), "to_s": round(w["to"], 2), "why": w["why"]} for w in cfg["SFX_SILENCES"]],
    "final_files": [{"file": f"public/{v['final']}", "used": sum(1 for e in cfg["SFX_EVENTS"] if e["sfx"] == k)} for k, v in lib.items()],
    "status": "temp SFX are synthesized placeholders (public/sfx/temp); final recorded/licensed sounds drop into public/sfx/final with the same names.",
}

# ---- music brief ------------------------------------------------------------------
key_lines = [{"text": l["text"], "at_s": l["speech_start_s"]} for l in rows if l["key_line"]]
music = {
    "about": "Final-score brief for the V6 film, locked to the founder's measured voice (the master clock).",
    "deliverable": {"file": f"public/{AUDIO['music']['final']}", "format": "WAV, 48 kHz, 24-bit, stereo", "length_s": END, "start": "sample-accurate at 0.000 s", "end": f"music resolves under the end card, then silence from {AUDIO['music']['dips'][-1]['from_s']} s",
                    "loudness": "score alone about −16 LUFS integrated, true peak ≤ −1 dBTP (the film applies −7 dB, ducks −10 dB under every line and −14 dB under the key lines)"},
    "style": AUDIO["music"]["style"],
    "arc": [{"range_s": [s["from_s"], s["to_s"]], "role": s["role"], "brief": s["brief"]} for s in AUDIO["music"]["sections"]],
    "key_lines_duck_deeper": key_lines,
    "silences": AUDIO["music"]["dips"],
    "voice_first": ["Leave 120–350 Hz and 2–4 kHz open under speech; no lead melody under a line.", "Let the score rise in the founder's pauses (P1 2.6 s, P2 2.9 s, P5 3.1 s, P7 2.6 s) — those are written into the ducking."],
    "forbidden": ["generic corporate", "EDM", "trailer booms / hits / braams", "cyberpunk", "cheesy inspirational piano", "overly dramatic Hollywood score", "constant risers or whooshes"],
    "status": "brief only — the final score is not generated. A synthesized temp bed following this arc plays in the review cut (public/music/temp/v6/score.wav).",
}

for name, obj in [("navislabs_v6_voiceover_screen_map.json", screen_map), ("navislabs_v6_sfx_map.json", sfx_map), ("navislabs_v6_music_production_brief.json", music)]:
    with open(os.path.join(ROOT, name), "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
print(f"lines {len(rows)} · sfx events {len(cfg['SFX_EVENTS'])} · music sections {len(AUDIO['music']['sections'])}")
