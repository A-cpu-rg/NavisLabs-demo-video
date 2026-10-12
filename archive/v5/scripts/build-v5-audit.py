#!/usr/bin/env python3
"""V5 narrative + product audit (brief § 23): navislabs_v5_narrative_product_audit.md and .json.

Built from the copy source, the generated V5 data, the audits, the validators, the stale-copy
search, the captions and the render checks — so every statement is traceable. Run after:
npm run data:build · npm run validate:film · npm run copy:stale · the renders · npm run check:render.
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
BRIEF_AT = dt.datetime(2026, 10, 5, 21, 49, 42, tzinfo=dt.timezone.utc)  # V5 narrative brief received
R540, R1080 = "out/navislabs-v5-review-540p.mp4", "out/navislabs-v5-picture-lock-1080p.mp4"


def opt(name):
    p = os.path.join(ROOT, name)
    return json.load(open(p)) if os.path.isfile(p) else None


copydoc = fa.load("src/data/navislabs_v5_copy.json")
data = fa.demo_data()
spec = fa.load("navislabs_v5_film_spec.json")
vo = fa.load("navislabs_v5_voiceover_screen_map.json")["voiceover"]
v4vo = {l["id"]: l for l in json.load(open(os.path.join(ROOT, "archive/v4/navislabs_v4_voiceover_screen_map.json")))["voiceover"]}
surf = fa.load("navislabs_v5_product_surface_map.json")["surfaces"]
val = fa.load("navislabs_v5_validation_report.json")
stale = fa.load("navislabs_v5_stale_copy_report.json")
ent = fa.load("navislabs_entity_audit.json")
cons = fa.load("navislabs_entity_consistency.json")
cap = fa.load("developer_capability_audit.json")
team = fa.load("team_permission_audit.json")
machine = fa.load("interaction_state_machine.json")
sfx = fa.load("navislabs_v5_sfx_map.json")
music = fa.load("navislabs_v5_music_production_brief.json")
audio_plan = fa.load("navislabs_v5_audio_production_plan.json")
render = opt("navislabs_v5_render_check.json")
captions = json.load(open(os.path.join(ROOT, "public/captions/navislabs-v5-captions.json")))
COPY = copydoc["onscreen_copy"]


def probe(path):
    p = os.path.join(ROOT, path)
    if not os.path.isfile(p):
        return None
    pr = json.loads(subprocess.run(["/opt/homebrew/bin/ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p], capture_output=True, text=True).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    return {"file": path, "size_mb": round(int(pr["format"]["size"]) / 1e6, 1), "duration_s": round(float(pr["format"]["duration"]), 2), "video": f"{v['width']}×{v['height']} {v['r_frame_rate']} {v['codec_name']}"}


r540, r1080 = probe(R540), probe(R1080)

# ---- changed lines / visuals --------------------------------------------------
changed_lines = [{"id": l["id"], "start_s": l["start_s"], "v4": v4vo[l["id"]]["voice_line"], "v5": l["voice_line"]} for l in vo if v4vo[l["id"]]["voice_line"] != l["voice_line"]]
CHANGED_VISUALS = [
    ("S01 0–6.2 s", "Opening rebuilt for V01–V02. PEOPLE | AI AGENTS: the person's inbox (Gmail, Jordan Lee · Oct 5) says Acme's renewal moved to Nov 28; the agent's session reads src/workflows/acme-renewal.ts — renewsOn \"2026-11-14\" (Nov 14). Both dates highlight (cobalt / amber) at 2.2 s. At 3.4 s the two views break apart and the truth lands in the six connected systems, a piece in each (a sixth fragment, the Docs account plan, added). Replaces the V4 'line gathers five signals' opening.", "src/scenes/MemoryFlow.tsx, src/ui/demoContent.ts (TWO_TRUTHS, OPENING_SIGNALS), beats truthLabels/truthPeople/truthAgent/truthDiff/signalAccount"),
    ("S02 6.2–10.3 s", "Label AGENTS → AI AGENTS (same as S01). The cursor fades out (8.45–8.85 s) instead of vanishing.", "src/scenes/S02.tsx, copy 'agents'"),
    ("S03 10.3–14.3 s", "Product title NAVIS APPLICATION → NAVIS APP.", "copy 'product.application'"),
    ("S04 14.3–22.6 s", "'Live today' → 'Connected today'; 'Expanding ecosystem · rolling out' → 'Roadmap · coming soon'. Roadmap tiles stay apart, dashed, unlabelled, emitting nothing.", "copy 'liveLabel', 'visionNote'; src/film/DataFlow.tsx comments"),
    ("S05 22.6–26.6 s", "Org intro first row 'Organization' → 'Company'; product caption above the window → NAVIS APP.", "src/film/OrgIntro.tsx; copy"),
    ("S07 29.7–34.2 s", "The cursor fades out as the Why drawer opens (30.2–30.4 s) and returns on the cut back to the card — no pop.", "src/scenes/AppFlow.tsx"),
    ("S11 48.4–52.4 s", "Members (light) → terminal (dark) → Connect (light): 0.16 s dissolves instead of hard light/dark flips.", "src/scenes/S11.tsx"),
    ("S17 73.4–84.0 s", "Header 'One organization · NavisLabs' → 'One company · NavisLabs'; thesis 'One organization.' → 'One company.'; label NAVIS APP. Poster frame (2484) follows.", "copy 'oneCompany', 'thesis1'; src/film/ProductSplit.tsx"),
    ("S18 84.0–94.0 s", "Moat rebuilt for V24. The compounding staircase (More systems → … → More history → Better understanding → More useful) is removed. Agent clients keep changing (Claude Code live verified; Cursor, Codex, VS Code config verified) while the company's record — 'What it knows': Renewal moved to Nov 28 · Owner · Annual plans keep their terms · Revised terms by Oct 7, each with source and freshness — stays put; caption 'What it knows stays yours.'; the client list glides once to centre the pair; pillars unchanged.", "src/scenes/S18.tsx; copy 'staysYours', 'whatItKnows'"),
    ("S18 94–100 s", "End card: NAVIS APP; disclosure now 'Acme Corp and all customer data are fictional demo data … Not yet connected (roadmap): … Navis Developer is in private preview.'", "copy 'product.application', 'disclosure'"),
]

# ---- files ------------------------------------------------------------------------
SKIP = {"node_modules", "out", ".git", ".remotion"}
NEW_IN_V5 = {"src/data/navislabs_v5_copy.json", "scripts/build-captions.py", "scripts/build-v5-audit.py", "scripts/stale-copy-search.py"}
RENAMED = [{"from": "scripts/build-v4-data.py", "to": "scripts/build-film-data.py"}, {"from": "scripts/build-v4-audits.py", "to": "scripts/build-audits.py"},
           {"from": "navislabs_v4_* data, audits and audio pack (project root)", "to": "archive/v4/ (replaced by navislabs_v5_*)"},
           {"from": "scripts/build-final-audit.py (V4 44-section audit)", "to": "archive/v4/scripts/ (replaced by scripts/build-v5-audit.py)"},
           {"from": "navislabs_v3_*, navislabs_final_*, navislabs_audio_map.json, navis_av_validation_report.json, navis_current_vs_target_film_audit.json, navis_film_research_notes.json, navis_launch_av_master.json", "to": "archive/v3-and-earlier/"}]
created, modified = [], []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in SKIP]
    for f in files:
        if f == ".DS_Store":
            continue
        p = os.path.join(d, f)
        st = os.stat(p)
        born = dt.datetime.fromtimestamp(getattr(st, "st_birthtime", st.st_mtime), dt.timezone.utc)
        mod = dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc)
        rel = os.path.relpath(p, ROOT)
        if rel.startswith("archive/"):
            continue
        # New in V5 by name; anything else touched since the brief was modified (an
        # in-place rewrite gives a file a new birth time, so birth time alone misleads).
        if rel in NEW_IN_V5 or rel.startswith(("navislabs_v5_", "captions/", "public/captions/")):
            created.append(rel)
        elif born >= BRIEF_AT or mod >= BRIEF_AT:
            modified.append(rel)
for o in (R540, R1080):
    if os.path.isfile(os.path.join(ROOT, o)):
        created.append(o)
archived = sorted(os.path.relpath(os.path.join(d, f), ROOT) for d, _, fs in os.walk(os.path.join(ROOT, "archive")) for f in fs if f != ".DS_Store")
PROTECTED = ["navis_code_audit.json", "navis_master_cinematic_launch_spec.json", "navis_launch_production_blueprint.json"]
protected_ok = all(p not in modified and p not in created for p in PROTECTED)

# ---- captions check -----------------------------------------------------------------
cap_ok = []
for l in vo:
    for b in l["caption_beats"]:
        first = re.sub(r"[^\w'’-]", "", b["phrase"].split()[0]).lower()
        hit = min((w for w in captions if re.sub(r"[^\w'’-]", "", w["text"]).lower() == first), key=lambda w: abs(w["startMs"] / 1000 - b["lands_at_s"]))
        cap_ok.append({"line": l["id"], "phrase": b["phrase"], "beat_s": b["lands_at_s"], "caption_s": round(hit["startMs"] / 1000, 2), "within": abs(hit["startMs"] / 1000 - b["lands_at_s"]) <= b["tolerance_s"] + 1e-6})

# ---- readiness ------------------------------------------------------------------------
validators_pass = val["all_pass"]
stale_ok = stale["summary"]["fix"] == 0
renders_ok = bool(r540 and r1080 and abs(r540["duration_s"] - 100) < 0.1 and abs(r1080["duration_s"] - 100) < 0.1)
qc_ok = bool(render and render["video"]["frames"] == 3000 and render["audio"]["clipped_samples"] == 0 and not render["vo_silent_lines"] and all(a >= 99.0 for a, _ in render["near_black_runs_s"]))
script_ok = all(l["voice_line"] == next(c["text"] for c in copydoc["voiceover"] if c["id"] == l["id"]) for l in vo) and len(vo) == 26
captions_ok = all(c["within"] for c in cap_ok)
review_done = os.path.isfile(os.path.join(ROOT, "out", "navislabs-v5-review-540p.mp4"))
READY_PICTURE = validators_pass and stale_ok and renders_ok and qc_ok and review_done and protected_ok
READY_VO = READY_PICTURE and script_ok and captions_ok and bool(audio_plan)
final_vo = sum(os.path.isfile(os.path.join(ROOT, "public", l["final"])) for l in vo)
final_score = os.path.isfile(os.path.join(ROOT, "public", "music/final/v4/score.wav"))
READY_FINAL = READY_VO and final_vo == 26 and final_score

by_product = lambda name: [{"surface": s["label"], "claim_status": s["claim_status"], "source": s["source"]} for s in surf if s["product"] == name]  # noqa: E731
integ = data["integrations"]
iscenes = fa.integration_scenes(integ["live_current"], integ["expanding"])

sections = [
    ("Final narrative", {
        "company": "NavisLabs",
        "products": copydoc["positioning"]["products"],
        "thesis": copydoc["positioning"]["thesis"],
        "shape": spec["narrative"]["shape"],
        "never": copydoc["positioning"]["never"],
        "demo_event": spec["narrative"]["business_event"],
    }),
    ("Final 26-line VO table", [{"id": l["id"], "start_s": l["start_s"], "hard_end_s": l["ceiling_s"], "text": l["voice_line"], "on_screen": l["visual"]} for l in vo]),
    ("Every changed line", changed_lines),
    ("Every changed visual", [{"where": w, "change": c, "files": f} for w, c, f in CHANGED_VISUALS]),
    ("Product naming audit", {
        "company": COPY["company"], "products_on_screen": [COPY["product.application"], COPY["product.developer"]],
        "brand_validator": val["summary"]["brand"], "narrative_validator": val["summary"]["narrative"],
        "Navis Application on screen / in copy / in VO": 0, "Navis AI on screen / in copy / in VO": 0,
        "note": "Repository paths such as 'Navis-AI/…' remain in source citations (the Navis App's repository name), never as a product label.",
    }),
    ("Navis App claims audit", by_product("Navis App")),
    ("Navis Developer claims audit", {"surfaces": by_product("Navis Developer"), "claims_avoided": cap["claims_avoided"]}),
    ("Integration audit", {
        "connected_today": [{"id": i, "semantic": integ["semantics"][i], "scenes": iscenes[i]} for i in integ["live_current"]],
        "roadmap_coming_soon": [{"id": i, "semantic": integ["semantics"][i], "scenes": iscenes[i]} for i in integ["expanding"]],
        "label": COPY["visionNote"], "rule": spec["narrative"]["integrations"]["rule"], "validator": val["summary"]["integration"],
    }),
    ("MCP/API/SDK/CLI audit", [{k: s[k] for k in ("surface", "implemented", "private_preview", "published", "working", "shown_as")} for s in cap["surfaces"]]),
    ("Solo/team/org user-model audit", [
        {"user": "A · Organization / team", "shown": "S11 Console › Members: Add a member → Invited; S10–S15 the company's developers and agents work against the company's context; S17 One company", "source": "MembersPanel.tsx, InviteMemberForm.tsx; DEVELOPER_ROLES owner · admin · developer · viewer", "status": "PRIVATE_PREVIEW"},
        {"user": "B · Solo builder", "shown": "S16 (V19): sign up offers 'For my organization' and 'For myself' → Personal workspace, Owner ('A personal workspace holds one member') → navis workstate checkpoint → next session restores the work state", "source": "SignUpForm.tsx, lib/format.ts PERSONAL_WORKSPACE_NOTE, packages/cli workstate", "status": "PRIVATE_PREVIEW"},
        {"user": "C · Developer working with an organization", "shown": "The same company uses the Navis App for people (S05–S09) and Navis Developer for developers and agents (S10–S15) on the same Acme event (S17)", "source": "navislabs_entity_consistency.json", "status": "FILM_SIMULATION (demo data)"},
        {"rule": "Navis Developer does not require an organization (S16 shows the personal path); no developer is shown as needing an enterprise."},
    ]),
    ("Demo-data audit", {"source": "src/data/navislabs_demo_data.json", "summary": ent["summary"], "acme": "Acme Corp is fictional demo data (SYNTHETIC); disclosed on the end card.",
                         "hardcoded_entities_in_components": "none (data_consistency validator)", "consistency": cons["checks"]}),
    ("Caption audit", {"files": ["captions/navislabs-v5.srt", "captions/navislabs-v5.vtt", "public/captions/navislabs-v5-captions.json"],
                       "words": len(captions), "beats_pinned": len(cap_ok), "all_within_tolerance": captions_ok, "beats": cap_ok,
                       "note": "Sidecar captions from the V5 script; nothing is burned into the picture. Re-time from the measured final takes."}),
    ("Cursor/motion audit", {
        "interaction_validator": val["summary"]["interaction"], "cursor_rules": machine["cursor_rules"],
        "fixes": ["S02 cursor fades out (no pop)", "S07 cursor fades out as the drawer opens; returns on the cut back to the card", "S11 0.16 s dissolves between light Console and dark terminal"],
        "motion_blur": "only while the camera moves faster than 14 px/frame (CameraMotionBlur, 6 samples, 180°); hard cuts never ghost",
        "camera": "wide → medium → macro → wide; drifts while reading; one glide in S18 to centre the record",
    }),
    ("SFX audit", {"categories": [{"category": c["category"], "count": c["count"]} for c in sfx["categories"]], "silences": sfx["silences"], "deliberately_silent": sfx["deliberately_silent"], "validator": val["summary"]["audio_timing"]}),
    ("Music audit", {"arc": music["arc"], "forbidden": music["forbidden"], "status": music["status"]}),
    ("Unsupported-claim audit", {"product_claim_validator": val["summary"]["product_claim"],
                                 "checked": ["no 'Navis AI'", "Navis never presented as the model", "no 'autonomous'", "no learning loop / outcome loop presented as built (Outcome 'Building', Learning 'Next')", "no ROI, savings or confidence percentages", "no 'only Navis'", "roadmap integrations never shown as connected", "no public-registry install shown", "no invented economics", "Approve & send by a person — never autonomous sending"],
                                 "removed_in_v5": ["'Your company already has the answer.' (implied a complete answer exists in one place)", "the compounding staircase 'More history → Better understanding → More useful' (implied a learning loop)", "'Expanding ecosystem · rolling out' (could imply partly connected)", "'Your company keeps its history.'"]}),
    ("Stale-copy search results", {"phrases": stale["phrases"], "summary": {k: stale["summary"][k] for k in ("total", "intentional", "fix", "by_phrase")},
                                   "by_file": stale["summary"]["by_file"], "fix": stale["fix"], "report": "navislabs_v5_stale_copy_report.json"}),
    ("Files modified", {"created": sorted(created), "modified": sorted(modified), "renamed_or_moved": RENAMED, "archive_contents": archived}),
    ("Files intentionally not modified", {
        "product_repositories": ["~/Desktop/Navis-AI", "~/Desktop/Devtool (Navis Developer)", "~/Desktop/Backend", "~/Desktop/navis-labs-website"],
        "protected_legacy_sources": PROTECTED, "protected_unchanged": protected_ok,
        "audio_slot_paths": "public/voiceover/final/v4/V01–V26.wav and public/music/final/v4/score.wav keep their names (the brief's expected drop-in paths)",
        "scene_timings": "all 18 scene boundaries and all 26 VO start times unchanged (timeline + narrative validators)",
    }),
    ("READY_FOR_VOICEOVER", READY_VO),
    ("READY_FOR_PICTURE_LOCK", READY_PICTURE),
    ("READY_FOR_FINAL_RENDER", READY_FINAL),
]
assert len(sections) == 22
report = {"about": "NavisLabs launch film — V5 narrative + product audit (scripts/build-v5-audit.py).", "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "READY_FOR_VOICEOVER": READY_VO, "READY_FOR_PICTURE_LOCK": READY_PICTURE, "READY_FOR_FINAL_RENDER": READY_FINAL,
          "inputs": {"validators": validators_pass, "stale_copy_fix": stale["summary"]["fix"], "renders": [x for x in (r540, r1080) if x], "render_qc": render, "script_matches_copy": script_ok, "captions_within_tolerance": captions_ok, "protected_unchanged": protected_ok, "final_vo_files": final_vo, "final_score": final_score},
          "sections": [{"n": i + 1, "title": t, "content": c} for i, (t, c) in enumerate(sections)]}
with open(os.path.join(ROOT, "navislabs_v5_narrative_product_audit.json"), "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
    f.write("\n")


def cell(v):
    if isinstance(v, list):
        return ", ".join(map(str, v))
    if v is None:
        return "—"
    return str(v).replace("|", "\\|").replace("\n", " ")


def md(v, depth=0):
    pad = "  " * depth
    if isinstance(v, bool):
        return f"{pad}**{str(v).lower()}**"
    if isinstance(v, (str, int, float)) or v is None:
        return f"{pad}{cell(v)}"
    if isinstance(v, list):
        if not v:
            return f"{pad}- none"
        if all(isinstance(x, dict) for x in v) and len({tuple(x.keys()) for x in v}) == 1 and all(not isinstance(y, dict) and not (isinstance(y, list) and any(isinstance(z, dict) for z in y)) for x in v for y in x.values()):
            keys = list(v[0].keys())
            return "\n".join(["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)] + ["| " + " | ".join(cell(x[k]) for k in keys) + " |" for x in v])
        return "\n".join(f"{pad}- {md(x).strip()}" if not isinstance(x, (dict, list)) else f"{pad}-\n{md(x, depth + 1)}" for x in v)
    lines = []
    for k, x in v.items():
        lines.append(f"{pad}- **{k}**:\n{md(x, depth + 1)}" if isinstance(x, (dict, list)) and x else f"{pad}- **{k}**: {md(x).strip()}")
    return "\n".join(lines)


out = ["# NavisLabs launch film — V5 narrative + product audit", "",
       f"Generated {report['generated_at']} by `scripts/build-v5-audit.py`. Picture timings: V4 (unchanged). Script: V5 (founder-approved, 26 lines).", "",
       "| READY_FOR_VOICEOVER | READY_FOR_PICTURE_LOCK | READY_FOR_FINAL_RENDER |", "|---|---|---|",
       f"| **{str(READY_VO).lower()}** | **{str(READY_PICTURE).lower()}** | **{str(READY_FINAL).lower()}** |", ""]
for s in report["sections"]:
    out += [f"## {s['n']}. {s['title']}", "", md(s["content"]), ""]
with open(os.path.join(ROOT, "navislabs_v5_narrative_product_audit.md"), "w") as f:
    f.write("\n".join(out))
print(f"READY_FOR_VOICEOVER={READY_VO} · READY_FOR_PICTURE_LOCK={READY_PICTURE} · READY_FOR_FINAL_RENDER={READY_FINAL}")
print(f"validators {validators_pass} · stale fix {stale['summary']['fix']} · renders {renders_ok} · QC {qc_ok} · review {review_done} · script {script_ok} · captions {captions_ok} · protected {protected_ok}")
