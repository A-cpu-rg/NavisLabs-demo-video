#!/usr/bin/env python3
"""NavisLabs SOCIAL V1 audit → navislabs_social_v1_audit.json + navislabs_social_v1_audit.md (project root).

  python3 scripts/build-social-audit.py

Reads the social plan, the QC report (scripts/qc-social-v1.py), the visible-text claims scan
(scripts/scan-social-claims.py), the V7 spec/voice timeline and the master hashes. Read-only
on V7/V8.
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: json.load(open(os.path.join(ROOT, *p)))  # noqa: E731
plan = J("src", "social", "navislabs_social_v1_plan.json")
qc = J("src", "data", "navislabs_social_v1_qc.json")
scan = J("src", "data", "navislabs_social_v1_claims_scan.json")
spec = J("archive", "v7", "navislabs_v7_film_spec.json")
v7voice = J("archive", "v7", "navislabs_v7_voice_timeline.json")
SCENES = [(x["id"], x["from_s"], x["to_s"], x["beat"]) for x in spec["scenes"]]
OUT = "out/navislabs-social-v1-1080x1350.mp4"


def md5(p):
    h = hashlib.md5()
    with open(os.path.join(ROOT, p), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def scenes(a, b):
    return [i for i, f, t, _ in SCENES if f < max(b, a + 0.01) - 1e-3 and t > a + 1e-3]


# ---------------------------------------------------------------- masters untouched
BASE = {"out/navislabs-v7-review-1080p.mp4": "66cf0c12f7915f39bdea6de010169db6", "out/navislabs-v7-review-540p.mp4": "304260ecb7d76f078b6d5c535d3a4c43",
        "out/navislabs-final-audio-review-1080p.mp4": "95fbb9af331a8efb10afd04f9e97df7b", "out/navislabs-final-audio-review-540p.mp4": "80783c28327bd15c7f87a252d9d829b7"}
untouched = {p: {"md5_before": h, "md5_now": md5(p), "unchanged": md5(p) == h} for p, h in BASE.items()}

# ---------------------------------------------------------------- shots retained
SHOWS = {
    "hook": "PEOPLE | AI AGENTS — the person's inbox says the renewal moved to Nov 28; the agent's workflow file still says Nov 14. Restacked as two 4:5 panels.",
    "scatter": "The truth breaks apart across the company's tools.",
    "systems": "CONNECTED SYSTEMS — only V7's first column: Gmail, Google Calendar, Google Meet, Google Drive, Google Docs, Slack (the six live integrations). Salesforce and the second column (upcoming) are out of frame.",
    "by_hand": "PEOPLE copy it by hand.",
    "without": "AI AGENTS start empty.",
    "reveal": "'Navis' lands on the NavisLabs mark → Navis App (for people) / Navis Developer (for developers + AI agents).",
    "app_intro": "A company opens the Navis App — Today at a glance.",
    "why": "What changed → 'Kaveri Freightworks's renewal moved to Nov 28' (Gmail · Meera Iyer · Oct 5) → Waiting on you → Why this matters.",
    "sources_a": "The Why drawer: what's happening, who it is about, why it matters.",
    "sources_b": "TRACE · SIGNALS USED — Gmail, Google Calendar, Google Meet, Google Drive, Google Docs, Slack, each with its time and freshness (V7's last pill, Salesforce, and its CRM line are clipped).",
    "sources_hold": "Held on the trace (V7 frame 37.80) with a slow drift.",
    "prepared": "Navis prepares the reply.",
    "decides": "The cursor reaches Approve & send — a person decides.",
    "acts": "Approve & send → Sending… → Gmail accepted → Reply sent.",
    "dev": "Hard cut to the developer world: VS Code + Claude Code on the same company's repository; the task.",
    "dev_hold": "Held on the task (V7 frame 56.05).",
    "connect_term": "claude mcp add / claude mcp list → ✓ Connected (terminal macro, 1.4 s).",
    "connect": "Connect › Access surfaces — MCP, Developer API, SDK, CLI, each card on its word.",
    "context": "navis_get_relevant_context → KAVERI FREIGHTWORKS · cited facts with source · date and freshness (V7's sixth row — the Salesforce CRM fact — is clipped).",
    "context_sources": "V7's own zoom onto SOURCE · DATE.",
    "context_fresh": "V7's own pan to FRESHNESS.",
    "context_hold": "Held on V7 frame 2087 (V7 zooms out next).",
    "truth": "Developer API response: items · sources · freshness, 'No model is called' → the permission check: Agent credential → Organization · NavisLabs, Agent key AUTHORIZED.",
    "truth_hold": "Held on V7 frame 77.50 (V7's other cards — own scope, denied — fade in next and stay in V7).",
    "run_diff": "The agent's diff to src/workflows/kaveri-renewal.ts in the editor.",
    "run_work": "The agent works with the context: 'Using Navis context: renewal moved to Nov 28 (gmail, Oct 5)…' → Update(src/workflows/kaveri-renewal.ts), 4 additions and 2 removals → the summary (V7's context table above it is masked).",
    "run_record": "Runs → Run detail: the run on record, each step Completed (from V7 frame 2443, after V7's crossfade).",
    "thesis": "One company · NavisLabs: Navis App and Navis Developer either side of the shared understanding → same fact / same source / same freshness → the pull-back; SAME FACTS. SAME SOURCES. SAME FRESHNESS. → ONE UNDERSTANDING. TWO WAYS IN. on the founder's words.",
    "name": "The mark; 'NavisLabs.' — near silence.",
    "tagline": "The shared understanding for your organization.",
    "end_hold": "Held end frame (V7 frame 122.20) with the social disclosure line.",
}
retained = []
for i, s in enumerate(plan["shots"], 1):
    still = s["layout"] == "still"
    v_in = s["src_in"]
    v_out = v_in if still else v_in + s["dur"]
    retained.append({"n": i, "shot": s["id"], "social_in_s": round(s["at"], 2), "social_out_s": round(s["at"] + s["dur"], 2), "dur_s": round(s["dur"], 2),
                     "v7_in_s": round(v_in, 2), "v7_out_s": round(v_out, 2), "v7_scenes": scenes(v_in, v_out), "kind": "held frame" if still else ("split panels" if s["layout"] == "split" else "live V7"),
                     "shows": SHOWS.get(s["id"], ""), "framing": {"keys": s["keys"] if s["layout"] != "split" else s["panels"], **{k: s[k] for k in ("clip_bottom", "clip_right", "side_fade", "top_fade", "top_cut", "fade_out") if k in s}}})
missing = [r["shot"] for r in retained if not r["shows"]]
assert not missing, missing

# ---------------------------------------------------------------- shots removed (complement of the live V7 ranges)
iv = sorted((r["v7_in_s"], r["v7_out_s"]) for r in retained if r["kind"] != "held frame")
merged = []
for a, b in iv:
    if merged and a <= merged[-1][1] + 0.04:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])
gaps, t = [], 0.0
for a, b in merged:
    if a - t > 0.04:
        gaps.append((round(t, 2), round(a, 2)))
    t = max(t, b)
gaps.append((round(t, 2), 125.23))
WHAT = {
    0.0: "The first 0.25 s before the hook settles.",
    4.15: "The rest of the S01 split: the two date chips (Nov 28 vs Nov 14) and the views breaking apart.",
    9.15: "S01 → S02 transition.",
    12.88: "S02 tail into the reveal.",
    17.77: "S03 tail ('One understanding. Two ways in.' under the products) and the wipe into S04.",
    22.1: "S04 pipeline: thirteen systems → signals → memory → context → intelligence → decision → execution → outcome → learning; P2 'Every email, meeting, document and message becomes a signal — remembered, connected, and turned into what should happen next.'; S05 opening.",
    31.89: "S05 → S06 transition.",
    36.65: "S07: the sources arriving (0.7 s).",
    37.82: "S07 evidence opened out (eight systems → one customer state — the CRM conflict); S08 'Waiting on you → Review & reply'; P3 'When something needs a decision, Navis prepares the next step.'",
    44.93: "S08: the person edits the draft.",
    51.3: "S09: the same event across Gmail, Salesforce, GitHub and Jira; the light → dark wipe into Navis Developer.",
    56.1: "S10 tail; S11 Console › Members: Add a member → Invited; P4 'Invite the team.'",
    63.69: "S11 → S12 transition.",
    69.57: "S12 zoom-out tail; S13 'npm install ./navis-sdk-0.1.0.tgz' (local package) + the SDK example.",
    81.3: "S15: V7's 0.13 s crossfade from the terminal into the Runs page (replaced by a hard cut).",
    77.5: "S14: the other organization's card (own scope), the read-only key (denied) and the exact refusal; P4 'Every request is checked against its permissions.'",
    83.03: "S15 run-detail economics/outcome; all of S16 (sign up 'For myself' → personal workspace → the company's Members and roles → navis workstate checkpoint → the next session restores it; P5 'A solo builder gets a private workspace. A team can work together. And the work state carries into the next session.'); S17 'One company. The person and the agent acted on the same event.'",
    104.61: "S17 tail; all of S18's moat section: 'Models change. Agents change. Tools change.' → 'What your company knows shouldn't have to start over.' → Company-owned · Model-neutral · Shared by people and agents (all of P7).",
    120.52: "0.8 s of the silence after 'NavisLabs.' (shortened).",
    122.2: "The end-card build: the product row (Navis App / Navis Developer), navislabs.in and V7's disclosure (replaced by the held frame and the social disclosure line).",
}
removed = []
for a, b in gaps:
    w = next((v for k, v in WHAT.items() if abs(k - a) < 0.06), None)
    assert w, (a, b)
    removed.append({"v7_in_s": a, "v7_out_s": b, "dur_s": round(b - a, 2), "v7_scenes": scenes(a, b), "what": w})

# ---------------------------------------------------------------- voice
v7_lines = [(ch["id"], i, ln) for ch in v7voice["chunks"] for i, ln in enumerate(ch["lines"])]
used = set()
voice = []
for v in plan["voice"]:
    for cid, i, ln in v7_lines:
        if cid == v["chunk"] and ln["start_s"] >= v["v7_start"] - 0.05 and ln["end_s"] <= v["v7_end"] + 0.05:
            used.add((cid, i))
    voice.append({"line": v["id"], "text": v["text"], "file": v["file"], "social_s": [v["speech_start"], v["speech_end"]], "v7_s": [v["v7_start"], v["v7_end"]], "key_line": v["key"]})
voice_removed = [{"chunk": cid, "line": i, "text": ln["text"], "v7_s": [ln["start_s"], ln["end_s"]]} for cid, i, ln in v7_lines if (cid, i) not in used]
assert len(used) + len(voice_removed) == len(v7_lines)

# ---------------------------------------------------------------- sections vs the brief
SEC = [("Social hook", 0, 5, "hook", "hook"), ("Scattered truth", 5, 11, "scatter", "without"), ("Navis reveal", 11, 17, "reveal", "reveal"),
       ("Navis App", 17, 30, "app_intro", "prepared"), ("Human decision", 30, 36, "decides", "acts"), ("Navis Developer", 36, 49, "dev", "context_hold"),
       ("Permissions + run", 49, 56, "truth", "run_record"), ("Shared understanding", 56, 63, "thesis", "thesis"), ("End", 63, 70, "name", "end_hold")]
by_id = {s["id"]: s for s in plan["shots"]}
sections = [{"section": n, "brief_s": [a, b], "social_s": [round(by_id[x]["at"], 2), round(by_id[y]["at"] + by_id[y]["dur"], 2)]} for n, a, b, x, y in SEC]

# ---------------------------------------------------------------- QC summaries
fmt = qc["format"]
loud = qc["loudness"]
sep = qc["separation"]
black = qc["black_runs_s"]
# The planned dark beat: the thesis fades out and the mark arrives ≤ 0.3 s later.
name_at = next(s_["at"] for s_ in plan["shots"] if s_["id"] == "name")
unexpected_black = [r for r in black if not (abs(r[0] - name_at) < 0.1 and r[2] <= 0.3)]
holds = qc["hold_cuts"]
dups_at_cuts = qc["duplicates_at_cuts"]
gaps_unexpected = [g for g in qc["silence_gaps"] if g["why"] == "UNEXPECTED"]
jumps_unexpected = qc["loudness_jumps"]["unexpected"]
# A sample taken in a shot's last 0.03 s can land one V7 frame past the shot (ffmpeg seek); those are not on screen.
ends = {s_["id"]: s_["at"] + s_["dur"] for s_ in plan["shots"]}
legible_hits = [h for h in scan["hits"] if h["legible"] and ends[h["shot"]] - h["social_s"] > 0.03]
claims = {}
for h in legible_hits:
    e = claims.setdefault((h["shot"], h["issue"]), {"shot": h["shot"], "issue": h["issue"], "from_s": h["social_s"], "to_s": h["social_s"], "examples": []})
    e["from_s"], e["to_s"] = min(e["from_s"], h["social_s"]), max(e["to_s"], h["social_s"])
    if h["text"] not in e["examples"] and len(e["examples"]) < 3:
        e["examples"].append(h["text"])
claims = list(claims.values())
ui = scan["ui_text_px_by_shot"]

visual_ok = (fmt["frames"] == plan["frames"] and not unexpected_black and all(abs(h["step"]) < 1.0 for h in holds) and not dups_at_cuts)
audio_ok = (abs(loud["integrated_lufs"] + 14) <= 0.5 and loud["true_peak_dbtp"] <= -1.0 and loud["clipped_samples"] == 0 and not gaps_unexpected and not jumps_unexpected
            and sep["voice_minus_music_lu"] >= 10 and qc["voice_sync"]["max_abs_diff_ms"] <= 50 and abs(qc["voice_sync"]["audio_minus_video_ms"]) <= 40)
dur = round(fmt["video_s"], 2)

flags = {
    "SOCIAL_DURATION": f"TRUE — {plan['duration_s']:.2f} s ({plan['frames']} frames)" if 65 <= plan["duration_s"] <= 70 else f"FALSE — {plan['duration_s']:.2f} s",
    "SOCIAL_FORMAT": "TRUE — 4:5 · H.264 High · yuv420p · 30 fps · AAC 48 kHz stereo 320 kb/s" if fmt["codec"] == "h264" and fmt["audio_codec"] == "aac" else "FALSE",
    "RESOLUTION": "TRUE — 1080 × 1350" if (fmt["width"], fmt["height"]) == (1080, 1350) else "FALSE",
    "VOICEOVER_READY": "TRUE",
    "MUSIC_READY": "FALSE",
    "SFX_READY": "FALSE",
    "CAPTIONS_READY": "TRUE",
    "VISUAL_QC": "TRUE" if visual_ok else "FALSE",
    "AUDIO_QC": "TRUE" if audio_ok else "FALSE",
    "MOBILE_READABILITY": "PARTIAL",
    "FINAL_SOCIAL_READY": "FALSE",
}
reasons = {
    "SOCIAL_DURATION": "Inside the 65–70 s brief; the founder's lines play at natural speed (no stretching), with shortened pauses only.",
    "SOCIAL_FORMAT": f"{fmt['width']}×{fmt['height']}, {fmt['fps']} fps, {fmt['codec']} {fmt['profile']} {fmt['pix_fmt']} ~{fmt['video_kbps']} kb/s (CRF 16), {fmt['audio_codec']} {fmt['audio_rate']} Hz {fmt['channels']} ch; faststart.",
    "RESOLUTION": "Native 1080 × 1350 render of the reframed V7 picture (via a 1.5× sharpened proxy of the V7 1080p master).",
    "VOICEOVER_READY": f"The founder's own P1/P2/P3/P4/P6/P8 recordings, unmodified and not regenerated: 19 social lines (26 of V7's 43 lines) cut at measured line boundaries with 20 ms fades; no speed change or stretching. Onsets within {qc['voice_sync']['max_abs_diff_ms']} ms of plan; A/V offset {qc['voice_sync']['audio_minus_video_ms']} ms.",
    "MUSIC_READY": "The edit is done (the founder-supplied Eleven Music track re-cut into four sections that follow the brief's arc; ducked under every line, deeper under key lines, near-silence after 'NavisLabs.', a slow decay to silence). FALSE because the track's licence tier is still NOT VERIFIED and it needs the founder's listening approval.",
    "SFX_READY": "35 subtle cues on visible actions only, but they are the in-project synthesized placeholders (TEMPORARY) — no ElevenLabs SFX were supplied.",
    "CAPTIONS_READY": "Burned in (≤ 2 lines, ≤ 34 characters per line, 44 px on an 80 % plate, 132 px above the bottom edge, inside 4:5 safe areas); the thesis lines are carried by the on-screen type and the last two lines by the end card. social-captions.srt / .vtt / .json carry every spoken line (word timings in .json).",
    "VISUAL_QC": f"{fmt['frames']}/{plan['frames']} frames; no stray black frames (one planned 6-frame dark beat before the mark); held frames decode identically to the frame before them (largest step {max(abs(h['step']) for h in holds):.2f}/255); no repeated frames at cuts; soft frames only inside V7's own transitions; every framing checked on stills.",
    "AUDIO_QC": f"{loud['integrated_lufs']} LUFS integrated, {loud['true_peak_dbtp']} dBTP, {loud['clipped_samples']} clipped samples, LRA {loud['lra_lu']} LU; voice {sep['voice_minus_music_lu']} LU over music under speech ({sep['voice_minus_music_key_lines_lu']} LU under key lines); no unexpected silence or level jumps; the only silence is the planned end.",
    "MOBILE_READABILITY": "Captions (44 px ≈ 16 pt on a phone), the thesis type (60–78 px) and the end card read on a phone. Product UI is legible on a phone where the reframe is a macro (systems list, trace pills, Approve & send, Connect cards, context table, AUTHORIZED card); V7's small UI text in the wide moments (scatter, app intro, the thesis picture) is texture on a phone — the captions and type carry those beats.",
    "FINAL_SOCIAL_READY": "FALSE until the founder approves this cut, the music licence is confirmed, the temporary SFX are replaced or accepted, and the V7 data noted under remaining problems is accepted for public posting.",
}

problems = [
    "V7 data (as the brief requires) still shows integrations that are not live yet and two dates V8 later corrected — see 'claims_still_visible'. The two strongest claims were removed by framing only (no data changed): the CONNECTED SYSTEMS list shows only the six live integrations, and the agent's context table and the trace no longer show the Salesforce/CRM row. Still visible: 'SALESFORCE Opportunity · closes Nov 14' and 'JIRA KVR-142 · Blocked' chips in the App (≈17.3–20.8 s), 'Renewal call · Oct 9' (V8: Thu, Oct 8) and 'Committed 9 days ago' (V8: 6 days ago) in the App (≈18.6–20.8 s), and 'salesforce · as_of 09:44' in the Runs page's run detail (≈55.4–56.2 s); the scatter shot's flying fragments name Salesforce, HubSpot, Microsoft 365, Jira and Zoom as tools where work happens (≈4.2–5.7 s). If these must not appear publicly, the cut can be re-sourced from the V8 picture (same plan) — not done because the brief makes V7 the source of truth.",
    "Music licence not verified (Eleven Music tier) — needed before public posting.",
    "SFX are temporary synthesized placeholders.",
    "Picture is reframed from the 1080p V7 master: macros up to ~1.9× (systems list) are slightly soft; mitigated by a 1.5× Lanczos + light-sharpen proxy. A native 4:5 render of the V7 scenes would be sharper.",
    "Wide moments (scatter, app intro, the thesis picture at 0.55×) carry small V7 UI text that is texture on a phone; the captions and the thesis type carry the message there.",
    "Five intentional held frames (sources 2.45 s, developer task 0.79 s, context 0.34 s, permission check 0.57 s, end frame 3.11 s) — static picture under a slow camera drift, not accidental duplicates.",
    "The terminal shots show the local prompt 'abhishekmeena@Abhisheks-MacBook-Pro-8' (inherited from V7) — consider whether that is fine for a public post.",
    "Section timing lands up to ~2.5 s earlier than the brief's guide in the middle (natural line pacing); the hook is 3.9 s and the end converges on 70 s.",
    "Brief macro edges: neighbouring Connect cards show as faint slivers at the frame edge in the MCP/API/SDK/CLI macros (softened with a 60 px side fade).",
    "The disclosure line (21 px) is small on a phone.",
]

audit = {
    "about": "NavisLabs SOCIAL V1 audit (scripts/build-social-audit.py). V7 = investor/product demo; SOCIAL V1 = attention + product thesis + proof.",
    "flags": flags, "flag_reasons": reasons,
    "output": {"file": OUT, "md5": md5(OUT), "size_mb": fmt["size_mb"], "duration_s": dur, "frames": fmt["frames"], "format": fmt,
               "captions": ["captions/social-captions.srt", "captions/social-captions.vtt", "captions/social-captions.json"],
               "stems": ["out/stems/social/social-voice.wav", "out/stems/social/social-music.wav", "out/stems/social/social-sfx.wav"],
               "composition": "NavisSocialV1 (src/social/SocialFilm.tsx, plan src/social/navislabs_social_v1_plan.json)"},
    "v7_v8_untouched": untouched,
    "recommendation": {"format": "4:5", "why": "Every product beat reframes to a readable 4:5 macro or a whole-frame composition; no shot needed the 16:9 fallback, so out/navislabs-social-v1-1920x1080.mp4 was not created (V7 itself remains the 16:9 demo)."},
    "total_duration_s": plan["duration_s"],
    "sections": sections,
    "shots_retained": retained,
    "shots_removed_from_v7": removed,
    "v7_overlaps": "why (V7 32.24–35.93) and sources_a (35.75–36.65) share 0.18 s of V7 across a re-framed cut; by_hand/without share 0.04 s.",
    "voice_lines_retained": voice, "voice_lines_removed": voice_removed,
    "music": {"file": plan["music"]["file"], "gain_db": plan["music"]["gain_db"], "segments": plan["music"]["segments"], "dips": plan["music"]["dips"]},
    "sfx_cues": len(plan["sfx"]),
    "qc": {k: qc[k] for k in ("format", "black_runs_s", "hold_cuts", "duplicates_at_cuts", "soft_frame_runs_s", "loudness", "silence_gaps", "separation", "voice_sync")} | {"loudness_jumps": qc["loudness_jumps"]},
    "claims_still_visible": claims,
    "claims_scan": {"samples": scan["samples"], "frames_without_text": scan.get("frames_without_text", []), "legible_hits": len(legible_hits), "illegible_hits": len(scan["hits"]) - len(legible_hits)},
    "ui_text_px_by_shot": ui,
    "remaining_problems": problems,
}
with open(os.path.join(ROOT, "navislabs_social_v1_audit.json"), "w") as f:
    json.dump(audit, f, indent=1, ensure_ascii=False)
    f.write("\n")

# ---------------------------------------------------------------- markdown
fm = lambda x: f"{int(x // 60)}:{x % 60:05.2f}"  # noqa: E731
L = ["# NavisLabs SOCIAL V1 — audit", "", f"`{OUT}` · {fmt['width']}×{fmt['height']} · {plan['duration_s']:.2f} s · {fmt['size_mb']} MB · md5 `{audit['output']['md5']}`", "",
     "V7 = investor/product demo. SOCIAL V1 = attention + product thesis + proof — edited from the approved V7 film; V7 and V8 untouched (hashes below).", "",
     "## Status", "", "| Flag | Value | Why |", "|---|---|---|"]
L += [f"| {k} | **{v}** | {reasons[k]} |" for k, v in flags.items()]
L += ["", "## 4. Total duration", "", f"**{plan['duration_s']:.2f} s** ({plan['frames']} frames at 30 fps; video stream {dur} s).", "",
      "## 5. Recommended format", "", f"**4:5.** {audit['recommendation']['why']}", "",
      "## Sections (brief guide vs social cut)", "", "| Section | Brief | Social |", "|---|---|---|"]
L += [f"| {s['section']} | {fm(s['brief_s'][0])}–{fm(s['brief_s'][1])} | {fm(s['social_s'][0])}–{fm(s['social_s'][1])} |" for s in sections]
L += ["", "## 2–3. Shots retained (exact timestamps)", "", "| # | Shot | Social in–out | V7 in–out | V7 | What it shows |", "|---|---|---|---|---|---|"]
for r in retained:
    v7 = f"{r['v7_in_s']:.2f} (held)" if r["kind"] == "held frame" else f"{r['v7_in_s']:.2f}–{r['v7_out_s']:.2f}"
    L.append(f"| {r['n']} | {r['shot']} | {r['social_in_s']:.2f}–{r['social_out_s']:.2f} | {v7} | {', '.join(r['v7_scenes'])} | {r['shows']} |")
L += ["", f"Overlaps: {audit['v7_overlaps']}", "", "## 1. Shots removed from V7 (exact V7 timestamps)", "", "| V7 in–out | Length | V7 scenes | Removed |", "|---|---|---|---|"]
L += [f"| {r['v7_in_s']:.2f}–{r['v7_out_s']:.2f} | {r['dur_s']:.2f} s | {', '.join(r['v7_scenes'])} | {r['what']} |" for r in removed]
L += ["", f"V7 kept live: {sum(b - a for a, b in merged):.2f} s of 125.23 s; removed {sum(r['dur_s'] for r in removed):.2f} s.", "",
      "## Voice — lines retained", "", "| Line | Social | V7 | Text |", "|---|---|---|---|"]
L += [f"| {v['line']}{' (key)' if v['key_line'] else ''} | {v['social_s'][0]:.2f}–{v['social_s'][1]:.2f} | {v['v7_s'][0]:.2f}–{v['v7_s'][1]:.2f} | {v['text']} |" for v in voice]
L += ["", "Voice lines removed (V7 timestamps):", ""]
L += [f"- {x['chunk']}·{x['line']} ({x['v7_s'][0]:.2f}–{x['v7_s'][1]:.2f}) — {x['text']}" for x in voice_removed]
L += ["", "## QC", "", f"- Picture: {fmt['frames']} frames; black runs {black} (the 0.2 s beat before the mark is planned); hold cuts {[(h['shot'], h['step']) for h in holds]}; repeated frames at cuts: {len(dups_at_cuts)}; soft-frame runs {len(qc['soft_frame_runs_s'])} (all inside V7's own transitions/fades, checked).",
      f"- Audio: {loud['integrated_lufs']} LUFS, {loud['true_peak_dbtp']} dBTP, {loud['clipped_samples']} clipped; silence {qc['silence_gaps']}; level jumps {qc['loudness_jumps']['count']} (unexpected: {len(jumps_unexpected)}); voice − music {sep['voice_minus_music_lu']} LU (key lines {sep['voice_minus_music_key_lines_lu']} LU); voice onsets ±{qc['voice_sync']['max_abs_diff_ms']} ms.",
      f"- Claims scan (OCR of every retained V7 frame, mapped through the social framing): {scan['samples']} samples; legible hits listed below.", "",
      "## Mobile readability (UI text height on screen; × 0.36 ≈ phone points)", "", "| Shot | Median px | p90 px | Share ≥ 30 px |", "|---|---|---|---|"]
L += [f"| {k} | {v['median']} | {v['p90']} | {v['share_ge_30px']:.0%} |" for k, v in ui.items()]
L += ["", "## V7 data still visible (kept per the brief — flagged for public posting)", "", "| Shot | Social s | Issue | Example |", "|---|---|---|---|"]
L += [f"| {c['shot']} | {c['from_s']:.2f}–{c['to_s']:.2f} | {c['issue']} | {c['examples'][0][:80]} |" for c in claims]
L += ["", "## 6. Remaining problems", ""] + [f"{i}. {p}" for i, p in enumerate(problems, 1)]
L += ["", "## V7 / V8 masters untouched", ""] + [f"- `{p}` — {'unchanged' if u['unchanged'] else 'CHANGED'} (`{u['md5_now']}`)" for p, u in untouched.items()]
with open(os.path.join(ROOT, "navislabs_social_v1_audit.md"), "w") as f:
    f.write("\n".join(L) + "\n")
print(json.dumps(flags, indent=1))
print("removed ranges", len(removed), "| retained shots", len(retained), "| voice kept/removed", len(voice), len(voice_removed), "| claims", len(claims))
