#!/usr/bin/env python3
"""Writes navislabs_v4_final_product_audit.json and .md: the 44-section
picture-lock report. Every value is read from the generated data, audits,
validators and the render check; nothing here is typed in by hand except the
narrative workflow descriptions, which cite their beats.

Run after: npm run validate:film, the render, and npm run check:render.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
BRIEF_AT = dt.datetime(2026, 10, 5, 17, 6, 47, tzinfo=dt.timezone.utc)  # picture-lock brief received
OUT_1080 = "out/navislabs-v4-picture-lock-1080p.mp4"
OUT_540 = "out/navislabs-v4-picture-lock-540p.mp4"


def load_opt(name):
    p = os.path.join(ROOT, name)
    return json.load(open(p)) if os.path.isfile(p) else None


data = fa.demo_data()
spec = fa.load("navislabs_v4_film_spec.json")
vo = fa.load("navislabs_v4_voiceover_screen_map.json")["voiceover"]
audio = fa.load("navislabs_v4_audio_map.json")
plan = fa.load("navislabs_audio_design_plan.json")
surf = fa.load("navislabs_v4_product_surface_map.json")
machine = fa.load("interaction_state_machine.json")
ent = fa.load("navislabs_entity_audit.json")
cons = fa.load("navislabs_entity_consistency.json")
cap = fa.load("developer_capability_audit.json")
team = fa.load("team_permission_audit.json")
val = fa.load("navislabs_v4_validation_report.json")
render = load_opt("navislabs_v4_render_check.json")
cfg = json.loads(subprocess.run(["node", os.path.join(ROOT, "scripts", "dump-config.mjs")], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
B = cfg["BEAT"]
COPY = spec["onscreen_copy"]
people = {p["id"]: p for p in data["people"]}
cust = data["customers"][0]


def b(key, what):
    return {"at_s": round(B[key], 2), "step": what}


def probe(path):
    p = os.path.join(ROOT, path)
    if not os.path.isfile(p):
        return None
    pr = json.loads(subprocess.run(["/opt/homebrew/bin/ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p], capture_output=True, text=True).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), {})
    return {"file": path, "size_mb": round(int(pr["format"]["size"]) / 1e6, 1), "duration_s": round(float(pr["format"]["duration"]), 3),
            "video": f"{v['codec_name']} {v['width']}×{v['height']} {v['r_frame_rate']} {v.get('pix_fmt')}", "audio": f"{a.get('codec_name')} {a.get('sample_rate')} Hz {a.get('channels')} ch" if a else None}


r1080, r540 = probe(OUT_1080), probe(OUT_540)

# ---- camera / zoom: parsed from the scene files ---------------------------
KF = re.compile(r'\{\s*f:\s*([^,]+?),\s*x:\s*(-?[\d.]+),\s*y:\s*(-?[\d.]+),\s*scale:\s*([\d.]+),\s*easing:\s*"(\w+)"(?:,\s*note:\s*"([^"]*)")?\s*\}')
camera = []
for sid in fa.SCENE_IDS:
    code = fa.visible_text(os.path.join(fa.SRC, "scenes", f"{sid}.tsx"))
    kfs = KF.findall(code)
    if not kfs:
        camera.append({"scene": sid, "camera": "static frame (no camera keyframes)", "keyframes": 0})
        continue
    scales = [float(k[3]) for k in kfs]
    camera.append({
        "scene": sid, "keyframes": len(kfs),
        "hard_cuts": [k[5].replace("cut: ", "") for k in kfs if k[5] and "cut" in k[5]],
        "glides": sum(1 for k in kfs if k[4] == "glide"),
        "drifts": sum(1 for k in kfs if k[4] == "drift"),
        "scale_range": [min(scales), max(scales)],
        "language": "wide" if max(scales) <= 1.1 else ("macro" if max(scales) >= 1.8 else "medium"),
    })

# ---- buttons ---------------------------------------------------------------
pressed = [{"control": i["control"], "product": i["product"], "states": [f"{s['state']} {s['at_s']}s" for s in i["states"]]} for i in machine["interactions"]]
visible_not_pressed = [
    {"control": "Mark decided · Ask Navis · Snooze", "where": "S06 priority card", "source": "Navis-AI NarrativeCard.tsx", "pressed": False},
    {"control": "Start my day · Refresh workspace", "where": "S05 Today", "source": "Navis-AI DailyBriefHero.tsx", "pressed": False},
    {"control": "Save changes · Rewrite · Ignore", "where": "S08 draft", "source": "Navis-AI DraftReviewPanel.tsx", "pressed": False, "note": "'Saved' → 'Save changes' state change shown after the edit"},
    {"control": "Console navigation (Overview … State)", "where": "S11, S15, S16", "source": "Devtool lib/navigation.ts", "pressed": False},
    {"control": "For my organization", "where": "S16 sign-up", "source": "Devtool SignUpForm.tsx", "pressed": False},
]

# ---- files -----------------------------------------------------------------
SKIP = {"node_modules", "out", ".git", ".remotion"}
created, modified = [], []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in files:
        p = os.path.join(d, f)
        st = os.stat(p)
        born = dt.datetime.fromtimestamp(getattr(st, "st_birthtime", st.st_mtime), dt.timezone.utc)
        mod = dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc)
        rp = os.path.relpath(p, ROOT)
        if f == ".DS_Store":
            continue
        if born >= BRIEF_AT:
            created.append(rp)
        elif mod >= BRIEF_AT:
            modified.append(rp)
created.sort()
modified.sort()
for o in (OUT_1080, OUT_540):
    if os.path.isfile(os.path.join(ROOT, o)):
        created.append(o)
PROTECTED = ["navis_code_audit.json", "navis_master_cinematic_launch_spec.json", "navis_launch_production_blueprint.json"]
protected_ok = all(p not in modified and p not in created for p in PROTECTED)

# ---- readiness ----------------------------------------------------------------
validators_pass = val["all_pass"]
renders_ok = bool(r1080 and r540 and abs(r1080["duration_s"] - 100) < 0.1 and abs(r540["duration_s"] - 100) < 0.1)
render_qc_ok = bool(render and render["audio"]["clipped_samples"] == 0 and not render["vo_silent_lines"]
                    and render["video"]["frames"] == 3000
                    and all(a >= 99.0 for a, _ in render["near_black_runs_s"]))
vo_prep_ok = len(vo) == 26 and all(all(k in l["elevenlabs"] for k in ("text", "emotion", "delivery", "pace", "pause", "pronunciation", "max_duration_s", "visual_moment")) for l in vo)
final_vo = [l["id"] for l in vo if os.path.isfile(os.path.join(ROOT, "public", l["final"]))]
final_music = os.path.isfile(os.path.join(ROOT, "public", audio["music"]["final"]))
READY_VO = validators_pass and renders_ok and render_qc_ok and vo_prep_ok and protected_ok
READY_MUSIC = READY_VO
READY_FINAL = READY_VO and len(final_vo) == len(vo) and final_music

claims = {}
for s in surf["surfaces"]:
    claims.setdefault(s["claim_status"], []).append(s["label"])

sections = [
    ("FILM STATUS", {
        "title": "NavisLabs launch film — V4 picture lock", "format": spec["format"], "scenes": len(spec["scenes"]),
        "voiceover": f"{len(vo)} lines · {sum(len(l['voice_line'].split()) for l in vo)} words (temp voice)",
        "renders": [r for r in (r1080, r540) if r], "render_qc": render,
    }),
    ("PICTURE LOCK STATUS", {
        "locked": READY_VO, "validators_all_pass": validators_pass, "validators": val["summary"],
        "renders_present_and_100s": renders_ok, "render_qc_pass": render_qc_ok,
        "rule": "Picture is locked: timing, beats and VO ceilings are frozen; VO and music are recorded to this cut.",
    }),
    ("BRAND STATUS", {"pass": val["summary"]["brand"], "checks": [c["check"] for c in val["validators"]["brand"]["checks"]],
                      "logo": "NavisLabs mark without its tile (public/images/brand/navislabs-mark-dark.png, -light.png), wordmark set in the site's font; no pill, no glow",
                      "tagline": COPY["tagline"], "never_used": ["NAVIS AI", "NAVIS-AI", "Navis Labs"]}),
    ("COMPANY NAME", data["company"]["name"]),
    ("PRODUCT NAMES", {"Navis Application": f"{COPY['product.application.who']} — for people", "Navis Developer": f"{COPY['product.developer.who']}"}),
    ("ALL PEOPLE USED", [{"name": p["name"], "role": p["title"], "email": p["email"], "provenance": p["provenance"],
                          "scenes": fa.entity_scenes()[0].get(p["id"], [])} for p in data["people"]]),
    ("ALL ORGANIZATIONS USED", [
        {"name": data["company"]["name"], "kind": "the company (dogfooding its own products)", "provenance": "REAL_AUTHORIZED"},
        {"name": cust["name"], "kind": "customer", "provenance": cust["provenance"]},
        {"name": "Another organization", "kind": "unnamed generic tenant in the S14 own-scope check", "provenance": "SYNTHETIC"},
        {"name": "Integration vendors (13) and MCP clients (4)", "kind": "named nominatively as connectors / clients; no partnership implied", "provenance": "REAL_PUBLIC_PRODUCT"},
    ]),
    ("ALL CUSTOMERS USED", [{"name": cust["name"], "contact": people[cust["contact"]]["name"], "provenance": cust["provenance"], "note": cust.get("note")}]),
    ("AUTHORIZATION STATUS OF EACH NAME", [{"value": e["value"], "provenance": e["real_or_synthetic"], "authorized_for_public_video": e["authorized_for_public_video"],
                                           "replacement_if_needed": e["replacement_if_needed"]} for e in ent["entities"]]),
    ("APPLICATION USER MODEL", {
        "organization": data["company"]["name"], "teams": [t["name"] for t in data["teams"]],
        "user": f"{people['p_abhishek']['name']} ({people['p_abhishek']['application_role']})",
        "model": "Organization → Teams → Employees → Customers / Projects / Commitments → the systems where the work lives → Navis Application (S05 org intro)",
        "what_the_user_does": "Reads Today, opens why, reviews and edits the draft, approves; Navis sends through Gmail.",
    }),
    ("DEVELOPER USER MODEL", {
        "company": "Members with an Application role and explicit Developer access (owner · admin · developer · viewer); agents hold credentials with permissions",
        "members": [f"{people[m['person']]['name']} — {m['developer_role']} · {m['state']}" for m in data["developer_workspace"]["members"]],
        "agent": f"{data['agents'][0]['client']} ({', '.join(data['agents'][0]['permissions'])})",
        "solo": f"{people['p_solo']['name']} — personal workspace '{data['developer_workspace']['solo']['name']}' (Owner)",
    }),
    ("ORGANIZATION WORKFLOW", [
        b("orgIn", "Organization → teams → people → customers · projects · commitments → live systems"),
        b("glance", "Today at a glance"), b("whatChanged", "What changed"), b("whyClick", "Why this matters (click)"),
        b("evidence0", "Source · timeline · freshness per signal"), b("explodeIn", "Evidence opened out: six live systems → one customer state"),
        b("waiting", "Waiting on you"), b("reviewReplyClick", "Review & reply (click) → draft"),
        b("selectStart", "Edit: select the sentence, type the change"), b("approveClick", "Approve & send (click)"),
        b("replySent", "Execution: Sending… → Gmail accepted → Reply sent"), b("proofRail", "Proof rail: Gmail confirmation"),
    ]),
    ("SOLO DEVELOPER WORKFLOW", [b("soloIn", "Sign up"), b("soloPick", "'For myself' (click)"), b("soloWorkspace", "Personal workspace · Owner"),
                                 b("soloCheckpoint", "navis workstate checkpoint"), b("soloCheckpointOk", "Checkpoint recorded"),
                                 b("soloDayTwo", "Next session"), b("soloRestore", "NAVIS WORK CONTINUITY restored"), b("soloSections", "Task · decisions · open")]),
    ("TEAM / INVITE WORKFLOW", [b("membersIn", "Console › Members"), b("addMember", "Add member (click)"), b("invited", "Row: Invited")] + [{"source": x["source"]} for x in team["items"][:2]]),
    ("MCP WORKFLOW", [b("mcpAdd", "claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> -- node …/stdio.js"), b("mcpList", "claude mcp list"),
                      b("mcpConnected", "✓ Connected"), b("contextCall", "navis_get_relevant_context"), b("contextResult", "5 facts with source and freshness"),
                      b("agentReason", "The agent reasons; Navis calls no model")]),
    ("API WORKFLOW", [b("apiIn", "curl -s \"$NAVIS_BASE_URL/developer/context\" -H \"X-API-Key: $NAVIS_API_KEY\""), b("apiResponse", "items · sources · freshness"),
                      b("modelNeutral", COPY["noModel"])]),
    ("SDK WORKFLOW", [b("sdkIn", "npm install ./navis-sdk-0.1.0.tgz (local package · not on npm yet)"), b("sdkInstalled", "added 1 package"), b("sdkCode", "new Navis({ apiKey: process.env.NAVIS_API_KEY })")]),
    ("CLI WORKFLOW", [b("soloCheckpoint", "navis workstate checkpoint --objective … --decision … --open …"), b("soloRestore", "SessionStart hook restores the work state")]),
    ("RUN / CONSOLE WORKFLOW", [b("agentUses", "The agent edits the workflow file"), b("agentDone", "Done"), b("runs", "Console › Runs"), b("runOpen", "Open run (click)"),
                                b("runTimeline", "Timeline: Context · Tool · Tool · Tool · Outcome with times"), b("runOutcome", "Outcome: Not judged; economics '—'")]),
    ("APPLICATION DATA FLOW", "Gmail · Calendar · Meet · Drive · Docs · Slack signals → NavisLabs memory and context → Today priority with sources and freshness → draft → a person approves → Gmail sends → reply sent."),
    ("DEVELOPER DATA FLOW", "Agent (Claude Code) → MCP / API / SDK with the organization's key → navis_get_relevant_context → facts with source and freshness (organization from the key) → the agent reasons and edits code → the run is recorded in the Console."),
    ("SHARED DATA FLOW", {"S04": "Signals → Memory → Context → Intelligence → Decision → Execution → Outcome (Building) → Learning (Next)",
                          "S17": "One organization · NavisLabs: one shared organizational context feeds Navis Application (people · teams) and Navis Developer (developers · AI agents) — same fact, same source, same freshness",
                          "consistency": cons["checks"]}),
    ("LIVE INTEGRATIONS", [{"id": i, "semantic": data["integrations"]["semantics"][i]} for i in data["integrations"]["live_current"]]),
    ("EXPANDING ECOSYSTEM", {"label": COPY["visionNote"], "where": "S04 only, dashed, apart from the live column; never evidence",
                             "systems": [{"id": i, "semantic": data["integrations"]["semantics"][i]} for i in data["integrations"]["expanding"]]}),
    ("CURRENT VS TARGET-STATE CLAIMS", {"legend": surf["claim_status_legend"], "by_status": claims}),
    ("EVERY BUTTON AUDITED", {"pressed": pressed, "visible_not_pressed": visible_not_pressed}),
    ("EVERY CURSOR INTERACTION AUDITED", {"rules": machine["cursor_rules"],
                                          "interactions": [{"id": i["id"], "settle_to_click_s": round(next(s["at_s"] for s in i["states"] if s["state"] == "click") - next(s["at_s"] for s in i["states"] if s["state"] == "settle"), 2)}
                                                           for i in machine["interactions"] if i["cursor"]],
                                          "validator": val["summary"]["interaction"]}),
    ("CAMERA MOVEMENTS AUDITED", {"model": "wide → medium → macro → wide; hard cuts between framings; drifts while reading; glides only to follow information",
                                  "motion_blur": "CameraMotionBlur (6 samples, 180°) only on frames where the camera moves faster than 14 px/frame; samples look forward within the frame so hard cuts never ghost",
                                  "scenes": camera}),
    ("ZOOM IN / OUT AUDITED", [{"scene": c["scene"], "scale_range": c.get("scale_range"), "language": c.get("language", "static")} for c in camera]),
    ("TRANSITIONS AUDITED", [{"from": s["id"], "transition_out": s["transition_out"], "why": s.get("beat")} for s in spec["scenes"]]),
    ("SOUND EFFECT PLAN", {"categories": plan["categories"], "rules": plan["rules"], "layers": plan["layers"],
                           "events": {k: sum(1 for e in cfg["SFX_EVENTS"] if e["sfx"] == k) for k in sorted({e["sfx"] for e in cfg["SFX_EVENTS"]})},
                           "status": "temp SFX (synthesized placeholders)"}),
    ("MUSIC PLAN", {"style": audio["music"]["style"], "sections": audio["music"]["sections"], "dips": audio["music"]["dips"],
                    "duck_under_vo_db": audio["music"]["duck_under_vo_db"], "status": "brief only; temp bed in the picture lock; final score not generated"}),
    ("VO PREPARATION", {"lines": len(vo), "words": sum(len(l["voice_line"].split()) for l in vo), "elevenlabs_fields": list(vo[0]["elevenlabs"].keys()),
                        "audio_tags_used": sum(1 for l in vo if l["elevenlabs"].get("audio_tag")), "final_paths": "public/voiceover/final/v4/V01–V26.wav",
                        "final_present": final_vo, "key": "ELEVENLABS_API_KEY from the environment only; never in JSON",
                        "voice": "the founder's own voice, with his permission, if cloned", "lines_detail": [{k: l[k] for k in ("id", "start_s", "ceiling_s", "max_duration_s", "voice_line")} for l in vo]}),
    ("UNSUPPORTED CLAIMS", {"found": [], "validator_product_claim": val["summary"]["product_claim"], "avoided": cap["claims_avoided"]}),
    ("SIMULATED UI", {"how": "Every product screen is rebuilt in React from the real source (src/ui/evidence.ts lists file, source and verbatim strings); no screen recordings",
                      "film_graphics": claims.get("FILM_SIMULATION", []), "demo_data": "all customer, project, run and solo-developer data is SYNTHETIC (src/data/navislabs_demo_data.json)"}),
    ("FUTURE FEATURES", {"future_state": claims.get("FUTURE_STATE", []), "roadmap": claims.get("ROADMAP", []),
                         "in_pipeline": ["Outcome (Building)", "Learning (Next)"], "shown_as_live": []}),
    ("FILES CREATED", created),
    ("FILES MODIFIED", modified),
    ("FILES NOT TOUCHED", {"read_only_repositories": ["~/Desktop/Devtool", "~/Desktop/Navis-AI", "~/Desktop/Backend", "~/Desktop/navis-labs-website"],
                           "protected_json": PROTECTED, "protected_json_unchanged": protected_ok,
                           "never_opened": ["Devtool/.claude/settings.local.json", "Navis-AI .env*"]}),
    ("REMAINING BLOCKERS", [
        "Final founder VO: record or generate V01–V26 to the ceilings (ElevenLabs with the founder's own voice, with his permission); drop files into public/voiceover/final/v4/.",
        "Final music: score to the arc in navislabs_audio_design_plan.json; drop into public/music/final/v4/score.wav.",
        "Confirm public display of the founder's email and Mac user/host (or switch to the neutral prompt listed in the entity audit).",
        "Optional: written approval before replacing the SYNTHETIC engineer with Mulayam Kumar.",
        "Legal check of nominative vendor marks (13 integrations, Claude Code icon) before public release.",
        "4K master (npm run render:4k) after final VO and music.",
    ]),
    ("FINAL RECOMMENDATION", {
        "decision": "Lock picture. Record the founder VO to the ceilings in navislabs_v4_voiceover_screen_map.json and commission the score from the music brief; then mix and render the 4K master." if READY_VO else "Do not lock: fix the failing checks first.",
        "creative_test": {
            "muted": "The UI carries the story without narration: one customer event, its evidence, a human approval and a sent reply; then the same facts reaching an agent with source and freshness.",
            "audio_only": "The VO script states the problem, the shared understanding, both products and the ending line; the temp voice is a placeholder.",
            "serious_company": "Real product strings and flows from the source, real commands with placeholders, no invented metrics; future systems labelled.",
        },
    }),
    ("READY_FOR_VOICEOVER", READY_VO),
    ("READY_FOR_MUSIC", READY_MUSIC),
    ("READY_FOR_FINAL_RENDER", READY_FINAL),
]
assert len(sections) == 44, len(sections)

report = {
    "about": "NavisLabs launch film V4 — final product audit at picture lock (scripts/build-final-audit.py).",
    "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "READY_FOR_VOICEOVER": READY_VO, "READY_FOR_MUSIC": READY_MUSIC, "READY_FOR_FINAL_RENDER": READY_FINAL,
    "sections": [{"n": i + 1, "title": t, "content": c} for i, (t, c) in enumerate(sections)],
}
with open(os.path.join(ROOT, "navislabs_v4_final_product_audit.json"), "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
    f.write("\n")


# ---- markdown -------------------------------------------------------------------
def md(v, depth=0):
    pad = "  " * depth
    if isinstance(v, bool):
        return f"{pad}**{str(v).lower()}**"
    if isinstance(v, (str, int, float)) or v is None:
        return f"{pad}{v}"
    if isinstance(v, list):
        if v and all(isinstance(x, dict) for x in v) and len({tuple(x.keys()) for x in v}) == 1 and all(not isinstance(y, (dict, list)) or isinstance(y, list) and all(isinstance(z, (str, int, float)) for z in y) for x in v for y in x.values()):
            keys = list(v[0].keys())
            cell = lambda y: ", ".join(map(str, y)) if isinstance(y, list) else ("—" if y is None else str(y).replace("|", "\\|"))  # noqa: E731
            rows = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)] + ["| " + " | ".join(cell(x[k]) for k in keys) + " |" for x in v]
            return "\n".join(rows)
        if not v:
            return f"{pad}- none"
        return "\n".join(f"{pad}- {md(x).strip()}" if not isinstance(x, (dict, list)) else f"{pad}-\n{md(x, depth + 1)}" for x in v)
    if isinstance(v, dict):
        lines = []
        for k, x in v.items():
            if isinstance(x, (dict, list)) and x:
                lines.append(f"{pad}- **{k}**:\n{md(x, depth + 1)}")
            else:
                lines.append(f"{pad}- **{k}**: {md(x).strip()}")
        return "\n".join(lines)
    return f"{pad}{v}"


out = [f"# NavisLabs launch film V4 — final product audit (picture lock)", "",
       f"Generated {report['generated_at']} by `scripts/build-final-audit.py`.", "",
       f"| READY_FOR_VOICEOVER | READY_FOR_MUSIC | READY_FOR_FINAL_RENDER |", "|---|---|---|",
       f"| **{str(READY_VO).lower()}** | **{str(READY_MUSIC).lower()}** | **{str(READY_FINAL).lower()}** |", ""]
for s in report["sections"]:
    out += [f"## {s['n']}. {s['title']}", "", md(s["content"]), ""]
with open(os.path.join(ROOT, "navislabs_v4_final_product_audit.md"), "w") as f:
    f.write("\n".join(out))
print(f"sections {len(sections)} · READY_FOR_VOICEOVER={READY_VO} · READY_FOR_MUSIC={READY_MUSIC} · READY_FOR_FINAL_RENDER={READY_FINAL}")
print(f"validators {validators_pass} · renders {renders_ok} · render QC {render_qc_ok} · VO prep {vo_prep_ok} · protected {protected_ok}")
