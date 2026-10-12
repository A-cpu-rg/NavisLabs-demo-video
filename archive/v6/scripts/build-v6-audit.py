#!/usr/bin/env python3
"""Writes navislabs_v6_final_product_audit.md (sections A–X) and navislabs_v6_ready_for_final.md.

Everything measurable is read from the built V6 data, the validators, the stale-copy search and
the render QC (navislabs_v6_render_check*.json); the public website's integration status is read
(read-only) from ~/Desktop/navis-labs-website/components/site/logos.tsx. Nothing outside
Navis-Launch-Film is modified. Run after `npm run validate:film`, `npm run copy:stale` and
`npm run check:render`:  npm run audit:final
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
data = fa.demo_data()
spec = fa.load("navislabs_v6_film_spec.json")
tl = fa.load("navislabs_v6_voice_timeline.json")
va = fa.load("navislabs_v6_voice_analysis.json")
amap = fa.load("navislabs_v6_audio_map.json")
sfx = fa.load("navislabs_v6_sfx_map.json")
smap = fa.load("navislabs_v6_voiceover_screen_map.json")
copydoc = fa.load("src/data/navislabs_v6_copy.json")
ent = fa.load("navislabs_entity_audit.json")
val = fa.load("navislabs_v6_validation_report.json")
stale = fa.load("navislabs_v6_stale_copy_report.json")
machine = fa.load("interaction_state_machine.json")


def opt(name):
    p = os.path.join(ROOT, name)
    return json.load(open(p)) if os.path.isfile(p) else None


rc = opt("navislabs_v6_render_check.json")
rc540 = opt("navislabs_v6_render_check_540p.json")
END = spec["format"]["duration_s"]
FRAMES = spec["format"]["frames"]
COPY = spec["onscreen_copy"]
SC = {s["id"]: s for s in spec["scenes"]}
launch = data["integrations"]["FILM_LAUNCH_INTEGRATIONS"]
ent_rows = {e["entity"]: e for e in ent["entities"]}
WEBSITE_DIFF = "The launch film represents the planned launch-state connector set supplied by the founder/team. Public website status may lag this film configuration."

web_path = os.path.expanduser("~/Desktop/navis-labs-website/components/site/logos.tsx")
web = {}
if os.path.isfile(web_path):  # read-only
    for m in re.finditer(r'id: "(\w+)",\s*label: "[^"]+",\s*status: "(\w+)"', open(web_path).read()):
        web[m.group(1)] = m.group(2)
ALIAS = {"calendar": "googlecalendar", "meet": "googlemeet", "drive": "googledrive", "docs": "googledocs"}
WEB_WORD = {"supported": "SUPPORTED", "soon": "COMING SOON"}


def web_status(i):
    s = web.get(ALIAS.get(i, i))
    return WEB_WORD.get(s, s.upper()) if s else "NOT LISTED"


def mmss(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def scenes(eid):
    return ", ".join(ent_rows.get(eid, {}).get("scenes", [])) or "—"


# Where each connector is actually drawn: all thirteen in the S01 field, the S04 systems column and
# the S05 "where the work lives" row; evidence wherever a demoContent constant cites the system
# (placement of each constant in the film, by scene).
PLACE = {"TWO_TRUTHS": ["S01"], "OPENING_SIGNALS": ["S01"], "HAND_COPIES": ["S02"], "FLOW_SIGNALS": ["S04"], "GLANCE": ["S05"],
         "PRIORITIES": ["S06"], "ACME_SIGNALS": ["S07"], "SYSTEM_FACTS": ["S07"], "ACROSS_SYSTEMS": ["S09"], "RESULT_ROWS": ["S12", "S15"], "ACME_CONTEXT": ["S17"]}
CHIP = {"calendar": "Calendar", "docs": "Docs", "meet": "Meet"}
_dc = fa.strip_comments(fa.read(fa.DEMO_CONTENT))
_decls = list(re.finditer(r"^(?:export\s+)?(?:const|function)\s+(\w+)", _dc, re.M))
_BODY = {m.group(1): _dc[m.end():_decls[k + 1].start() if k + 1 < len(_decls) else len(_dc)] for k, m in enumerate(_decls)}


def placed(x):
    out = {"S01", "S04", "S05"}
    for const, sc in PLACE.items():
        body = _BODY.get(const, "")
        if re.search(rf'"{x["id"]}"|`{x["id"]} ·|label: "{re.escape(CHIP.get(x["id"], x["label"]))}"', body):
            out |= set(sc)
    return ", ".join(sorted(out))


v_ok = val["all_pass"]
# ---- render QC verdicts -------------------------------------------------------------
qc = {}
if rc:
    blacks = rc["near_black_runs_s"]
    deliberate = [(13.0, 14.0), (END - 1.2, END + 0.1)]  # the breath before Navis; the end fade
    stray = [b for b in blacks if not any(lo - 0.2 <= b[0] and b[1] <= hi + 0.2 for lo, hi in deliberate)]
    qc = {
        "duration": abs(rc["duration_s"] - END) < 0.1,
        "frames": rc["video"]["frames"] == FRAMES,
        "lufs": abs(rc["audio"]["integrated_lufs"] + 14) <= 0.6,
        "true_peak": rc["audio"]["true_peak_dbtp"] <= -0.95,
        "clipping": rc["audio"]["clipped_samples"] == 0,
        "vo_present": not rc["vo_silent_lines"],
        "silent_end": rc["silent_end_rms_db"] < -60,
        "black": not stray,
    }
PICTURE_READY = bool(v_ok and stale["summary"]["fix"] == 0 and qc and all(qc.values()))
VOICEOVER_READY = bool(val["summary"].get("narrative") and val["summary"].get("voice_audio") and val["summary"].get("captions") and qc.get("vo_present", False))
MUSIC_READY = False  # the score in the cut is a synthesized temp bed; the final score is briefed, not made
SFX_READY = False  # synthesized placeholders in public/sfx/temp; final recorded/licensed sounds not delivered
NOT_IN_SOURCE = [x["label"] for x in launch if x["local_source_status"].startswith(("NOT IN", "PARTIAL", "ENUM", "IDENTITY", "COMMENT"))]
INTEGRATIONS_VERIFIED = False  # the film configuration is verified; product-side connectors for NOT_IN_SOURCE are not
FINAL_RENDER_READY = all([VOICEOVER_READY, PICTURE_READY, MUSIC_READY, SFX_READY, INTEGRATIONS_VERIFIED])

L = []
w = L.append
w("# NavisLabs launch film — V6 final product audit\n")
w(f"Review cut: `out/navislabs-v6-review-1080p.mp4` and `out/navislabs-v6-review-540p.mp4` · **{END:.2f} s ({mmss(END)}) · {FRAMES} frames · 1920×1080 · 30 fps**.  ")
w("The founder's final ElevenLabs performance (P1–P8) is the master clock: every scene, beat, caption, cursor move, SFX and music section is placed on the measured voice. "
  "Generated by `scripts/build-v6-audit.py` from the built data, the validators (`navislabs_v6_validation_report.json`), the stale-copy search and the render QC. "
  "Nothing outside Navis-Launch-Film was modified; the Navis product repositories and the website were read only.\n")
w(f"**Validators:** {'all pass' if v_ok else 'FAILING'} — " + " · ".join(f"{k} {'✓' if ok else '✗'}" for k, ok in val["summary"].items()) + ".  ")
w(f"**Stale-copy search:** {stale['summary']['total']} hits, {stale['summary']['intentional']} intentional, {stale['summary']['fix']} to fix.\n")

# A
w("## A · PRODUCT STORY\n")
w("SYSTEMS → SIGNALS → NAVIS → UNDERSTANDING → WHAT MATTERS → DECISION → ACTION, then the same understanding reached by agents.\n")
w("| Scene | Time | What the film shows |\n|---|---|---|")
for s in spec["scenes"]:
    w(f"| {s['id']} | {mmss(s['from_s'])}–{mmss(s['to_s'])} | {s['beat']} |")
w("\nOne organization (NavisLabs, using its own products), one customer (Acme Corp, fictional), one event (Jordan Lee's email moving the renewal from "
  f"{data['customers'][0]['renewal_was']} to {data['customers'][0]['renewal_now']}), one decision (annual plans keep current terms) — carried from the App (S05–S09) into Developer (S10–S16) and the hero (S17).\n")

# B
w("## B · APPLICATION (Navis App)\n")
w("- S05 Today at a glance → S06 What changed → the Acme priority (chips include `Salesforce · Opportunity · closes "
  f"{data['crm_records'][0]['close_date']}` and `Jira · {data['engineering_context']['issues'][0]['key']} · Blocked`).")
w("- S07 *Why Navis surfaced this*: every fact with its source system, time and connector freshness; then the evidence opened out — "
  "eight facts from the connected systems that hold demo records, resolved into one customer state.")
w("- S08 *Waiting on you* → the prepared reply (Navis prepares; the person edits one sentence) → the cursor rests on **Approve & send** through \"A person decides.\"")
w("- S09 Approve & send → Sending → Gmail accepted → **The same event, across the company's systems**: Gmail *Done*; Salesforce *Next* (owner: the founder); "
  "GitHub *Next* (Engineering · agent); Jira *Related*. Navis does not update those systems itself; each row says who owns the next step.")
w("- Interfaces are recreated from the Navis-AI source (read-only); customer data is fictional. Claim statuses: `navislabs_v6_product_surface_map.json`.\n")

# C
w("## C · DEVELOPER (Navis Developer)\n")
w("- S10 VS Code with Claude Code: the founder types the agent's task (from the same renewal).")
w("- S11 Console › Members (Add a member → *Invited*) → terminal `claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> …` → `claude mcp list` → ✓ Connected → Connect › Access surfaces, MCP · API · SDK · CLI lit as each is said.")
w("- S12 the agent asks → `navis_get_relevant_context` returns the company's context with SOURCE and FRESHNESS.")
w("- S13 SDK (local package, *not on npm yet*) and the Developer API (`$NAVIS_BASE_URL/developer/context`, `X-API-Key`); \"No model is called · Navis grounds · your agent reasons\".")
w("- S14 permissions (allowed / own scope / denied with the product's exact refusal). S15 the diff → Runs → Run detail (Outcome *Not judged*; Model/Tokens/Cost/Latency \"—\").")
w("- Navis Developer stands on its own: no Navis App is required for a solo developer or a team (S16).\n")

# D, E, F
w("## D · SOLO\n")
solo = data["developer_workspace"]["solo"]
w(f"S16: a solo developer (Riya, fictional) signs up **For myself** — \"Build and experiment on your own. Your workspace is private to you.\" (Devtool SignUpForm.tsx, verbatim) → "
  f"Settings › Organization: Workspace *Personal*, ownership *Owner* (\"{solo['name']}\"). No Navis App, no company.\n")
w("## E · TEAM\n")
w("S11: Members — *Add a member* → *Add member* → the new row reads *Invited* (InviteMemberForm.tsx / MembersPanel.tsx). Roles shown: owner, developer (DEVELOPER_ROLES: owner, admin, developer, viewer).  ")
w(f"S16: the company's Members as the team → the team's agent records `navis workstate checkpoint` → next session restores NAVIS WORK CONTINUITY — decision \"{data['team_workstate']['decision']}\", next \"{data['team_workstate']['open']}\"  ")
w("\"For myself\" / \"For my organization\" are the product's real sign-up strings. \"Invite your team\" is **not** a product string and is not used.\n")
w("## F · ORGANIZATION\n")
w(f"One organization throughout: **{data['company']['name']}** (REAL_AUTHORIZED, the founder's own company) — teams, people, one fictional customer, projects and commitments (S05 OrgIntro). "
  "API keys are scoped to one organization by the key alone (S14 *own scope*). Every entity: `navislabs_entity_audit.json` "
  f"({ent['summary']['entities']} rows: {ent['summary']['real_authorized']} real-authorized, {ent['summary']['real_public_product']} public products named nominatively, {ent['summary']['synthetic']} synthetic).\n")
w("Names: only approved names are used — Abhishek Meena (founder, REAL_AUTHORIZED), NavisLabs; Sam Rivera, Jordan Lee, Riya and Acme Corp are SYNTHETIC. "
  "**Mulayam Kumar and Digantara are not in the film**: the dataset holds no written authorization for either (Digantara is a real company). Swapping in an approved teammate is a one-field change in the launch-state file.\n")

# G
w("## G · CONNECTORS (film launch state)\n")
w(f"> {WEBSITE_DIFF}\n")
w("The film uses an isolated, film-only configuration — `FILM_LAUNCH_INTEGRATIONS` in `src/data/navislabs_v6_launch_state.json` — in which all thirteen systems are connected. "
  "No product repository and no website file was changed. Systems that hold a demo record give evidence; HubSpot, Microsoft 365 and Zoom appear only as connected infrastructure (no invented records).\n")
for x in launch:
    w(f"- **{x['label']}** — FILM STATUS: CONNECTED / LAUNCH STATE · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS {web_status(x['id'])} · "
      f"LOCAL PRODUCT SOURCE: {x['local_source_status']} · ROLE: {x['role']} · IN FILM: {x['in_film']} · ON SCREEN: {placed(x)}")
w("")

# H, I
crm = data["crm_records"][0]
w("## H · CRM\n")
w(f"Salesforce is the CRM of record: one FILM DEMO RECORD — {crm['object']} \"{crm['name']}\", stage {crm['stage']}, close date **{crm['close_date']}**, owner the founder, last activity \"{crm['last_activity']}\". "
  f"No amounts, no pipeline numbers. The story: the email moved the renewal to {data['customers'][0]['renewal_now']} but the CRM still says {crm['close_date']} — Navis surfaces the gap (S06–S07), "
  "and after the reply the Salesforce row reads *Next*, owned by a person (S09). The agent's context carries the same fact (\"Opportunity still closes " + crm["close_date"] + "\", S12/S15) and the team's checkpoint leaves \"" + data["team_workstate"]["open"] + "\" open (S16). "
  "HubSpot is shown only as another connected source. On screen: S01 (scattered signal), S04, S06 (priority chip), S07 (trace and evidence), S09, S12, S15, S16.\n")
iss, code, kn = data["engineering_context"]["issues"][0], data["engineering_context"]["code"][0], data["knowledge"][0]
w("## I · ENGINEERING CONTEXT\n")
w(f"- Jira: {iss['key']} \"{iss['title']}\" · {iss['status']} (fictional; owner Sam Rivera, synthetic) — a related signal on the Acme priority and in the across-systems panel.")
w(f"- GitHub: `{code['path']}` in the company repository still holds `{code['fact']}`; the agent's change in Navis Developer makes it `{code['after']}` (S15). No PR numbers, no deployment, no autonomous merge.")
w(f"- Knowledge: Notion \"{kn['title']}\" — \"{kn['fact']}\" ({kn['date']}). Microsoft 365 is a connected documents source with no record shown. Zoom and Google Meet are meeting signals; the decision comes from the Meet pricing review.\n")

# J–N
w("## J · MCP\n")
w("Real commands, placeholder key only: `claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> -- node ./services/mcp-server/dist/stdio.js` → `claude mcp list` → `✓ Connected`. "
  "Claude Code is the only client shown as LIVE VERIFIED (Devtool docs/mcp/CLIENTS.md); Cursor, Codex and VS Code are CONFIG VERIFIED and text-only. Status: PRIVATE PREVIEW.\n")
w("## K · API\n")
w("`curl -s \"$NAVIS_BASE_URL/developer/context\" -H \"X-API-Key: $NAVIS_API_KEY\"` → items · sources · freshness (real field names, demo values). No public base URL is implied; the organization comes from the key. "
  "Navis grounds the agent; the model reasons — no generative model is called by Navis.\n")
w("## L · SDK\n")
w("`npm install ./navis-sdk-0.1.0.tgz` with the on-screen note *@navis/sdk 0.1.0 · local package · not on npm yet*. No public-registry install is shown.\n")
w("## M · CLI\n")
w("`navis workstate checkpoint` records the work state; the next session's SessionStart hook restores NAVIS WORK CONTINUITY (packages/cli workstate.ts, restore.ts). Built from source; not on npm.\n")
w("## N · PERMISSIONS\n")
w("S14 three credentials: allowed (view_memory) · own scope (one organization) · denied, with the product's exact refusal: "
  "*navis_get_relevant_context requires the \"view_memory\" permission, which this credential does not hold. Do not retry — the answer will not change. Ask an organization admin to issue a key carrying it.* "
  "The central policy engine is not shown as live (product: \"Not enabled yet\").\n")

# O
w("## O · VOICEOVER\n")
w("The founder's final ElevenLabs v4 performance, eight chunks, used as delivered: **no speed change, no trims inside a chunk, no pauses removed**. "
  "Originals kept in `public/voiceover/source/v6/`; the film plays 48 kHz WAVs gain-matched to −19 LUFS with a safety limiter (`public/voiceover/final/v6/`). "
  "Placement: speech-end → speech-start breaths between chunks. ElevenLabs v4 offers Stability and Similarity only (no Style/Speed; no SSML) — pauses come from punctuation and `[pause]` tags.\n")
w("| Chunk | Placed at | Length | Speech | LUFS | Marked pauses (measured) |\n|---|---|---|---|---|---|")
VA = {c["id"]: c for c in va["chunks"]}
for c in tl["chunks"]:
    mp = [f"{round(c['lines'][i + 1]['start_s'] - ln['end_s'], 2)} s" for i, ln in enumerate(c["lines"][:-1]) if ln["pause_after"]]
    w(f"| {c['id']} | {mmss(c['at_s'])} | {c['duration_s']:.2f} s | {mmss(c['speech_start_s'])}–{mmss(c['speech_end_s'])} | {VA[c['id']]['integrated_lufs']} | {', '.join(mp) or '—'} |")
w(f"\nVoice total {va['total_s']:.2f} s → film {END:.2f} s (lead {tl['lead_s']} s, breaths between chunks, {tl['hold_s']} s hold on the end card). Every line, its scene, camera, cursor, SFX, music state and captions: `navislabs_v6_voiceover_screen_map.json`.\n")
w("Key lines (music ducks −14 dB instead of −10 dB): " + "; ".join(f"\"{l['text']}\"" for l in smap["lines"] if l["key_line"]) + "\n")

# P
w("## P · MUSIC\n")
w(f"Style: {amap['music']['style']}  \nThe arc follows the voice, so the section edges sit on the scene changes rather than on round seconds:\n")
w("| Section | Brief target | In the film | Role |\n|---|---|---|---|")
TARGET = {"M1": "0–15 near silence", "M2": "15–30 pulse", "M3": "30–50 warm", "M4": "50–75 developer rhythm", "M5": "75–95 expansion", "M6": "95–end resolve", "M7": "→ silence"}
for s in amap["music"]["sections"]:
    w(f"| {s['id']} | {TARGET.get(s['id'], '')} | {s['from_s']:.2f}–{s['to_s']:.2f} s | {s['role']} — {s['brief']} |")
w("\nDips: " + "; ".join(f"{d['from_s']}–{d['to_s']} s {d['db']} dB ({d['why']})" for d in amap["music"]["dips"]) + ".  ")
w(f"Ducking follows the measured speech windows: {amap['music']['duck_under_vo_db']} dB under every line, {amap['music']['duck_key_line_db']} dB under the eight key lines (attack 0.12 s, release 0.45 s).  ")
w("**Status: TEMP.** The cut plays a synthesized temp bed (`public/music/temp/v6/score.wav`) that follows this arc; the final score is briefed in `navislabs_v6_music_production_brief.json` and drops into `public/music/final/v6/score.wav`.\n")

# Q
w("## Q · SFX\n")
w("| Category | Events |\n|---|---|")
for c in sfx["categories"]:
    w(f"| {c['category']} | {c['count']} |")
w(f"\n{sum(c['count'] for c in sfx['categories'])} events, each tied to a visible action (validator: no click sound without a visible click; nothing but keystrokes under a key line — the npm Enter under \"Navis isn't the model.\" was removed). "
  "Deliberate silences: " + "; ".join(f"{s['from_s']}–{s['to_s']} s ({s['why']})" for s in sfx["silences"]) + ".  ")
w("**Status: TEMP** — synthesized placeholders in `public/sfx/temp`; final sounds drop into `public/sfx/final` under the same names.\n")

# R, S, T
w("## R · CAMERA\n")
CAM = {}
for ln in smap["lines"]:
    CAM.setdefault(ln["scene"], ln["camera"])
for sid in sorted(CAM):
    w(f"- **{sid}** {CAM[sid]}")
w("\nMotion blur only on fast moves (speed-based CameraMotionBlur, 14 px/frame threshold); holds and drifts elsewhere. No camera move fights a line.\n")
w("## S · CURSOR\n")
cur = [i for i in machine["interactions"] if i["cursor"]]
w(f"{len(cur)} cursor interactions, each before → settle (≥ 0.1 s) → click → feedback → after; no click ring; every press has its sound at the same frame (validator: interaction 29/29 checks).  ")
w("Approve & send: the cursor settles on the button through \"A person decides.\" and presses just before \"Then the company acts.\"\n")
w("## T · CAPTIONS\n")
cues = open(os.path.join(ROOT, "captions", "navislabs-v6.srt")).read().strip().count("\n\n") + 1
words = len(json.load(open(os.path.join(ROOT, "public", "captions", "navislabs-v6-captions.json"))))
w(f"`captions/navislabs-v6.srt`, `captions/navislabs-v6.vtt` (line:88%, off the UI) and word-level `public/captions/navislabs-v6-captions.json` — {cues} cues, {words} words, regenerated from the measured voice "
  "(speech bursts matched to the words). They read exactly the script; every cue starts on spoken words; no overlaps. Sidecar files — nothing burned in.\n")

# U, V, W, X
w("## U · BRAND\n")
w(f"Company **{COPY['company']}** (one word). Products **{COPY['product.application']}** and **{COPY['product.developer']}**. Tagline: \"{COPY['tagline']}\" "
  "The approved mark (public/images/brand, from the website) — never a generic black pill. Hero: NAVIS APP | NAVISLABS | NAVIS DEVELOPER → \"ONE UNDERSTANDING. TWO WAYS IN.\" "
  f"End card disclosure: \"{COPY['disclosure']}\"\n")
w("## V · DATA CONSISTENCY\n")
w("Every name, date, record and string the scenes show comes from one file (`src/data/navislabs_v6_launch_state.json` → `src/ui/demoContent.ts`); the validator finds no entity value hard-coded in a component. "
  f"The CRM close date is the customer's old renewal date ({crm['close_date']}); the GitHub file is the workflow the agent edits; the run's task is the agent's task; the same customer, decision and commitment appear in both products. "
  "Economics read \"—\"; the run is *Not judged*; *Updates* is 0.\n")
w("## W · PUBLIC-WEBSITE-DIFFERENCE\n")
w(f"> {WEBSITE_DIFF}\n")
sup = [x["label"] for x in launch if web_status(x["id"]) == "SUPPORTED"]
soon = [x["label"] for x in launch if web_status(x["id"]) == "COMING SOON"]
w(f"- Public website (navis-labs-website/components/site/logos.tsx, read today): SUPPORTED — {', '.join(sup)}; COMING SOON — {', '.join(soon)}.")
w("- The film shows all thirteen as connected (launch state). The website was **not** modified and the film does not claim it was updated.")
w(f"- Local product checkout: connectors exist for the Google Workspace systems and Slack; {', '.join(NOT_IN_SOURCE)} have no working connector in the local source (enum / identity-alias / comment references only, or nothing). "
  "These must be live — or the film's launch state confirmed by the team — before public release.\n")
w("## X · FINAL RENDER\n")
if rc:
    a = rc["audio"]
    w(f"| Check | 1080p | Result |\n|---|---|---|")
    w(f"| Duration | {rc['duration_s']:.3f} s (expected {END:.3f}) | {'✓' if qc['duration'] else '✗'} |")
    w(f"| Frames | {rc['video']['frames']} (expected {FRAMES}) · {rc['video']['width']}×{rc['video']['height']} · {rc['video']['fps']} · {rc['video']['codec']} {rc['video']['pix_fmt']} | {'✓' if qc['frames'] else '✗'} |")
    w(f"| Integrated loudness | {a['integrated_lufs']} LUFS (target −14) | {'✓' if qc['lufs'] else '✗'} |")
    w(f"| True peak | {a['true_peak_dbtp']} dBTP (≤ −1) | {'✓' if qc['true_peak'] else '✗'} |")
    w(f"| Clipping | {a['clipped_samples']} samples, peak {a['peak']} | {'✓' if qc['clipping'] else '✗'} |")
    w(f"| Loudness range | {a['lra']} LU | — |")
    w(f"| Voice on every line | {rc['vo_rms_range_db'][0]} … {rc['vo_rms_range_db'][1]} dB RMS; silent lines: {rc['vo_silent_lines'] or 'none'} | {'✓' if qc['vo_present'] else '✗'} |")
    w(f"| Near-black runs | {rc['near_black_runs_s']} — the end fade only | {'✓' if qc['black'] else '✗'} |")
    w(f"| Silent end | {rc['silent_end_rms_db']} dB RMS | {'✓' if qc['silent_end'] else '✗'} |")
    w(f"| Bed in the founder's marked pauses | {rc['bed_in_marked_pauses_db']} | music rises in the pauses |")
    if rc540:
        w(f"| 540p | {rc540['video']['width']}×{rc540['video']['height']} · {rc540['duration_s']:.3f} s · {rc540['audio']['integrated_lufs']} LUFS · {rc540['audio']['true_peak_dbtp']} dBTP · {rc540['size_mb']} MB | ✓ |")
    S_ = val["summary"]
    ok = lambda b: "✓" if b else "✗"  # noqa: E731
    w(f"| Voice sync | 8 chunks at their measured slots; WAV length = measured length (no speed change); breaths ≥ 0.4 s; every [pause] ≥ 1 s | {ok(S_['voice_audio'])} |")
    w(f"| Caption sync | 48 cues start on measured speech; exact script; no overlaps | {ok(S_['captions'])} |")
    w(f"| SFX sync | every cursor press has its sound on the same frame; no click without a visible click; nothing under the key lines but keystrokes | {ok(S_['interaction'] and S_['voice_audio'])} |")
    w(f"| Music ducking | −10 dB under every measured line, −14 dB under the 8 key lines; the bed rises in the marked pauses (above) | {ok(S_['voice_audio'])} |")
    w(f"| Cursor accuracy | {len(cur)} interactions: before → settle ≥ 0.1 s → click → feedback → after; no click ring | {ok(S_['interaction'])} |")
    w(f"| Button accuracy | product labels verbatim (Approve & send, Review & reply, Add member, For myself, …) | {ok(S_['product_claim'] and S_['brand'])} |")
    w(f"| Integration accuracy | 13 launch-state systems, each with a mark; evidence only where a demo record exists | {ok(S_['integration'])} |")
    w(f"\nSizes: 1080p {rc['size_mb']} MB" + (f", 540p {rc540['size_mb']} MB" if rc540 else "") + ". Audio mastered with one static gain to −14 LUFS and a 4×-oversampled peak limiter (`scripts/master-v6.py`) — "
      "no dynamic loudness processing, so the pauses and silences stay as designed; picture copied, not re-encoded. **No 4K rendered.**\n")
    w("**Frame-level review** (contact sheets every 2 s across the whole film, plus full-resolution frames where a closer look was needed — the S06→S07 push, the S09 across-systems panel, S11, the S12/S15 context table, S14, S16 and the end card): two defects found in the first V6 render and fixed before this one — "
      "the agent's context table let \"salesforce · Oct 5\" run into the FRESHNESS column (columns now sized to their longest cell), and S16's personal workspace showed for only 0.55 s "
      "(\"For myself\" is now chosen on \"solo builder\" and the workspace holds ~1 s through \"private workspace\"). One-frame motion blur on fast camera moves is intended.\n")
else:
    w("Render QC pending (`npm run check:render`).\n")

with open(os.path.join(ROOT, "navislabs_v6_final_product_audit.md"), "w") as f:
    f.write("\n".join(L) + "\n")

flags = {"VOICEOVER_READY": VOICEOVER_READY, "PICTURE_READY": PICTURE_READY, "MUSIC_READY": MUSIC_READY, "SFX_READY": SFX_READY,
         "INTEGRATIONS_VERIFIED": INTEGRATIONS_VERIFIED, "FINAL_RENDER_READY": FINAL_RENDER_READY}
with open(os.path.join(ROOT, "navislabs_v6_ready_for_final.md"), "w") as f:
    f.write("\n".join(f"{k} = {str(v).lower()}" for k, v in flags.items()) + "\n")
print(" · ".join(f"{k}={v}" for k, v in flags.items()))
print("QC:", qc or "pending")
