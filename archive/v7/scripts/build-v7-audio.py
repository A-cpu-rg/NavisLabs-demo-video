#!/usr/bin/env python3
"""V7 audio + sync documents, generated from the film itself.

Writes:
  navislabs_v7_voiceover_screen_map.json   per spoken line: P file, speech start/end, pauses, the
                                           visual beat, camera action, cursor action, SFX, music
                                           state and caption timing — the voice is the master clock
  navislabs_v7_sfx_map.json                every SFX the film plays (from src/config/beats.ts)
  navislabs_v7_music_production_brief.json the final-score brief, locked to the measured voice

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
TL = fa.load("navislabs_v7_voice_timeline.json")
SPEC = fa.load("navislabs_v7_film_spec.json")
AUDIO = fa.load("navislabs_v7_audio_map.json")
MACHINE = fa.load("interaction_state_machine.json")
COPYDOC = fa.load("src/data/navislabs_v7_copy.json")
cfg = json.loads(subprocess.run(["node", os.path.join(ROOT, "scripts", "dump-config.mjs")], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
B = cfg["BEAT"]
END = SPEC["format"]["duration_s"]
SCENES = SPEC["scenes"]
SHOTS = {s["scene"]: s for s in SPEC["shots"]}

# What the camera does in each scene (from the scene files' keyframes, in words).
CAMERA = {
    "S01": "Locked off on PEOPLE | AI AGENTS (0.98 → 1.0 drift through the pause); on 'scattered' a glide out to 0.86 to hold the whole field of systems.",
    "S02": "Static split: the PEOPLE side works, the AI AGENTS side waits; fade to black.",
    "S03": "The mark comes into focus on 'Navis' (a short lens pull, scale 0.965 → 1) with a slow push (1 → 1.025); the two products branch below it.",
    "S04": "Wipe into the light world; a progressive pull-back — close on the connected systems (1.08), wider as each stage is named (1.03 → 0.96 → 0.88), the whole chain on 'next' (0.66).",
    "S05": "Org intro (no camera); the App window rises wide, hard cut to 'Today at a glance', cut to 'Your attention'.",
    "S06": "Macro cut to What changed, cut to the customer priority card; settles for the cursor.",
    "S07": "Push into the 'Why Navis surfaced this' drawer as sources arrive; cut to the evidence opened out (wide, still): the chain email → CRM → meeting → decision → documents → engineering, and the CRM conflict (Nov 14 ≠ Nov 28).",
    "S08": "Macro on 'Waiting on you'; back to the card; push into the drawer and the prepared draft; macro on the sentence the person edits; as the typing ends, a clean cut to Approve & send — the camera is still for 'A person decides.', only the cursor moves.",
    "S09": "Holds on the press; a clean macro cut to the send state on 'Then the company acts.'; a 1.2 s pull-back so the right third holds the same event across the company's systems.",
    "S10": "Wipe to dark; push into Claude Code as the task is typed.",
    "S11": "Members (macro on Add member) → dissolve to the terminal → dissolve to Connect › Access surfaces, each surface lit as it is said.",
    "S12": "Push onto the tool result as facts arrive one by one; macro cuts on SOURCE, then FRESHNESS; cut back to the agent.",
    "S13": "Two panes: the SDK install, then a clean cut to the API response.",
    "S14": "Static, three credentials; the refusal holds.",
    "S15": "The diff, cut to Runs (the run arrives Running), cut into the run's timeline: steps land one by one, then Completed.",
    "S16": "Solo sign-up (cursor) → personal workspace → the company's Members → terminal checkpoint → 'Next session' restore, held through the pause.",
    "S17": "Wide hero; macro cuts to same fact / source / freshness on each word; on 'One understanding.' the camera pulls back (1.03 → 0.93); on 'Two ways in.' both product surfaces are marked.",
    "S18": "Static, quieter: clients swap, the company's record holds; everything clears for the mark, the name, silence, the tagline.",
}


def scene_at(t):
    return next((s for s in SCENES if s["from_s"] <= t < s["to_s"]), SCENES[-1])


def music_at(t):
    sec = next((s for s in AUDIO["music"]["sections"] if s["from_s"] <= t < s["to_s"]), AUDIO["music"]["sections"][-1])
    return f"{sec['id']} {sec['role']}: {sec['brief']}"


cues = []
for line in open(os.path.join(ROOT, "captions", "navislabs-v7.srt")).read().strip().split("\n\n"):
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
    "about": "V6 voiceover screen map: the founder's final performance (P1–P8) is the master clock. Every spoken line with where it lands, what is on screen, the camera, the cursor, the SFX, the music and the captions. Generated by scripts/build-v7-audio.py.",
    "duration_s": END, "chunks": [{k: c[k] for k in ("id", "file", "at_s", "duration_s", "speech_start_s", "speech_end_s", "pauses")} for c in TL["chunks"]],
    "voice_direction": COPYDOC["voice_direction"],
    "lines": rows,
}

# ---- SFX map --------------------------------------------------------------------
CAT_TEXT = {
    "KEYBOARD": "Keystrokes when someone types: the person's sentence, the agent's task, terminal commands.",
    "TERMINAL": "Enter as a command or task is sent; 'Checkpoint recorded'.",
    "MOUSE": "Not used: the cursor moves silently — only a visible press makes a sound.",
    "UI CLICK": "A visible cursor presses a control (never without a visible click).",
    "DATA ARRIVAL": "A signal or a cited fact arrives (S01 fragments, S04 signals, the agent's context rows).",
    "SOURCE APPEAR": "A source chip or evidence row appears (the two views, evidence, across-systems rows, ALLOWED / OWN SCOPE).",
    "MCP CONNECT": "'✓ Connected', and a tiny accent as each access surface (MCP · API · SDK · CLI) lights.",
    "API RESPONSE": "The Developer API returns items, sources, freshness.",
    "CONTEXT RETRIEVAL": "Navis assembles or returns context.",
    "PERMISSION DENIED": "A key without the permission is refused — a low, serious tone, not a game error.",
    "APPROVE": "Approve & send.",
    "SEND": "The approved reply is sent.",
    "GMAIL CONFIRM": "Gmail accepts the message.",
    "RUN START": "The agent starts the work.",
    "RUN COMPLETE": "The last step lands; the run reads Completed.",
    "PRODUCT REVEAL": "The Navis mark on 'Navis'.",
    "TRANSITION": "A move between worlds (soft air, never a swoosh on ordinary moves).",
    "END REVEAL": "The end lockup.",
}
lib = AUDIO["sfx"]["library"]
cats = []
for c in cfg["SFX_CATEGORIES"]:
    ev = sorted((e for e in cfg["SFX_EVENTS"] if e["category"] == c), key=lambda e: e["at"])
    cats.append({"category": c, "meaning": CAT_TEXT[c], "count": len(ev), "events": [{"at_s": round(e["at"], 3), "scene": scene_at(e["at"])["id"], "sound": e["sfx"], "gain_db": round(lib[e["sfx"]]["gain_db"] + e.get("gainDb", 0), 1), "why": e["why"]} for e in ev]})
sfx_map = {
    "about": "Every SFX the V7 film plays, generated from src/config/beats.ts (the code that plays them). Sounds: public/sfx/temp/v7 (synthesized in-project by scripts/make-sfx-v7.py); ElevenLabs Sound Effects versions drop into public/sfx/final/v7 under the same names (scripts/elevenlabs-generate.py).",
    "rules": ["Felt, subtle, realistic, premium; never louder than the voice; important interactions (Approve, Gmail confirm, ✓ Connected, DENIED, run complete) may peak briefly above the music.", "Only for visible actions; silence on purpose.", "No whooshes on ordinary moves, no booms, no trailer hits, no game sounds."],
    "categories": cats, "silences": [{"from_s": round(w["from"], 2), "to_s": round(w["to"], 2), "why": w["why"]} for w in cfg["SFX_SILENCES"]],
    "final_files": [{"file": f"public/{v['final']}", "used": sum(1 for e in cfg["SFX_EVENTS"] if e["sfx"] == k)} for k, v in lib.items()],
    "status": "V7 SFX are synthesized in-project (public/sfx/temp/v7; no third-party rights). ElevenLabs Sound Effects versions are scripted (scripts/elevenlabs-generate.py) but not generated — ELEVENLABS_API_KEY was not available in this environment.",
}

# ---- music brief ------------------------------------------------------------------
key_lines = [{"text": l["text"], "at_s": l["speech_start_s"]} for l in rows if l["key_line"]]
music = {
    "about": "Final-score brief for the V7 film, locked to the founder's measured voice (the master clock). The review cut plays a six-stem score synthesized in-project (scripts/make-score-v7.py) that follows this brief.",
    "deliverable": {"preferred": "six stems, WAV 48 kHz 24-bit stereo, sample-accurate at 0.000 s, each the film's full length: " + ", ".join(f"public/{st['final']} ({st['role']})" for st in AUDIO["music"]["stems"]),
                    "alternative": f"one mixed score at public/{AUDIO['music']['final']} (e.g. Eleven Music; the stems are then muted)", "length_s": END,
                    "end": f"the music almost stops for 'NavisLabs.', a very soft harmonic tail under the tagline, silence from {AUDIO['music']['dips'][-1]['from_s']} s",
                    "loudness": "score alone about −18 to −20 LUFS integrated, true peak ≤ −1 dBTP; the film applies the keyframed curves (−6 dB under every line, −11 dB under the key lines, controlled dips)"},
    "style": AUDIO["music"]["style"],
    "layers": [{"id": st["id"], "role": st["role"], "mix_gain_db": st["gain_db"], "share_of_duck": st["duck"]} for st in AUDIO["music"]["stems"]],
    "arc": [{"range_s": [sx["from_s"], sx["to_s"]], "role": sx["role"], "brief": sx["brief"]} for sx in AUDIO["music"]["sections"]],
    "sync_points": {"music opens": "'Navis' (P2)", "drops back": "'A person decides.'", "returns": "'Then the company acts.'", "slows + low tonal shift": "DENIED", "resolves slightly": "the run reads Completed",
                    "lift": "'One understanding.'", "resolution": "'Two ways in.'", "almost stops": "'NavisLabs.'", "tail": "the tagline"},
    "key_lines_duck_deeper": key_lines,
    "dips": AUDIO["music"]["dips"],
    "voice_first": ["Leave 2–4 kHz open under speech (the stems carry a −3 dB presence dip at 2.8 kHz); no lead melody under a line.", "Let the score rise in the founder's pauses — the curves release 0.6 s after each line."],
    "mix_targets": {"voice_to_music_under_speech_lu": "12–13", "voice_to_music_under_key_lines_lu": "14–16", "music_rise_in_pauses_lu": "4–7", "small_speaker_check": "music audible with a 180 Hz high-pass (laptop / phone)"},
    "forbidden": ["generic corporate", "EDM", "trailer booms / hits / braams", "cyberpunk", "cheesy inspirational piano", "overly dramatic Hollywood score", "constant risers or whooshes", "generic motivational music"],
    "eleven_music": {"endpoint": "POST https://api.elevenlabs.io/v1/music (composition_plan with sections, force_instrumental)", "script": "scripts/elevenlabs-generate.py --music",
                     "status": "not generated — ELEVENLABS_API_KEY was not available here", "terms": "Eleven Music v1 terms: commercial use requires a paid plan; the Starter plan excludes films, advertising and broadcast — use Creator or above for a launch film; check the account's plan before final."},
}

for name, obj in [("navislabs_v7_voiceover_screen_map.json", screen_map), ("navislabs_v7_sfx_map.json", sfx_map), ("navislabs_v7_music_production_brief.json", music)]:
    with open(os.path.join(ROOT, name), "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
print(f"lines {len(rows)} · sfx events {len(cfg['SFX_EVENTS'])} · music sections {len(AUDIO['music']['sections'])}")
