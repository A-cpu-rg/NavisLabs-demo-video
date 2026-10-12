#!/usr/bin/env python3
"""Stale-copy search over the whole Navis-Launch-Film project (V7; earlier versions in archive/v5|v6/scripts).

Searches every text file (not node_modules/, out/ renders or .git/) for the old narrative
wording and forbidden claims, and classifies each hit: INTENTIONAL (with the reason) or FIX.
Writes navislabs_v7_stale_copy_report.json; exits 1 if anything needs fixing.
Run: npm run copy:stale
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"node_modules", "out", ".git", ".remotion", "public"}
TEXT_EXT = {".ts", ".tsx", ".js", ".mjs", ".cjs", ".json", ".md", ".py", ".txt", ".srt", ".vtt", ".css", ".html", ".yml", ".yaml"}
PHRASES = [
    ("already has the answer", re.compile(r"already has the answer", re.I)),
    ("NavisLabs turns", re.compile(r"NavisLabs turns", re.I)),
    ("Navis Application", re.compile(r"Navis Application", re.I)),
    ("same organization's", re.compile(r"same organization['’]s", re.I)),
    ("One organization", re.compile(r"One organization", re.I)),
    ("keeps its history", re.compile(r"keeps its history", re.I)),
    ("learning loop", re.compile(r"learning loop", re.I)),
    ("autonomous", re.compile(r"\bautonomous", re.I)),
    ("confidence percentage", re.compile(r"confidence percentage", re.I)),
    ("ROI", re.compile(r"\bROI\b")),
    ("savings", re.compile(r"\bsavings\b", re.I)),
    ("only Navis", re.compile(r"only Navis", re.I)),
    ("Navis AI", re.compile(r"\bNavis AI\b", re.I)),
    ("coming soon", re.compile(r"coming soon", re.I)),
    ("roadmap", re.compile(r"\broadmap\b", re.I)),
    ("Acme", re.compile(r"\bAcme\b|\bACME\b|acme-", re.I)),
    ("Jordan Lee", re.compile(r"Jordan Lee|\bJordan\b")),
    ("Sam Rivera", re.compile(r"Sam Rivera")),
]
PROTECTED = {"navis_master_cinematic_launch_spec.json", "navis_launch_production_blueprint.json", "navis_code_audit.json"}
SELF = {"scripts/stale-copy-search.py", "scripts/validate-film.py", "navislabs_v7_stale_copy_report.json", "navislabs_v7_validation_report.json", "scripts/build-v7-audit.py",
        "navislabs_v5_stale_copy_report.json", "navislabs_v5_validation_report.json"}
AUDITS = {"navislabs_v6_final_product_audit.md", "scripts/build-v7-audit.py", "navislabs_v6_ready_for_final.md", "navislabs_v7_final_product_audit.md", "navislabs_v7_audio_audit.md",
          "navislabs_v7_visual_audit.md", "navislabs_v7_customer_entity_audit.json", "navislabs_v7_readiness_report.md",
          "navislabs_v5_narrative_product_audit.md", "navislabs_v5_narrative_product_audit.json", "scripts/build-v5-audit.py"}
# Files that record the public website's / local source's integration status beside the film's launch state.
STATUS_RECORDS = {"src/data/navislabs_v7_launch_state.json", "scripts/build-audits.py", "navislabs_entity_audit.json", "scripts/build-film-data-v7.py",
                  "navislabs_v7_product_surface_map.json", "src/config/navisBrand.ts", "src/ui/demoContent.ts", "README.md"}


def classify(rel, phrase, line):
    if rel.startswith("archive/"):
        return "INTENTIONAL", "archived history (archive/README.md); read by nothing"
    if rel in PROTECTED:
        return "INTENTIONAL", "protected legacy source (not modified per brief); code reads it only for design tokens / legacy schema checks — no copy from it reaches the screen"
    if rel in SELF:
        return "INTENTIONAL", "the search / validator pattern itself"
    if rel in AUDITS:
        return "INTENTIONAL", "the audit records the old wording / the public website's status it compares against"
    if phrase in ("Acme", "Jordan Lee", "Sam Rivera") and rel in ("README.md", "archive/README.md"):
        return "INTENTIONAL", "explains what V7 replaced"
    if phrase in ("Acme", "Jordan Lee", "Sam Rivera") and rel == "src/data/navislabs_v7_launch_state.json":
        return "FIX", "stale customer/person name in the V7 data"
    if phrase in ("coming soon", "roadmap") and rel in STATUS_RECORDS:
        return "INTENTIONAL", "records the public website's current status beside the film's launch state (an annotation, never on screen; validator: narrative)"
    if phrase in ("coming soon", "roadmap") and rel.endswith((".ts", ".tsx")) and line.lstrip().startswith(("//", "*", "/*")):
        return "INTENTIONAL", "source comment (stripped before anything reaches the screen)"
    if rel in ("src/data/navislabs_v5_copy.json", "src/data/navislabs_v7_copy.json") and ('"never"' in line or phrase in ("Navis AI", "autonomous", "coming soon", "roadmap")):
        return "INTENTIONAL", "positioning rules: the words the film must never use"
    if rel == "scripts/build-film-data.py" and phrase == "Navis Application" and ("x.get(\"product\")" in line or "archive/v4" in line):
        return "INTENTIONAL", "rename rule for older surface records ('Navis Application' → 'Navis App')"
    if rel == "scripts/asset-requirements.mjs" and phrase == "Navis AI":
        return "INTENTIONAL", "rename rule: the legacy spec's 'Navis AI' becomes 'Navis App' in asset_requirements.json"
    if rel == "src/ui/developer/Console.tsx" and phrase == "One organization" and "scoped to one organization" in line:
        return "INTENTIONAL", "verbatim Devtool product copy (features/connect/data/surfaces.ts L1019: 'scoped to one organization by that key alone') — about API-key scope, not the narrative"
    if rel == "README.md" and "archive" in line.lower():
        return "INTENTIONAL", "README explains what was archived"
    return "FIX", ""


hits = []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
    for f in files:
        if os.path.splitext(f)[1] not in TEXT_EXT or f in ("package-lock.json", "navislabs_v5_stale_copy_report.json", "navislabs_v7_stale_copy_report.json"):
            continue
        p = os.path.join(d, f)
        rel = os.path.relpath(p, ROOT)
        try:
            lines = open(p, encoding="utf-8").read().split("\n")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            for phrase, rx in PHRASES:
                for m in rx.finditer(line):
                    kind, why = classify(rel, phrase, line)
                    hits.append({"phrase": phrase, "file": rel, "line": n, "text": line.strip()[:200], "class": kind, "why": why})

fix = [h for h in hits if h["class"] == "FIX"]
by_file = {}
for h in hits:
    by_file.setdefault((h["class"], h["file"]), 0)
    by_file[(h["class"], h["file"])] += 1
report = {
    "about": "Stale-copy search over the whole project (excludes node_modules/, out/ renders, public/ media, .git/). Each hit is INTENTIONAL (with the reason) or FIX.",
    "phrases": [p for p, _ in PHRASES],
    "summary": {"total": len(hits), "intentional": len(hits) - len(fix), "fix": len(fix),
                "by_phrase": {p: sum(1 for h in hits if h["phrase"] == p) for p, _ in PHRASES},
                "by_file": [{"file": f, "class": c, "hits": n} for (c, f), n in sorted(by_file.items(), key=lambda kv: (kv[0][0], kv[0][1]))]},
    "fix": fix,
    "hits": hits,
}
with open(os.path.join(ROOT, "navislabs_v7_stale_copy_report.json"), "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"hits {len(hits)} · intentional {len(hits) - len(fix)} · fix {len(fix)}")
for h in fix:
    print(f"  FIX {h['file']}:{h['line']} [{h['phrase']}] {h['text'][:120]}")
sys.exit(1 if fix else 0)
