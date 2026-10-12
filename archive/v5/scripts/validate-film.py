#!/usr/bin/env python3
"""Film validators. Every one must pass before picture lock.

  narrative · brand · entity · product_claim · integration · interaction ·
  timeline · audio_timing · visual_asset · data_consistency

Reads src/ (comments stripped: only what can reach the screen), the generated
JSONs and the resolved TS config (scripts/dump-config.mjs). Writes
navislabs_v5_validation_report.json; exits 1 if any validator fails.
Run: npm run validate:film
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
data = fa.demo_data()
spec = fa.load("navislabs_v5_film_spec.json")
vo_map = fa.load("navislabs_v5_voiceover_screen_map.json")
audio = fa.load("navislabs_v5_audio_map.json")
surfaces = fa.load("navislabs_v5_product_surface_map.json")
copydoc = fa.load("src/data/navislabs_v5_copy.json")
machine = fa.load("interaction_state_machine.json")
entity_audit = fa.load("navislabs_entity_audit.json")
consistency = fa.load("navislabs_entity_consistency.json")
cfg = json.loads(subprocess.run(["node", os.path.join(ROOT, "scripts", "dump-config.mjs")], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
COPY = spec["onscreen_copy"]
VO = vo_map["voiceover"]

# Files that can reach the screen: every scene's import closure, the
# composition, and the config modules whose strings are rendered.
RENDERED = set()
for sid in fa.SCENE_IDS:
    RENDERED |= fa.closure(os.path.join(fa.SRC, "scenes", f"{sid}.tsx"))
for d in ("compositions",):
    for f in os.listdir(os.path.join(fa.SRC, d)):
        RENDERED.add(os.path.join(fa.SRC, d, f))
RENDERED.add(os.path.join(fa.SRC, "config", "navisBrand.ts"))
RENDERED = sorted(p for p in RENDERED if p.endswith((".ts", ".tsx")))
VISIBLE = {p: fa.visible_text(p) for p in RENDERED}


def data_values(obj, skip=("note", "about", "provenance")):
    """Every string value in the demo data except annotations."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k not in skip:
                yield from data_values(v, skip)
    elif isinstance(obj, list):
        for v in obj:
            yield from data_values(v, skip)
    elif isinstance(obj, str):
        yield obj


SCREEN_STRINGS = (
    [s for p in RENDERED for s in fa.string_literals(VISIBLE[p])]
    + [v for v in COPY.values() if isinstance(v, str)]
    + [l["voice_line"] for l in VO]
    + list(data_values(data))
)
SCREEN_TEXT = "\n".join(SCREEN_STRINGS) + "\n" + "\n".join(VISIBLE.values())

results = {}


class V:
    def __init__(self, name):
        self.name, self.checks = name, []

    def check(self, what, ok, detail=None):
        self.checks.append({"check": what, "pass": bool(ok), **({"detail": detail} if detail not in (None, [], "") else {})})

    def done(self):
        results[self.name] = {"pass": all(c["pass"] for c in self.checks), "checks": self.checks}


def hits(rx, text=SCREEN_TEXT, flags=0):
    return sorted(set(m.group(0) for m in re.finditer(rx, text, flags)))


# 0 · narrative ---------------------------------------------------------------
# The founder-approved V5 script and the locked V4 timings (the brief, verbatim).
SCRIPT_STARTS = {"V01": 0.6, "V02": 3.1, "V03": 6.6, "V04": 10.6, "V05": 14.6, "V06": 18.4, "V07": 22.8, "V08": 26.8, "V09": 29.9, "V10": 34.5, "V11": 37.8, "V12": 41.2, "V13": 45.0,
                 "V14": 48.5, "V15": 52.5, "V16": 56.0, "V17": 59.0, "V18": 62.4, "V19": 66.8, "V20": 73.6, "V21": 77.7, "V22": 81.4, "V23": 84.4, "V24": 88.4, "V25": 90.4, "V26": 94.2}
# Case-insensitive unless the brief's phrase is a headline ("One organization" as a line;
# the Console's real "scoped to one organization" is product copy, not narrative).
STALE = ["(?i)already has the answer", "(?i)NavisLabs turns", "(?i)Navis Application", "(?i)same organization's", "One organization", "(?i)keeps its history",
         "(?i)learning loop", "(?i)\\bautonomous", "(?i)confidence percentage", r"\bROI\b", "(?i)\\bsavings\\b", "(?i)only Navis", "(?i)rolling out", r"(?i)\bNavis[ -]AI\b"]
v = V("narrative")
script = {l["id"]: l["text"] for l in copydoc["voiceover"]}
v.check("26 lines in the copy source", len(script) == 26 and sorted(script) == sorted(SCRIPT_STARTS))
v.check("screen map speaks the copy source, word for word", all(l["voice_line"] == script[l["id"]] for l in VO), [l["id"] for l in VO if l["voice_line"] != script[l["id"]]])
v.check("audio map speaks the copy source, word for word", all(l["text"] == script[l["id"]] for l in audio["voiceover"]), [l["id"] for l in audio["voiceover"] if l["text"] != script[l["id"]]])
moved = [f"{l['id']}: {l['start_s']} (locked {SCRIPT_STARTS[l['id']]})" for l in VO if abs(l["start_s"] - SCRIPT_STARTS[l["id"]]) > 1e-6]
v.check("every line starts at its locked V4 time", not moved, moved)
v.check("every line has caption beats inside its window", all(l.get("caption_beats") and all(l["start_s"] - 1e-6 <= c["lands_at_s"] <= l["ceiling_s"] for c in l["caption_beats"]) for l in VO))
v.check("every caption phrase is in its line", all(c["phrase"] in l["voice_line"] for l in VO for c in l["caption_beats"]))
v.check("every line lists its product claims", all("product_claims" in l for l in VO))
stale_hits = sorted({f"{pat}: {m}" for pat in STALE for m in hits(pat, SCREEN_TEXT)})
v.check("no stale or forbidden copy can reach the screen, the copy or the VO", not stale_hits, stale_hits)
v.check("thesis: One understanding. Two ways in.", copydoc["positioning"]["thesis"] == "One understanding. Two ways in." and script["V22"] == "One understanding. Two ways in.")
v.done()

# 1 · brand ------------------------------------------------------------------
v = V("brand")
v.check("no 'NAVIS AI' / 'Navis-AI' label on screen, in copy or in VO", not hits(r"\bnavis[\s_-]?ai\b", flags=re.I), hits(r"\bnavis[\s_-]?ai\b", flags=re.I))
v.check("no 'Navis Labs' (company is one word: NavisLabs)", not hits(r"\bNavis Labs\b"), hits(r"\bNavis Labs\b"))
v.check("no repository names as product labels ('Devtool')", not hits(r"\bDevtool\b", "\n".join(SCREEN_STRINGS)), hits(r"\bDevtool\b", "\n".join(SCREEN_STRINGS)))
v.check("company name is NavisLabs", COPY.get("company") == "NavisLabs", COPY.get("company"))
v.check("products are the Navis App and Navis Developer",
        COPY.get("product.application", "").lower() == "navis app" and COPY.get("product.developer", "").lower() == "navis developer",
        [COPY.get("product.application"), COPY.get("product.developer")])
v.check("tagline is the website headline", COPY.get("tagline") == "The shared understanding for your organization.", COPY.get("tagline"))
v.check("logo assets exist (mark without tile, dark + light)", all(os.path.isfile(os.path.join(PUBLIC, "images", "brand", f)) for f in ("navislabs-mark-dark.png", "navislabs-mark-light.png")))
v.done()

# 2 · entity -----------------------------------------------------------------
v = V("entity")
audited = {e["entity"].split(":", 1)[1].split(".")[0] for e in entity_audit["entities"]}
ids = [data["company"]["id"]] + [x["id"] for k in ("people", "teams", "customers", "projects", "decisions", "commitments", "meetings", "emails", "documents", "repositories", "agents", "runs") for x in data[k]] + [data["developer_workspace"]["solo"]["id"]]
missing = [i for i in ids if i not in audited]
v.check("every demo-data entity has an entity-audit row", not missing, missing)
bad_prov = [e["entity"] for e in entity_audit["entities"] if e["real_or_synthetic"] not in ("REAL_AUTHORIZED", "REAL_PUBLIC_PRODUCT", "SYNTHETIC", "REAL_PERSON", "REAL_COMPANY")]
v.check("every row has a known provenance", not bad_prov, bad_prov)
shown_unauth = [e["entity"] for e in entity_audit["entities"] if not e["authorized_for_public_video"] and e["scenes"]]
v.check("nothing unauthorized appears in a scene", not shown_unauth, shown_unauth)
restricted = hits(r"mulayam|digantara", flags=re.I)
v.check("restricted names (Mulayam, Digantara) appear nowhere on screen, in copy, VO or demo values", not restricted, restricted)
emails = sorted(set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "\n".join(SCREEN_STRINGS))))
bad_mail = [e for e in emails if not (e == "abhishek@navislabs.in" or e.endswith("@example.com") or e.endswith(".example"))]
v.check("emails are the founder's own or reserved example domains", not bad_mail, bad_mail)
synthetic = [p["name"] for p in data["people"] if p["provenance"] == "SYNTHETIC"]
v.check("synthetic people are marked SYNTHETIC", len(synthetic) == 3, synthetic)
SECRET = r"navis_(?!<)[A-Za-z0-9]{6,}_[A-Za-z0-9]{12,}|\bsk-[A-Za-z0-9]{20,}|sk_live_[A-Za-z0-9]+|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|ELEVENLABS_API_KEY\s*[=:]\s*['\"]?[A-Za-z0-9]{16,}|xi-api-key\s*[:=]\s*['\"]?[A-Za-z0-9]{16,}"
scan = [p for p in fa.ts_files()] + [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".json")] + [os.path.join(ROOT, "scripts", f) for f in os.listdir(os.path.join(ROOT, "scripts"))]
leaks = [fa.rel(p) for p in scan if os.path.isfile(p) and re.search(SECRET, fa.read(p))]
v.check("no API keys, tokens or private keys in src, scripts or JSON", not leaks, leaks)
gi = fa.read(os.path.join(ROOT, ".gitignore")) if os.path.isfile(os.path.join(ROOT, ".gitignore")) else ""
v.check(".env is git-ignored", ".env" in gi)
v.done()

# 3 · product_claim -------------------------------------------------------------
v = V("product_claim")
legend = set(surfaces["claim_status_legend"])
bad = [s["id"] for s in surfaces["surfaces"] if s["claim_status"] not in legend]
v.check("every surface has a known claim status", not bad, bad)
fut = [s["id"] for s in surfaces["surfaces"] if s["claim_status"] in ("FUTURE_STATE", "ROADMAP")]
v.check("roadmap surfaces carry an on-screen 'Roadmap · coming soon' label", "coming soon" in COPY.get("visionNote", "").lower() and "roadmap" in COPY.get("visionNote", "").lower(), fut)
v.check("end-card disclosure: fictional demo data, roadmap not yet connected, private preview", all(k in COPY.get("disclosure", "").lower() for k in ("fictional", "demo", "not yet connected", "roadmap", "private preview")), COPY.get("disclosure"))
v.check("Navis is never presented as the model", not hits(r"Navis (is|=) (the|a) (model|LLM)", "\n".join(SCREEN_STRINGS), re.I))
v.check("Outcome and Learning stay labelled Building / Next", all(k in "\n".join(VISIBLE.values()) for k in ("Building", "Next")))
v.check("SDK shown as not on npm", "not on npm" in SCREEN_TEXT)
pub = hits(r"npm install @navis/sdk|npm i @navis/sdk|pip install navis", "\n".join(VISIBLE.values()))
v.check("no public-registry install shown as working", not pub, pub)
v.check("the run's outcome is 'Not judged'", data["runs"][0]["outcome"] == "Not judged")
econ = [k for r in data["runs"] for st in r.get("steps", []) for k in st if k in ("tokens", "cost", "latency", "model")]
v.check("no invented economics on run steps (shown as '—')", not econ, econ)
v.check("no 'Projects' page in the Console", '"Projects"' not in VISIBLE.get(os.path.join(fa.SRC, "ui", "developer", "Console.tsx"), ""))
policy_live = hits(r"policy engine (?:is )?(?:enabled|active|live)|policies enforced", flags=re.I)
v.check("central policy engine not shown as live", not policy_live, policy_live)
clients = re.findall(r'name: "([^"]+)", status: "([^"]+)"', fa.read(os.path.join(fa.SRC, "config", "navisBrand.ts")))
v.check("only Claude Code is shown as live verified", [n for n, s in clients if s == "live verified"] == ["Claude Code"], clients)
v.check("placeholders only for credentials", "NAVIS_API_KEY" in SCREEN_TEXT and "navis_<prefix>_<secret>" in SCREEN_TEXT)
v.done()

# 4 · integration -----------------------------------------------------------------
v = V("integration")
brand_src = fa.read(os.path.join(fa.SRC, "config", "navisBrand.ts"))


def ids_in(block_name):
    m = re.search(rf"export const {block_name} = \[[\s\S]*?\n\]", brand_src)
    return re.findall(r'id: "(\w+)"', m.group(0)) if m else []


live, expanding = data["integrations"]["live_current"], data["integrations"]["expanding"]
v.check("live set matches the website's supported logos", sorted(ids_in("INTEGRATIONS")) == sorted(live), [ids_in("INTEGRATIONS"), live])
v.check("expanding set matches the website's 'soon' logos", sorted(ids_in("ROADMAP_INTEGRATIONS")) == sorted(expanding), [ids_in("ROADMAP_INTEGRATIONS"), expanding])
v.check("live and expanding are disjoint", not set(live) & set(expanding))
v.check("every system has a semantic", all(i in data["integrations"]["semantics"] for i in live + expanding))
names = {"salesforce": "Salesforce", "hubspot": "HubSpot", "jira": "Jira", "github": "GitHub", "notion": "Notion", "zoom": "Zoom", "microsoft365": "Microsoft 365"}
dc = fa.strip_comments(fa.read(fa.DEMO_CONTENT))
WORKFLOW = ["OPENING_SIGNALS", "HAND_COPIES", "PRIORITIES", "ACME_SIGNALS", "SYSTEM_FACTS", "FLOW_SIGNALS", "RESULT_ROWS", "AGENT_LINES", "ACME_DRAFT", "ACME_CONTEXT", "JUST_LEARNED", "ACME_NEXT", "ACME_STATE"]
cited = []
for name in WORKFLOW:
    m = re.search(rf"export const {name}\b([\s\S]*?)(?=\nexport |\Z)", dc)
    body = m.group(1) if m else ""
    for i in expanding:
        if re.search(rf'"{i}"', body) or re.search(rf"\b{re.escape(names[i])}\b", body):
            cited.append(f"{name}: {i}")
v.check("demonstrated workflows cite live systems only", not cited, cited)
steps = " ".join(st["what"] for r in data["runs"] for st in r.get("steps", []))
v.check("run steps cite live systems only", not [n for n in names.values() if re.search(rf"\b{re.escape(n)}\b", steps)])
sc = fa.integration_scenes(live, expanding)
outside = {i: s for i, s in sc.items() if i in expanding and set(s) - {"S04"}}
v.check("expanding systems appear only in the S04 ecosystem view", not outside, outside)
v.check("roadmap systems are labelled 'coming soon', never 'rolling out' or connected", not hits(r"rolling out", flags=re.I) and "Roadmap · coming soon" in COPY.get("visionNote", ""), hits(r"rolling out", flags=re.I))
v.done()

# 5 · interaction ----------------------------------------------------------------
v = V("interaction")
RANK = {"before": 0, "settle": 1, "click": 2, "feedback": 3, "feedback2": 3, "after": 4}
for it in machine["interactions"]:
    st = it["states"]
    times = [s["at_s"] for s in st]
    v.check(f"{it['id']}: states are in time order", times == sorted(times), times)
    if it["cursor"]:
        names_ = [s["state"] for s in st]
        v.check(f"{it['id']}: before → settle → click → feedback → after", names_ == ["before", "settle", "click", "feedback", "after"], names_)
        if "settle" in names_ and "click" in names_:
            gap = round(st[names_.index("click")]["at_s"] - st[names_.index("settle")]["at_s"], 3)
            v.check(f"{it['id']}: cursor settles ≥ 0.1 s before the click", gap >= 0.1 - 1e-6, gap)
rules = machine["cursor_rules"]
v.check("cursor has no click ring", rules["ring"] is False and "<circle" not in fa.visible_text(os.path.join(fa.SRC, "components", "Cursor.tsx")))
PRESS = {"click", "approve", "select", "confirm"}
clicks = sorted(e["at"] for e in cfg["SFX_EVENTS"] if e["sfx"] in PRESS)
unheard = [it["id"] for it in machine["interactions"] if it["cursor"] and not any(abs(c - next(s["at_s"] for s in it["states"] if s["state"] == "click")) < 0.05 for c in clicks)]
v.check("every cursor click has a press sound (click / approve / select) at the same moment", not unheard, unheard)
v.done()

# 6 · timeline ---------------------------------------------------------------------
v = V("timeline")
scenes = cfg["FILM_SCENES"]
fps = cfg["FILM_FPS"]
v.check("18 scenes S01–S18 in order", [s["id"] for s in scenes] == fa.SCENE_IDS)
v.check("starts at 0 s and ends at 100 s", scenes[0]["from"] == 0 and scenes[-1]["to"] == 100)
gaps = [f"{a['id']}→{b['id']}" for a, b in zip(scenes, scenes[1:]) if abs(a["to"] - b["from"]) > 1e-6]
v.check("scenes are contiguous", not gaps, gaps)
v.check("3000 frames at 30 fps", cfg["FILM_FRAMES"] == 3000 and fps == 30 and spec["format"]["frames"] == 3000)
total = sum(round(s["to"] * fps) - round(s["from"] * fps) for s in scenes)
v.check("scene lengths sum to 3000 frames", total == 3000, total)
bad_t = []
for a, b in zip(scenes, scenes[1:] + [None]):
    t = a["transitionOut"]
    if t["type"] not in ("none", "fade", "wipe") or (t["type"] == "none") != (t["frames"] == 0):
        bad_t.append(f"{a['id']}: {t}")
    if b and t["frames"] > min(round((a["to"] - a["from"]) * fps), round((b["to"] - b["from"]) * fps)) / 2:
        bad_t.append(f"{a['id']}: {t['frames']}f too long")
    if not b and t["type"] != "none":
        bad_t.append("last scene has a transition out")
v.check("transitions are fade/wipe/none and at most half of each neighbour", not bad_t, bad_t)
out_of_range = [k for k, t in cfg["BEAT"].items() if not 0 <= t <= 100]
v.check("all beats lie within the film", not out_of_range, out_of_range)
typing_bad = [k for k, t in cfg["TYPING"].items() if t["text"] != "(unused)" and not 0 <= t["start"] + len(t["text"]) / t["cps"] <= 100]
v.check("all typing ends within the film", not typing_bad, typing_bad)
v.done()

# 7 · audio_timing -------------------------------------------------------------------


def wav_len(rel):
    p = os.path.join(PUBLIC, rel)
    if not os.path.isfile(p):
        return None
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


v = V("audio_timing")
scene_at = {s["id"]: s for s in scenes}
over, overlap, missing_tmp, outside_scene, el_missing = [], [], [], [], []
for i, l in enumerate(VO):
    d = wav_len(l["temp"])
    if d is None:
        missing_tmp.append(l["id"])
    elif l["start_s"] + d > l["ceiling_s"] + 0.05 or d > l["max_duration_s"] + 0.05:
        over.append(f"{l['id']}: {d:.2f}s from {l['start_s']} (ceiling {l['ceiling_s']}, max {l['max_duration_s']})")
    if i + 1 < len(VO) and l["ceiling_s"] > VO[i + 1]["start_s"] + 1e-6:
        overlap.append(f"{l['id']}→{VO[i + 1]['id']}")
    s = scene_at[l["scene"]]
    if not s["from"] - 1e-6 <= l["start_s"] < s["to"]:
        outside_scene.append(l["id"])
    el = l["elevenlabs"]
    need = ("text", "emotion", "delivery", "pace", "pause", "pronunciation", "max_duration_s", "visual_moment")
    if any(k not in el for k in need):
        el_missing.append(l["id"])
v.check("26 VO lines", len(VO) == 26, len(VO))
v.check("every temp VO file exists", not missing_tmp, missing_tmp)
v.check("every VO line fits its ceiling and max duration", not over, over)
v.check("VO lines never overlap", not overlap, overlap)
v.check("each VO line starts inside its scene", not outside_scene, outside_scene)
v.check("every line has a complete ElevenLabs block", not el_missing, el_missing)
tagged = sum(1 for l in VO if l["elevenlabs"].get("audio_tag"))
v.check("audio tags used sparingly (≤ 1/3 of lines)", tagged <= len(VO) / 3, f"{tagged}/{len(VO)}")
sec_ = audio["music"]["sections"]
v.check("music sections cover 0–100 s contiguously", sec_[0]["from_s"] == 0 and sec_[-1]["to_s"] == 100 and all(abs(a["to_s"] - b["from_s"]) < 1e-6 for a, b in zip(sec_, sec_[1:])))
ARC = [0, 12, 22, 45, 68, 82, 94, 100]  # approved audio-production arc
starts = [s["from_s"] for s in sec_] + [100]
far = [b for b in ARC if min(abs(b - x) for x in starts) > 2.5]
v.check("music follows the brief's arc (boundaries within 2.5 s)", not far, far)
v.check("temp score exists", wav_len(audio["music"]["temp"]) is not None)
lib = audio["sfx"]["library"]
bad_sfx = sorted({e["sfx"] for e in cfg["SFX_EVENTS"] if e["sfx"] not in lib or not os.path.isfile(os.path.join(PUBLIC, lib[e["sfx"]]["temp"]))})
v.check("every SFX event has a library sound with a temp file", not bad_sfx, bad_sfx)
v.check("SFX events lie within the film", all(0 <= e["at"] <= 100 for e in cfg["SFX_EVENTS"]))
cats = set(cfg["SFX_CATEGORIES"])
bad_cat = sorted({e.get("category", "?") for e in cfg["SFX_EVENTS"]} - cats)
v.check("every SFX event is one of the 15 meaningful categories", len(cats) == 15 and not bad_cat, bad_cat)
in_silence = [f"{e['category']} @ {e['at']:.2f}s in '{w['why']}'" for e in cfg["SFX_EVENTS"] for w in cfg["SFX_SILENCES"] if w["from"] <= e["at"] < w["to"]]
v.check("no SFX inside the deliberate silences", not in_silence, in_silence)
finals = []
for l in VO:
    p = os.path.join(PUBLIC, l["final"])
    if os.path.isfile(p):
        try:
            with wave.open(p) as w:
                d, sr = w.getnframes() / w.getframerate(), w.getframerate()
        except (wave.Error, EOFError):
            finals.append(f"{l['id']}: unreadable WAV (convert to 48 kHz PCM)")
            continue
        if d > l["max_duration_s"] + 0.05 or sr != 48000:
            finals.append(f"{l['id']}: {d:.2f}s (max {l['max_duration_s']}), {sr} Hz")
v.check("final VO takes, where present, fit their hard end at 48 kHz", not finals, finals)
amb = audio["ambience"]
s04 = scene_at["S04"]
v.check("ambience sits under the S04 data flow only", s04["from"] - 0.5 <= amb["from_s"] and amb["to_s"] <= s04["to"] + 0.5, [amb["from_s"], amb["to_s"]])
v.check("audio layers defined (VO, music, UI SFX, transitions, ambience)", set(audio["layers"]) == {"vo", "music", "ui_sfx", "transitions", "ambience"})
v.done()

# 8 · visual_asset ---------------------------------------------------------------------
v = V("visual_asset")
ASSET = re.compile(r"^/?[\w./-]+\.(png|jpe?g|svg|webp|gif|wav|mp3|m4a|woff2?|ttf|otf|mp4)$", re.I)
refs = sorted({s.lstrip("/") for p in fa.ts_files() for s in fa.string_literals(fa.visible_text(p)) if ASSET.match(s)})
gone = [r for r in refs if not os.path.isfile(os.path.join(PUBLIC, r))]
v.check(f"every literal asset path in src exists in public/ ({len(refs)} paths)", not gone, gone)
logo_dirs = re.findall(r'"((?:logos?|images)/[^"]+)"', brand_src)
v.check("every integration logo and brand mark exists", all(os.path.isfile(os.path.join(PUBLIC, x)) for x in logo_dirs), [x for x in logo_dirs if not os.path.isfile(os.path.join(PUBLIC, x))])
v.check("Claude Code icon exists", os.path.isfile(os.path.join(PUBLIC, "images", "clients", "claude.png")))
v.done()

# 9 · data_consistency -----------------------------------------------------------------
v = V("data_consistency")
people = data["people"]
cust = data["customers"][0]
literal_values = (
    [p["name"] for p in people] + [p["email"] for p in people]
    + [p.get("mac_host", "") for p in people if p.get("mac_host")]
    + [cust["name"], cust["caps"], cust["slug"], cust["renewal_was"], cust["renewal_now"], cust["renewal_was_iso"], cust["renewal_now_iso"]]
    + [e["date_iso"] for e in data["emails"]] + [d["date_iso"] for d in data["decisions"]] + [data["application_workspace"]["date_iso"]]
    + [x["ticket"] for x in data["projects"] if x.get("ticket")] + [x["file"] for x in data["projects"] if x.get("file")]
    + [r["id"] for r in data["runs"]] + [r["task"] for r in data["runs"]]
    + [d["short"] for d in data["decisions"]] + [e["subject"] for e in data["emails"]]
    + [r["name"] for r in data["repositories"] if r["name"] != data["company"]["name"]]
    + [data["developer_workspace"]["solo"]["name"]]
)
WORD = [p["first"] for p in people if p["provenance"] == "SYNTHETIC"] + [cust["short"]]
ALLOWED = {fa.DEMO_CONTENT, os.path.join(fa.SRC, "config", "navisBrand.ts")}
found = []
for p in fa.ts_files():
    if p in ALLOWED or p.endswith("evidence.ts"):
        continue
    code = fa.visible_text(p)
    for val in literal_values:
        if val and val in code:
            found.append(f"{fa.rel(p)}: {val}")
    for w in WORD:
        if re.search(rf"\b{re.escape(w)}\b", code):
            found.append(f"{fa.rel(p)}: {w}")
found = sorted(set(found))
v.check("no entity value hardcoded in TSX (outside the data and demoContent)", not found, found)
run = data["runs"][0]
ts_ = [st["at"] for st in run["steps"]]
to_s = lambda t: int(t[:2]) * 3600 + int(t[3:5]) * 60 + int(t[6:8])  # noqa: E731
mins, secs = re.match(r"(\d+)m (\d+)s", run["duration"]).groups()
v.check("run steps are in order and fit the run's duration", ts_ == sorted(ts_) and to_s(ts_[-1]) - to_s(ts_[0]) <= int(mins) * 60 + int(secs), f"{ts_[0]}–{ts_[-1]} vs {run['duration']}")
v.check("run start matches its first step", run["started"].endswith(ts_[0][:5]), [run["started"], ts_[0]])
v.check("'Updates' tile is 0 (the product always reports 0)", data["application_workspace"]["glance"]["updates"] == 0)
dates = set(re.findall(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}\b", "\n".join(data_values(data))))
vo_dates = set(re.findall(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}\b", " ".join(l["voice_line"] for l in VO)))
v.check("dates in the VO exist in the demo data", vo_dates <= dates, sorted(vo_dates - dates))
v.check("same customer, decision and commitment in both products", all(consistency["checks"][k] for k in ("customer_in_both_products", "decision_in_both_products", "commitment_in_both_products")))
v.check("one coherent run: the agent's task is the run's task", re.search(r"export const AGENT_TASK = RUN\.task", dc) is not None)
v.done()

report = {
    "about": "Film validators (scripts/validate-film.py). All must pass before picture lock.",
    "all_pass": all(r["pass"] for r in results.values()),
    "summary": {k: r["pass"] for k, r in results.items()},
    "validators": results,
}
with open(os.path.join(ROOT, "navislabs_v5_validation_report.json"), "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
    f.write("\n")
for k, r in results.items():
    fails = [c for c in r["checks"] if not c["pass"]]
    print(f"{'PASS' if r['pass'] else 'FAIL'}  {k:<17} {len(r['checks']) - len(fails)}/{len(r['checks'])}")
    for c in fails:
        print(f"      ✗ {c['check']}: {c.get('detail', '')}")
sys.exit(0 if report["all_pass"] else 1)
