#!/usr/bin/env python3
"""Audio production pack for the approved V4 picture lock.

Writes:
  navislabs_v5_audio_production_plan.json   V01–V26: timing, pace, delivery, sync, ElevenLabs settings
  navislabs_v5_music_production_brief.json  one continuous 100 s score, locked to picture
  navislabs_v5_sfx_map.json                 the meaningful SFX the film plays (from src/config/beats.ts)
  navislabs_v5_audio_readiness_report.md    what to record, generate, deliver; what is assembled automatically

Timing comes from the locked picture (navislabs_v5_voiceover_screen_map.json,
the resolved beats and SFX events); the direction below is authored per line.
Re-run any time (npm run audio:plan): the readiness report re-checks which final
files are present.
"""
import json
import os
import re
import subprocess
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
PUBLIC = os.path.join(ROOT, "public")
vo_map = fa.load("navislabs_v5_voiceover_screen_map.json")
VO = vo_map["voiceover"]
audio = fa.load("navislabs_v5_audio_map.json")
spec = fa.load("navislabs_v5_film_spec.json")
cfg = json.loads(subprocess.run(["node", os.path.join(ROOT, "scripts", "dump-config.mjs")], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
B = cfg["BEAT"]
SCENES = cfg["FILM_SCENES"]
render = json.load(open(os.path.join(ROOT, "navislabs_v5_render_check.json"))) if os.path.isfile(os.path.join(ROOT, "navislabs_v5_render_check.json")) else None
VERIFIED = "elevenlabs.io docs, checked 2026-10-06"


def scene_at(t):
    return next((s["id"] for s in SCENES if s["from"] <= t < s["to"]), SCENES[-1]["id"])


def wav_info(rel):
    p = os.path.join(PUBLIC, rel)
    if not os.path.isfile(p):
        return None
    try:
        with wave.open(p) as w:
            return {"duration_s": round(w.getnframes() / w.getframerate(), 3), "sample_rate": w.getframerate(), "channels": w.getnchannels(), "bits": 8 * w.getsampwidth()}
    except (wave.Error, EOFError):  # e.g. 32-bit float WAV: present, but needs converting to PCM
        return {"duration_s": float("inf"), "sample_rate": 0, "channels": 0, "bits": 0, "unreadable": True}


syllables = fa.syllables


# ---- per-line direction (authored) -------------------------------------------
# intensity: 1 hushed · 2 calm · 3 present · 4 lifted · 5 strong (nothing in this film goes above 3).
# onset: "immediate" = the file starts on the first word (≤ 50 ms of air);
#        "breath"    = a soft, natural in-breath of ≤ 0.2 s may open the file; the first word lands ~0.2 s after start.
# sync: words that must land on a picture beat (± tolerance); "beat" names the picture event.
D = {
 "V01": dict(i=2, onset="breath", style="Low, unhurried, certain. A plain observation about how companies work today — not a hook, not a warning.", emph=["people and agents", "different truths"],
             pause="Land 'answer', then stop. Nothing after it in the file."),
 "V02": dict(i=2, onset="immediate", style="Even, matter-of-fact; a slight weight on 'scattered'. 'The truth' picks up V01's last word.", emph=["truth", "scattered", "work happens"],
             pause="No internal pause; let it end level."),
 "V03": dict(i=2, onset="immediate", style="Dry and observant: two clean sentences, the second a little lower.", emph=["by hand", "without it"],
             pause="0.4–0.5 s between the sentences so 'Agents' lands on the AGENTS side."),
 "V04": dict(i=3, onset="immediate", style="Quiet confidence. Say 'Navis' clearly; then let the line open up.", emph=["Navis", "one shared understanding"],
             pause="None inside; 0.3 s after. The film's 0.45 s silence before the line is the breath — the file starts on 'Navis'."),
 "V05": dict(i=3, onset="breath", style="Precise list, even rhythm; lift slightly on 'signal' — the sentence continues into V06.", emph=["Every", "signal"],
             pause="No full stop: end on a held, rising 'signal —'. Generate together with V06."),
 "V06": dict(i=3, onset="immediate", style="Three building beats; settle on 'next'.", emph=["remembered", "connected", "next"],
             pause="Short commas (~0.15 s); 0.4 s after 'next'."),
 "V07": dict(i=2, onset="breath", style="Warm, plain. Name the product clearly — this is where the people story starts.", emph=["Navis App", "people"],
             pause="Small comma pause after 'organization'."),
 "V08": dict(i=2, onset="immediate", style="Matter-of-fact; the dash is a real beat.", emph=["what changed", "moved"],
             pause="0.2 s at the dash."),
 "V09": dict(i=2, onset="immediate", style="Clear and explanatory: three items with even weight, no list sing-song.", emph=["why", "source", "time", "fresh"],
             pause="'And why:' lands on the click; a 0.15 s colon pause; no other pauses."),
 "V10": dict(i=2, onset="immediate", style="Helpful and natural, like explaining a colleague's tool.", emph=["waiting on you", "drafts the reply"],
             pause="0.2 s after the line."),
 "V11": dict(i=3, onset="breath", style="Firm and quiet. Three words with space around them — the most important human line.", emph=["person", "decides"],
             pause="0.5 s of silence after; nothing else in the file."),
 "V12": dict(i=2, onset="immediate", style="Settled; land it softly. The picture carries the send.", emph=["acts"],
             pause="Starts right after the held breath on Approve; 1.5 s of space after."),
 "V13": dict(i=2, onset="breath", style="Technical, even; a new world, same voice. Name the product clearly.", emph=["same company's", "Navis Developer"],
             pause="0.2 s after."),
 "V14": dict(i=3, onset="immediate", style="Brisk and precise. Spell the acronyms crisply, evenly, without sing-song.", emph=["Invite", "once"],
             pause="0.2 s after 'team.'; the dash after 'once' may hold up to 0.4 s; 0.1 s between acronyms."),
 "V15": dict(i=2, onset="immediate", style="Precise; a small beat at the dash.", emph=["asks", "cited facts", "freshness"],
             pause="0.2 s at the dash."),
 "V16": dict(i=3, onset="immediate", style="Firm, two short statements; no emphasis spike on 'isn't'.", emph=["isn't the model", "company's truth"],
             pause="0.2 s between the sentences."),
 "V17": dict(i=2, onset="breath", style="Quiet and serious — lower energy than the lines around it.", emph=["Every request", "permissions"],
             pause="0.4 s after; the refusal plays in near-silence."),
 "V18": dict(i=2, onset="immediate", style="Matter-of-fact, even.", emph=["does the work", "on record"],
             pause="0.3 s after."),
 "V19": dict(i=2, onset="breath", style="Encouraging, light, understated — one person, not a company.", emph=["solo builder", "private workspace", "next session"],
             pause="0.2 s at the dash."),
 "V20": dict(i=2, onset="breath", style="Grounded. A full stop after 'One company.'", emph=["One company", "same event"],
             pause="0.3 s after 'One company.'"),
 "V21": dict(i=2, onset="immediate", style="Measured: three equal beats, same pitch shape each time.", emph=["facts", "sources", "freshness"],
             pause="~0.6 s between phrases so each lands on its macro cut."),
 "V22": dict(i=3, onset="immediate", style="Quiet conviction.", emph=["One understanding", "Two ways in"],
             pause="0.4 s between the sentences; 0.6 s after."),
 "V23": dict(i=2, onset="immediate", style="Thoughtful; three equal beats.", emph=["Models", "Agents", "Tools"],
             pause="~0.6 s between phrases."),
 "V24": dict(i=3, onset="immediate", style="Firm and quiet; land 'yours'. Ownership, stated plainly — no swell.", emph=["knows", "yours"],
             pause="None inside; 0.3 s after."),
 "V25": dict(i=3, onset="immediate", style="Confident, three beats, each a little warmer.", emph=["Company-owned", "Model-neutral", "people and agents"],
             pause="~0.45 s between phrases."),
 "V26": dict(i=2, onset="immediate", style="Quiet and final. Name, pause, line; let it end in silence.", emph=["NavisLabs", "shared understanding"],
             pause="0.5 s after 'NavisLabs.'; nothing after the line."),
}
EXTRA_BEATS = {
    "agentTaskTyping": cfg["TYPING"]["agentTask"]["start"] + 0.5,
    "pillar1": B["pillars"], "pillar2": B["pillars"] + 1.0, "pillar3": B["pillars"] + 2.1,
}
BEAT_LABEL = {
    "signalDecision": "first Acme signal lands", "scatter": "the line breaks; signals scatter", "peopleStart": "PEOPLE side: copy by hand",
    "agentsStart": "AGENTS side: empty session", "logoWord": "NavisLabs wordmark", "iconsIn": "live systems appear", "flowIntel": "Intelligence stage",
    "flowLearning": "Learning (Next)", "appRise": "the Navis App window rises", "whatChanged": "What changed", "priorityFocus": "the Acme priority card",
    "whyClick": "click: Why this matters", "waiting": "Waiting on you", "draftShown": "the draft appears", "selectStart": "the person selects a sentence",
    "approved": "Approved — sending", "agentTaskTyping": "the task is typed to the agent", "addMember": "click: Add member", "mcpConnected": "✓ Connected",
    "contextCall": "navis_get_relevant_context", "contextFresh": "freshness column", "modelNeutral": "'No model is called'", "permDenied": "denied key",
    "agentUses": "the agent edits the file", "runRow": "run row: Completed", "soloWorkspace": "Personal workspace", "soloDayTwo": "Next session",
    "heroIn": "One company · NavisLabs", "sameFacts": "macro: same fact", "sameSources": "macro: same source", "sameFreshness": "macro: same freshness",
    "sharedUnderstanding": "thesis line", "peopleAgents": "People + AI agents", "modelsChange": "Models change.", "agentsChange": "Agents change.",
    "toolsChange": "Tools change.", "staysYours": "'What it knows stays yours.'", "pillar1": "pillar: Company-owned", "pillar2": "pillar: Model-neutral",
    "pillar3": "pillar: Shared by people + agents", "endLockup": "end lockup", "endTagline": "headline on the end card",
}
PRON = {
    "NavisLabs": "NavisLabs — one word. The current map says NAV-iss-labs /ˈnævɪs læbz/; CONFIRM with the founder. Whatever he says naturally is correct; use it identically in V04 and V26.",
    "Navis": "Navis — the founder's own pronunciation, identical in every line (V04, V07, V10, V13, V16) and as the first part of NavisLabs (V26). The notes assume NAV-iss /ˈnævɪs/ — confirm.",
    "Acme": "Acme — AK-mee /ˈækmi/.",
    "MCP": "MCP — em-see-pee", "API": "API — ay-pee-eye", "SDK": "SDK — ess-dee-kay", "CLI": "CLI — see-el-eye",
    "Model-neutral": "Model-neutral — one compound, stress on MOD and NEU.",
    "company's": "company's — keep the possessive audible (V13, V16).",
}
PASSAGES = [("P1 · Problem", ["V01", "V02", "V03"]), ("P2 · Navis + data flow", ["V04", "V05", "V06"]),
            ("P3 · Navis App", ["V07", "V08", "V09", "V10", "V11", "V12"]), ("P4 · Navis Developer", ["V13", "V14", "V15", "V16", "V17", "V18"]),
            ("P5 · Solo + one company", ["V19", "V20", "V21", "V22"]), ("P6 · What stays yours + name", ["V23", "V24", "V25", "V26"])]
PASSAGE_OF = {v: name for name, ids in PASSAGES for v in ids}
def settings(line, d):
    """eleven_v4 exposes two voice settings only: Stability and Similarity.
    Style and Speed are not available in v4, so nothing else is written here.
    Start every line at 0.5 / 0.8; nudge Stability up for the firm, short lines."""
    stability = 0.55 if d["i"] >= 3 or line["elevenlabs"]["pace"] == "slow" else 0.5
    return {"stability": stability, "similarity": 0.8}


lines = []
for l in VO:
    d = D[l["id"]]
    text = l["voice_line"]
    words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", text))
    syl = syllables(text)
    target = round(l["end_s"] - l["start_s"], 2)
    mx = l["max_duration_s"]
    sps_t, sps_m = syl / target, syl / mx
    check = "relaxed" if sps_m <= 4.0 else ("natural" if sps_m <= 4.8 else "tight")
    window = [(k, v) for k, v in B.items() if v > 0 and l["start_s"] - 0.15 <= v <= l["ceiling_s"]]
    window.sort(key=lambda kv: kv[1])
    # One definition of every sync point: the caption beats in the screen map.
    sync = [{"phrase": c["phrase"], "lands_at_s": c["lands_at_s"], "picture": c["picture"], "tolerance_s": c["tolerance_s"]} for c in l["caption_beats"]]
    pron = [PRON[k] for k in PRON if re.search(rf"\b{re.escape(k)}\b", text)]
    tag = l["elevenlabs"]["audio_tag"]
    st = settings(l, d)
    temp = wav_info(l["temp"])
    lines.append({
        "id": l["id"], "scene": l["scene"], "file": f"V{l['id'][1:]}.wav", "final_path": f"public/{l['final']}",
        "text": text,
        "start_s": l["start_s"], "hard_end_s": l["ceiling_s"],
        "target_duration_s": target, "max_duration_s": mx,
        "word_count": words, "syllables": syl,
        "words_per_sec": round(words / target, 2), "syllables_per_sec": round(sps_t, 2), "syllables_per_sec_at_max": round(sps_m, 2),
        "pace_check": check,
        "delivery_style": d["style"], "pace": l["elevenlabs"]["pace"],
        "emotional_intensity": {"level": d["i"], "of": 5, "label": {1: "hushed", 2: "calm", 3: "present", 4: "lifted", 5: "strong"}[d["i"]], "emotion": l["elevenlabs"]["emotion"]},
        "pause_requirements": d["pause"],
        "emphasis_words": d["emph"],
        "pronunciation_notes": pron,
        "onset": "immediate" if d["onset"] == "immediate" else "after a short breath",
        "onset_rule": "file starts on the first word (≤ 50 ms of air)" if d["onset"] == "immediate" else "a soft in-breath of ≤ 0.2 s may open the file; the first word lands ~0.2 s after start_s",
        "on_screen": {"while_spoken": l["visual"], "picture_events_in_window": [{"at_s": round(v, 2), "event": BEAT_LABEL.get(k, k)} for k, v in window]},
        "phrase_sync": sync,
        "elevenlabs": {
            "model": "eleven_v4 with Abhishek Meena's cloned voice",
            "text_v4": f"{tag} {text}" if tag else text,
            "text_plain": text,
            "audio_tag_optional": tag,
            "voice_settings": st,
            "generate_in": PASSAGE_OF[l["id"]],
            "notes": ("Tight slot: natural pace, no added pauses. eleven_v4 has no Speed control, so pace comes from the text and the take; if a take is up to 0.2 s long, Claude tightens the pause at the dash or full stop in post (an edit, never a time-stretch); longer than that, regenerate." if check == "tight" else "Audition 3 takes; keep the one that sounds like the founder talking, not reading."),
        },
        "temp_take_s": temp["duration_s"] if temp else None,
    })

tight = [x["id"] for x in lines if x["pace_check"] == "tight"]
plan = {
    "about": "Audio production plan for the V5 script on the locked V4 timings. One entry per voice line V01–V26: exact text, locked timing, pace, delivery, sync points (= caption beats) and ElevenLabs settings. Generated by scripts/build-audio-production.py from navislabs_v5_voiceover_screen_map.json and the resolved beats.",
    "picture": {"locked_timings": True, "reference": "out/navislabs-v5-picture-lock-1080p.mp4", "fps": 30, "duration_s": 100},
    "voice": {
        "who": "Abhishek Meena — his own voice, or an ElevenLabs Professional Voice Clone of it made with his explicit permission. No other voice.",
        "character": vo_map["direction"],
        "pace_reference": "calm founder narration ≈ 3.5–4.5 syllables/s; 'tight' means the hard end forces more than 4.8 syllables/s",
    },
    "elevenlabs_defaults": {
        "verified_against": VERIFIED,
        "model": "eleven_v4 with Abhishek Meena's cloned voice (Professional Voice Clones are fully supported in eleven_v4).",
        "voice_settings": {"stability": 0.5, "similarity": 0.8},
        "not_available_in_v4": "Style and Speed sliders are not available in eleven_v4; speaker boost is not listed as a v4 setting. Do not look for them — pace and emphasis come from the text, punctuation and retakes.",
        "if_another_model_is_used": "Only if v4 is unusable for a line: eleven_multilingual_v2 exposes Style (start 0), Speaker boost (on) and Speed (1.0). The plan does not depend on them.",
        "post": "The final audio may be trimmed and aligned in post (heads, tails, the pause at a dash or full stop) without changing the narration. Never time-stretch.",
        "pauses": "eleven_v4 does not support SSML: use punctuation (commas, full stops, dashes, ellipses) and line structure",
        "pronunciation": "eleven_v4: IPA between slashes inline, e.g. /ˈnævɪs/, only if the clone mispronounces 'Navis' (results can vary — audition)",
        "audio_tags": "sparingly: 8 of 26 lines carry an optional tag; drop any tag that makes the read sound acted",
        "output": "request 48 kHz PCM / WAV (or the highest-quality MP3 if PCM is unavailable); Claude converts to 48 kHz, 24-bit, mono WAV",
        "generation": "generate one passage at a time (P1–P6) for a consistent tone; Claude splits each passage take at its pauses into V01–V26. Per-line generation also works.",
    },
    "passages": [{"id": name, "lines": ids, "text_v4": "\n\n".join(next(x["elevenlabs"]["text_v4"] for x in lines if x["id"] == i) for i in ids)} for name, ids in PASSAGES],
    "summary": {"lines": len(lines), "words": sum(x["word_count"] for x in lines), "tight_lines": tight,
                "breath_onsets": [x["id"] for x in lines if x["onset"] != "immediate"], "phrase_sync_lines": [x["id"] for x in lines if len(x["phrase_sync"]) > 1]},
    "lines": lines,
}

# ---- music brief -------------------------------------------------------------
def vo_density(a, b):
    busy = sum(max(0.0, min(b, l["end_s"]) - max(a, l["start_s"])) for l in VO)
    return round(busy / (b - a), 2)


SECTION_TEXT = {
    "restrained": ("Problem — restrained, almost silent", "A low, soft bed (sustained low strings or a warm synth pad, very quiet); no pulse, no melody. Distant, sparse glints at most.", "−30 to −24 dB relative to full score level",
                   "The voice opens the film over near-silence. At 10.0–10.45 s everything stops (full rest): the NavisLabs mark arrives on silence plus one tonal SFX. Do not score the reveal with a hit."),
    "emergence": ("Subtle brand emergence", "A gentle harmonic opening under the two products and the light data-flow world: a soft motif (2–4 notes) introduced on piano or mallet, a slow pad lift. Allow a very light pulse from ~14.3 s (the wipe to light).", "−24 to −18 dB",
                  "Infrastructure, not spectacle: the pipeline builds stage by stage; let the music breathe with it. No riser into 22 s."),
    "human": ("Human / organizational", "Warm and unhurried: piano, soft strings or warm pads; the motif becomes human. Light movement, no driving rhythm.", "−22 to −16 dB",
              "A person's day: Today, why, the draft, a human edit. Full rest on Approve & send (40.95–41.2 s), then a small, warm resolution as the reply is sent (42.8 s)."),
    "technical": ("Technical developer momentum", "Precise, light rhythm (muted plucks, soft arpeggio, restrained electronic pulse ~100–108 BPM feel); bass enters gently. Clean and modern, never aggressive.", "−20 to −15 dB",
                  "Terminal, MCP, context, SDK, API, permissions, the run. Pull right back (−18 dB) under the refusal 60.9–62.1 s — quieter, not tense. Lighter again for the solo developer from 66.6 s."),
    "convergence": ("Convergence / shared understanding", "The human motif and the technical pulse meet: the warm harmony returns over a softened pulse. By 73.4 s (One company) both motifs are present.", "−20 to −15 dB",
                    "Same facts, same sources, same freshness (77.7–79.9 s): keep the music steady with no accents — the voice and the macro cuts carry it."),
    "conviction": ("Conviction / moat", "Grounded and steady: sustained harmony, a slow, confident pulse; the motif stated once, simply. No riser, no drum build.", "−20 to −15 dB",
                   "Models change, agents change, tools change; what it knows stays yours. Ownership stated with restraint — no swell, no build."),
    "resolve": ("Resolution → silence", "One resolving chord or the motif's last statement under the end card; decay naturally to silence.", "fade from −22 dB to silence",
                "The end lockup lands at 94.0 s; the score must be fully silent from 98.6 s to 100.0 s."),
}
SYNC = [
    (0.0, "film start", "silence; the bed may enter softly under V01 (0.6 s)"),
    (B["blackout"], "black before NavisLabs", "full rest (score silent) 10.0–10.45 s"),
    (B["logoTile"], "NavisLabs mark", "no hit; the tonal SFX carries it; the score re-enters softly after"),
    (B["archApp"], "the two products branch", "M2 emergence begins around here (brief: 12 s)"),
    (B["toLight"], "wipe to the light data-flow world", "gentle lift allowed; no whoosh, no hit"),
    (22.6, "cut: the company (Navis App act)", "M3 human texture by 22.6 s (brief: 22 s)"),
    (B["approveClick"], "Approve & send", "full rest 40.95–41.2 s (held breath)"),
    (B["replySent"], "Reply sent", "small, warm resolution"),
    (B["devCut"], "cut to dark: Navis Developer", "M4 technical momentum from here (brief: 45 s)"),
    (B["mcpConnected"], "✓ Connected", "optional subtle accent, under −6 dB relative"),
    (B["refusal"], "the exact refusal", "score −18 dB until 62.1 s; no tension cue"),
    (B["soloIn"], "solo developer", "lighter texture"),
    (68.0, "brief: convergence begins", "start bringing the human motif back over the pulse"),
    (B["heroIn"], "One company · NavisLabs", "both motifs present"),
    (B["staysYours"], "What it knows stays yours.", "steady; no swell, no build"),
    (B["sameFacts"], "same fact / source / freshness macros", "steady, no accents (77.7–79.9 s)"),
    (82.0, "brief: conviction / moat", "settle into a grounded pulse"),
    (84.0, "cut: Models change. Agents change. Tools change.", "steady; no build"),
    (B["endLockup"], "end lockup", "resolve"),
    (98.6, "silence", "score fully silent to 100.0 s"),
]
sections = []
for s in audio["music"]["sections"]:
    title, inst, level, note = SECTION_TEXT[s["role"]]
    anchors = [{"at_s": round(t, 2), "picture": what} for t, what, _ in SYNC if s["from_s"] <= t < s["to_s"]]
    sections.append({"id": s["id"], "range_s": [s["from_s"], s["to_s"]], "character": title, "brief": s["brief"], "instrumentation": inst,
                     "relative_level": level, "vo_density": vo_density(s["from_s"], s["to_s"]), "picture": note, "picture_anchors": anchors,
                     "scenes": [sc["id"] for sc in SCENES if sc["from"] < s["to_s"] and sc["to"] > s["from_s"]]})
music = {
    "about": "Music production brief: one continuous 100-second score for the approved V4 picture lock. The founder's voice is always dominant.",
    "deliverable": {"file": f"public/{audio['music']['final']}", "format": "WAV, 48 kHz, 24-bit, stereo", "length_s": 100.0,
                    "start": "sample-accurate at 0.000 s (the film's first frame)", "end": "fully silent from 98.6 s to 100.0 s",
                    "loudness": "score alone: about −16 LUFS integrated, true peak ≤ −1 dBTP (the film applies −7 dB and ducks −9 dB under every voice line)",
                    "stems_optional": ["bed / pads", "pulse / rhythm", "motif (piano / mallet)", "textures"]},
    "reference": {"video": "out/navislabs-v4-picture-lock-1080p.mp4 (temp voice and temp score; mute the temp score while composing)",
                  "voice_timing": "navislabs_v5_audio_production_plan.json"},
    "voice_first": [
        "The founder's voice is always dominant: leave 120–350 Hz and 2–4 kHz open while he speaks.",
        "No lead melody under a voice line; state the motif between lines.",
        f"Ducking is automatic: −{abs(audio['music']['duck_under_vo_db'])} dB under each line (attack {audio['music']['duck_attack_s']} s, release {audio['music']['duck_release_s']} s). Write so the ducked score still sounds intentional.",
    ],
    "forbidden": ["generic corporate music (ukulele, claps, 'inspiring' piano-pop)", "trailer drums, booms, braams, impacts", "excessive risers or reverse swells", "constant whooshes",
                  "'AI' clichés: fast glittery arpeggios, robotic vocoder", "vocals or choirs with words", "a hit on the NavisLabs reveal", "anything louder than the voice"],
    "arc": [{"range_s": [s["from_s"], s["to_s"]], "character": SECTION_TEXT[s["role"]][0]} for s in audio["music"]["sections"]],
    "sections": sections,
    "sync_points": [{"at_s": round(t, 2), "picture": what, "music": action} for t, what, action in SYNC],
    "silences": audio["music"]["dips"],
    "tempo": "Score to picture, not to a grid: picture events are not on a beat grid. A ~100–108 BPM feel suits 45–68 s; elsewhere free time or very slow pulse.",
    "status": "brief only — the final score is not generated. A temp score that follows this arc plays in the current cut.",
}

# ---- SFX map -------------------------------------------------------------------
CAT_TEXT = {
    "KEYBOARD": "Real keystrokes when someone types: the person's sentence, the agent's task, terminal commands.",
    "TERMINAL ENTER": "One Enter as a command or task is sent.",
    "MCP CONNECTION": "The moment Navis connects to the agent: '✓ Connected'.",
    "CONTEXT RETRIEVAL": "Navis assembles or returns context: memory → context, the tool call, the API response, the restored work state.",
    "SOURCE APPEARING": "A signal or fact appears with its source.",
    "CURSOR CLICK": "A visible cursor presses a control.",
    "PERMISSION DENIED": "A key without the permission is refused — quiet, low.",
    "SAVE": "Work state is saved: 'Checkpoint recorded'.",
    "APPROVE": "The person approves: Approve & send.",
    "SENDING": "The approved reply is sent.",
    "GMAIL CONFIRMATION": "Gmail accepts the message.",
    "RUN START": "The agent starts the work.",
    "RUN COMPLETE": "The run is recorded as Completed.",
    "PRODUCT TRANSITION": "A move between worlds: into the light data flow, into the Navis App, into Navis Developer, into the shared view.",
    "NAVISLABS REVEAL": "The NavisLabs mark: the reveal and the end lockup.",
}
lib = audio["sfx"]["library"]
by_cat = {c: [] for c in cfg["SFX_CATEGORIES"]}
for e in cfg["SFX_EVENTS"]:
    by_cat[e["category"]].append(e)
categories = []
for c in cfg["SFX_CATEGORIES"]:
    evs = sorted(by_cat[c], key=lambda e: e["at"])
    entry = {"category": c, "meaning": CAT_TEXT[c], "sounds": sorted({e["sfx"] for e in evs}), "count": len(evs)}
    if c == "KEYBOARD":
        runs = []
        for e in evs:
            if runs and e["why"] == runs[-1]["why"] and e["at"] - runs[-1]["to_s"] < 0.3:
                runs[-1]["to_s"] = round(e["at"], 3)
                runs[-1]["keystrokes"] += 1
            else:
                runs.append({"from_s": round(e["at"], 3), "to_s": round(e["at"], 3), "keystrokes": 1, "why": e["why"], "scene": scene_at(e["at"])})
        entry["runs"] = runs
    else:
        entry["events"] = [{"at_s": round(e["at"], 3), "scene": scene_at(e["at"]), "sound": e["sfx"], "gain_db": round(lib[e["sfx"]]["gain_db"] + e.get("gainDb", 0), 1), "why": e["why"]} for e in evs]
    categories.append(entry)
sfx_map = {
    "about": "Every sound effect the film plays, generated from src/config/beats.ts (SFX_EVENTS) — this map and the film cannot disagree. Only the fifteen meaningful categories are used; everything else is silent on purpose.",
    "rules": ["The founder's voice is always dominant: SFX sit at least 12 dB below speech.", "Quiet, physical, precise: keys, trackpad clicks, soft tones. No whooshes on ordinary moves, no booms, no risers.",
              "Silence is a sound: the windows below have no SFX at all.", "Product transitions are a soft air, never a swoosh."],
    "layers_db": audio["layers"],
    "categories": categories,
    "silences": [{"from_s": round(w["from"], 2), "to_s": round(w["to"], 2), "why": w["why"]} for w in cfg["SFX_SILENCES"]],
    "deliberately_silent": [
        "S01 the scatter (the voice says 'scattered')", "S03 the two products branching", "S04 each pipeline stage resolving (the data flow is carried by music)",
        "S08 the selection ending; the 'Saved → Save changes' state (nothing is saved there)", "S11 'Invited' row; the four Connect cards (the voice names MCP, API, SDK, CLI)",
        "S13 'added 1 package'", "S14 authorized and own-scope keys (only the denial sounds)", "S15 opening the run (no visible cursor)",
        "S17 the same fact / source / freshness macros (the voice carries them)", "S18 agent clients changing and the company's record appearing (the voice carries V24)",
    ],
    "final_files": [{"file": f"public/{v['final']}", "categories": sorted({e["category"] for e in cfg["SFX_EVENTS"] if e["sfx"] == k}), "gain_db": v["gain_db"], "used": sum(1 for e in cfg["SFX_EVENTS"] if e["sfx"] == k)} for k, v in lib.items()],
    "status": "temp SFX are synthesized placeholders (public/sfx/temp); final files are optional drop-ins with the same names in public/sfx/final.",
}

# ---- write JSON ------------------------------------------------------------------
for name, obj in [("navislabs_v5_audio_production_plan.json", plan), ("navislabs_v5_music_production_brief.json", music), ("navislabs_v5_sfx_map.json", sfx_map)]:
    with open(os.path.join(ROOT, name), "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")

# ---- readiness report --------------------------------------------------------------
final_vo = {x["id"]: wav_info(VO[i]["final"]) for i, x in enumerate(lines)}
vo_ok = {k: (v is not None and v["sample_rate"] == 48000 and v["duration_s"] <= next(x["max_duration_s"] for x in lines if x["id"] == k) + 0.05) for k, v in final_vo.items()}
score = wav_info(audio["music"]["final"])
sfx_final = {k: wav_info(v["final"]) for k, v in lib.items()}
val = fa.load("navislabs_v5_validation_report.json")
_audit_path = os.path.join(ROOT, "navislabs_v5_narrative_product_audit.json")
audit = json.load(open(_audit_path)) if os.path.isfile(_audit_path) else {"READY_FOR_VOICEOVER": "pending audit", "READY_FOR_PICTURE_LOCK": "pending audit"}
ready_final = all(vo_ok.values()) and score is not None and val["all_pass"]

R = []
w = R.append
w("# NavisLabs V5 — audio readiness report")
w("")
w("V5 script (26 founder-approved lines) on the **locked V4 timings**. This report covers audio production only. Generated by `scripts/build-audio-production.py` (`npm run audio:plan`); re-run it after dropping in files and the status columns update.")
w("")
w(f"| READY_FOR_PICTURE_LOCK | READY_FOR_VOICEOVER | Ready for music (scores to the locked picture) | Final VO present | Final score present | READY_FOR_FINAL_RENDER |")
w("|---|---|---|---|---|---|")
w(f"| **{str(audit.get('READY_FOR_PICTURE_LOCK')).lower()}** | **{str(audit.get('READY_FOR_VOICEOVER')).lower()}** | **{str(audit.get('READY_FOR_PICTURE_LOCK')).lower()}** | {sum(vo_ok.values())}/26 | {'yes' if score else 'no'} | **{str(ready_final).lower()}** |")
w("")
w("## 1. Exact ElevenLabs files required")
w("")
w("26 voice files — one per line — and nothing else from ElevenLabs. Music and SFX are separate (sections 5–6).")
w("")
w("Folder: `public/voiceover/final/v4/` (the slot folder keeps its v4 name on purpose — nothing else to configure). Format: WAV, 48 kHz, 24-bit (16-bit accepted), mono. Claude converts other formats on delivery.")
w("")
w("## 2. Exact filenames")
w("")
w("`V01.wav` `V02.wav` `V03.wav` `V04.wav` `V05.wav` `V06.wav` `V07.wav` `V08.wav` `V09.wav` `V10.wav` `V11.wav` `V12.wav` `V13.wav` `V14.wav` `V15.wav` `V16.wav` `V17.wav` `V18.wav` `V19.wav` `V20.wav` `V21.wav` `V22.wav` `V23.wav` `V24.wav` `V25.wav` `V26.wav`")
w("")
w("## 3. Duration target for every file")
w("")
w("Target = the planned read. Max = the hard limit: anything longer is cut by the next line or the scene. Pace: syllables per second if the read uses the full max (calm founder narration ≈ 3.5–4.5; tight > 4.8).")
w("")
w("| File | Text | Starts | Target | Max (hard end) | Words | Pace | Onset | Status |")
w("|---|---|---|---|---|---|---|---|---|")
for x in lines:
    st = final_vo[x["id"]]
    status = "missing" if st is None else (f"✓ {st['duration_s']} s" if vo_ok[x["id"]] else f"✗ {st['duration_s']} s / {st['sample_rate']} Hz")
    w(f"| {x['file']} | {x['text']} | {x['start_s']} s | {x['target_duration_s']} s | {x['max_duration_s']} s ({x['hard_end_s']} s) | {x['word_count']} | {x['syllables_per_sec_at_max']} syl/s · {x['pace_check']} | {x['onset']} | {status} |")
w("")
if tight:
    w(f"**Tight lines: {', '.join(tight)}.** Read at a natural pace with no added pauses (eleven_v4 has no Speed control — pace comes from the text and the take). If a take is up to 0.2 s long, Claude tightens the pause at the dash or full stop in post — an edit, never a time-stretch. Longer than that, regenerate the line.")
    w("")
w("## 4. ElevenLabs delivery / settings")
w("")
e = plan["elevenlabs_defaults"]
w(f"Checked against the {VERIFIED}.")
w("")
w(f"- **Voice:** {plan['voice']['who']}")
w(f"- **Model:** {e['model']}")
w("- **Settings (eleven_v4 exposes only these two):** Stability ≈ 0.5 · Similarity ≈ 0.8. Per-line values in `navislabs_v5_audio_production_plan.json` (Stability 0.5–0.55, Similarity 0.8).")
w("- **Not available in eleven_v4:** Style and Speed (no sliders), and speaker boost is not a listed v4 setting. Nothing in this project assumes them; pace and emphasis come from the text, punctuation and retakes, and timing is finished in post by trimming (never time-stretching).")
w(f"- **Pauses:** {e['pauses']}.")
w(f"- **Pronunciation:** {e['pronunciation']}. **Confirm how the founder says 'Navis'** before generating; the map currently assumes NAV-iss.")
w(f"- **Audio tags:** {e['audio_tags']}.")
w(f"- **How to generate:** {e['generation']}")
w(f"- **Output:** {e['output']}.")
w("- **Character:** calm, deep, precise, technical, confident, understated, founder-led — natural to Abhishek's own accent. **Not:** a commercial announcer, a trailer voice, an AI voice, overly American, overly dramatic, or fast social-media narration.")
w("")
w("Passages to paste (optional audio tags shown; remove them for multilingual v2):")
w("")
for p in plan["passages"]:
    w(f"**{p['id']}** ({', '.join(p['lines'])})")
    w("")
    w("```text")
    w(p["text_v4"])
    w("```")
    w("")
w("Lines whose phrases must land on picture beats (Claude aligns them on delivery):")
w("")
for x in lines:
    if len(x["phrase_sync"]) > 1 or x["id"] in ("V09", "V12"):
        w(f"- **{x['id']}** — " + "; ".join(f"“{s['phrase']}” at {s['lands_at_s']} s ({s['picture']})" for s in x["phrase_sync"]))
w("")
w("## 5. Music requirements")
w("")
w(f"- One continuous score, `{music['deliverable']['file']}`: {music['deliverable']['format']}, exactly 100.0 s, starting at 0.000 s, silent from 98.6 s.")
w(f"- Loudness: {music['deliverable']['loudness']}.")
w("- Arc:")
for a in music["arc"]:
    w(f"  - {a['range_s'][0]:g}–{a['range_s'][1]:g} s — {a['character']}")
w("- Full rests: 10.0–10.45 s (before NavisLabs), 40.95–41.2 s (Approve & send), 98.6–100 s. Pull back to −18 dB during the refusal (60.9–62.1 s).")
w("- Forbidden: " + "; ".join(music["forbidden"]) + ".")
w("- The voice is always dominant: leave 120–350 Hz and 2–4 kHz open under speech; no lead melody under a voice line.")
w("- Full brief with section-by-section instrumentation, picture anchors and sync points: `navislabs_v5_music_production_brief.json`.")
w("")
w("## 6. SFX requirements")
w("")
w(f"- {len(cfg['SFX_EVENTS'])} events in 15 categories, every one tied to something visible (`navislabs_v5_sfx_map.json`, generated from the code that plays them).")
w("- Temp SFX are synthesized placeholders and already play in the cut. **Final SFX are optional**: for a release-quality mix, drop recorded or licensed sounds with the same names into `public/sfx/final/` (48 kHz WAV, mono, short, clean tails).")
w("")
w("| Final file | Used for | Uses | Present |")
w("|---|---|---|---|")
for f in sfx_map["final_files"]:
    name = f["file"].split("/")[-1]
    w(f"| `{f['file']}` | {' · '.join(f['categories'])} | {f['used']} | {'✓' if sfx_final[name[:-4]] else '—'} |")
w("")
w("- Deliberate silences (no SFX): " + "; ".join(f"{s['from_s']}–{s['to_s']} s {s['why']}" for s in sfx_map["silences"]) + ".")
w("")
w("## 7. Final mix requirements")
w("")
w("- Integrated loudness −14 LUFS (±1) for web and social; true peak ≤ −1.0 dBTP; no clipped samples.")
w("- Voice on top: music ducks −9 dB under each line (automatic); SFX at least 12 dB below speech; music bed −7 dB.")
w("- 48 kHz stereo; AAC 320 kb/s in the MP4 (render script); voice centred.")
w("- Silence where planned: 10.0–10.45 s, 40.95–41.2 s, the refusal at −18 dB, 98.6–100 s.")
if render:
    w(f"- Current temp mix (picture-lock render): {render['audio']['integrated_lufs']} LUFS, true peak {render['audio']['true_peak_dbtp']} dBTP, {render['audio']['clipped_samples']} clipped samples. The final mix is checked the same way (`npm run check:render`).")
w("")
w("## 8. What you need to record")
w("")
w("- **If you clone your voice (recommended for consistency):** for a Professional Voice Clone, at least 30 minutes of your own clean speech (2–3 hours is best). Use one quiet, dead room, one microphone 15–20 cm away, consistent level, no music or other voices, and no long silences. Read in the film's register: calm, explanatory, unhurried. An Instant Voice Clone needs 1–2 minutes but is less faithful.")
w("- **Or record the 26 lines yourself:** read each line to picture against `out/navislabs-v5-picture-lock-1080p.mp4`, 3 takes per line, 48 kHz / 24-bit WAV, same room and microphone throughout, about 1 s of room tone before each take.")
w("- Confirm the pronunciation of 'Navis' / 'NavisLabs' and say it the same way everywhere.")
w("- Nothing else to record. Music and SFX are produced separately.")
w("")
w("## 9. What you need to generate")
w("")
w("- **ElevenLabs:** V01–V26 in your own voice (clone made with your permission). Use the passages above with the settings in section 4, audition 3 takes per passage, and export WAV at 48 kHz (or MP3 at 192 kb/s or higher).")
w("- **Music:** the 100-second score from `navislabs_v5_music_production_brief.json`, composed or generated, delivered as one WAV (stems optional).")
w("- **SFX (optional):** final versions of the 17 sounds in section 6. The temp set works for review.")
w("")
w("## 10. What Claude will automatically assemble")
w("")
w("Already automatic in the project:")
w("")
w("- Each slot plays its final file if present, else temp, else silence. Delivering a file is a file drop, not a code change.")
w("- Every voice line is placed at its start time and cut at its hard end. Music ducks −9 dB around every line with 0.15 s attack and 0.5 s release, and dips at the planned silences.")
w("- The temp data-flow texture mutes itself once the final score is present.")
w("- `mode: \"final\"` refuses to render until all 26 lines and the score are final.")
w("- `npm run validate:film` checks final takes against their hard ends and the 48 kHz sample rate, plus the SFX categories and silences.")
w("")
w("When you deliver files, Claude will:")
w("")
w("1. QC every take: format, length against the hard end, leading and trailing silence, peaks, clipping, noise.")
w("2. Convert to 48 kHz / 24-bit mono WAV and trim heads and tails to ≤ 50 ms, keeping the breath on 'after a short breath' lines.")
w("3. Split passage takes into V01–V26 at their pauses.")
w("4. Set each line's measured speech end, so the ducking follows your real voice.")
w(f"5. Align the phrase-sync lines ({', '.join(plan['summary']['phrase_sync_lines'])}) to their picture beats if a take drifts by more than its tolerance.")
w("6. Check the score's length, silences and loudness.")
w("7. Rerun every validator.")
w("8. Render the 1080p final, measure loudness, peaks and clipping, then render the 4K master after your approval.")
w("")
w("## 11. Is the project ready for final render?")
w("")
if ready_final:
    w("**Yes.** All 26 final voice files and the final score are present and valid.")
else:
    missing = [k for k, ok in vo_ok.items() if not ok]
    w(f"**No — not yet.** The picture is ready (READY_FOR_PICTURE_LOCK = true, READY_FOR_VOICEOVER = true). The final render is waiting on {len(missing)} of 26 voice files" + (" and the score." if not score else "."))
    w("")
    w("It becomes ready when V01–V26 and `public/music/final/v4/score.wav` are delivered and pass the checks above. The 4K master is rendered only after that, and after your approval.")
w("")
w("_Note: the SFX were tidied to the 15 categories and the temp score was regenerated to the approved arc after the picture-lock render. The next render includes both; the picture does not change._")
w("")
w("Sources: [What is Eleven v4?](https://elevenlabs.io/docs/help-center/product/core-capabilities/text-to-speech/what-is-eleven-v4) · [ElevenLabs prompting guide](https://elevenlabs.io/docs/best-practices/prompting) · [Professional Voice Cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning) · [Instant Voice Cloning](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/instant-voice-cloning)")
with open(os.path.join(ROOT, "navislabs_v5_audio_readiness_report.md"), "w") as f:
    f.write("\n".join(R) + "\n")

print(f"lines {len(lines)} · tight {tight} · sfx events {len(cfg['SFX_EVENTS'])} · music sections {len(sections)} · ready_for_final_render {ready_final}")
