#!/usr/bin/env python3
"""V6 film validators. Every one must pass before the review render is called ready.

  narrative · brand · entity · product_claim · integration · interaction · timeline ·
  voice_audio · visual_asset · data_consistency · captions

Reads src/ (comments stripped: only what can reach the screen), the V6 data
(copy, launch state, voice analysis + timeline, spec, audio map), the audits and
the resolved TS config (scripts/dump-config.mjs). Writes
navislabs_v6_validation_report.json; exits 1 if any validator fails.
The V5 validator is preserved in archive/v5/scripts/validate-film.py.
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
data = fa.demo_data()  # src/data/navislabs_v6_launch_state.json
spec = fa.load("navislabs_v6_film_spec.json")
timeline = fa.load("navislabs_v6_voice_timeline.json")
analysis = fa.load("navislabs_v6_voice_analysis.json")
audio = fa.load("navislabs_v6_audio_map.json")
surfaces = fa.load("navislabs_v6_product_surface_map.json")
copydoc = fa.load("src/data/navislabs_v6_copy.json")
machine = fa.load("interaction_state_machine.json")
entity_audit = fa.load("navislabs_entity_audit.json")
consistency = fa.load("navislabs_entity_consistency.json")
cfg = json.loads(subprocess.run(["node", os.path.join(ROOT, "scripts", "dump-config.mjs")], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
COPY = spec["onscreen_copy"]
END = spec["format"]["duration_s"]
CHUNKS = timeline["chunks"]

# The founder's final script (V6 brief), verbatim. The film must say exactly this.
SCRIPT = {
    "P1": ["Your people and agents see different truths.", "The truth is scattered across the systems where work happens.", "People rebuild it by hand.", "Agents start without it."],
    "P2": ["Navis turns those signals into one shared understanding.", "Every email, meeting, document and message becomes a signal —", "remembered, connected, and turned into what should happen next."],
    "P3": ["Inside a company, the Navis App is for people.", "It shows what changed —", "and why it matters.", "Every fact has its source, its time, and how fresh it is.", "When something needs a decision, Navis prepares the next step.", "A person decides.", "Then the company acts."],
    "P4": ["The same company's agents use Navis Developer.", "Invite the team.", "Connect once — through MCP, API, SDK or CLI.", "The agent asks —", "and gets the company's context, with sources and freshness.", "Navis isn't the model.", "It supplies the company's truth.", "Every request is checked against its permissions.", "The agent does the work,", "and the run is on record."],
    "P5": ["A solo builder gets a private workspace.", "A team can work together.", "And the work state carries into the next session.", "One company.", "The person and the agent acted on the same event."],
    "P6": ["Same facts.", "Same sources.", "Same freshness.", "One understanding.", "Two ways in."],
    "P7": ["Models change.", "Agents change.", "Tools change.", "What your company knows shouldn't have to start over.", "Company-owned.", "Model-neutral.", "Shared by people and agents."],
    "P8": ["NavisLabs.", "The shared understanding for your organization."],
}
MARKED_PAUSES = {("P1", 0), ("P2", 0), ("P3", 4), ("P3", 5), ("P4", 5), ("P5", 2), ("P7", 2), ("P8", 0)}

RENDERED = set()
for sid in fa.SCENE_IDS:
    RENDERED |= fa.closure(os.path.join(fa.SRC, "scenes", f"{sid}.tsx"))
for f in os.listdir(os.path.join(fa.SRC, "compositions")):
    RENDERED.add(os.path.join(fa.SRC, "compositions", f))
RENDERED.add(os.path.join(fa.SRC, "config", "navisBrand.ts"))
RENDERED = sorted(p for p in RENDERED if p.endswith((".ts", ".tsx")))
VISIBLE = {p: fa.visible_text(p) for p in RENDERED}

ANNOTATIONS = ("note", "about", "provenance", "names_policy", "film_status", "public_website_status", "local_source_status", "in_film", "source", "version")


def data_values(obj):
    """Every string value in the launch-state data except annotations (statuses, notes, sources)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k not in ANNOTATIONS:
                yield from data_values(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from data_values(v)
    elif isinstance(obj, str):
        yield obj


SCREEN_STRINGS = (
    [s for p in RENDERED for s in fa.string_literals(VISIBLE[p])]
    + [v for v in COPY.values() if isinstance(v, str) and v != "(unused)"]
    + [ln["text"] for c in CHUNKS for ln in c["lines"]]
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


dc = fa.strip_comments(fa.read(fa.DEMO_CONTENT))


def const_body(name):
    m = re.search(rf"export const {name}\b([\s\S]*?)(?=\nexport |\Z)", dc)
    return m.group(1) if m else ""


# 0 · narrative ------------------------------------------------------------------------
STALE = ["(?i)already has the answer", "(?i)NavisLabs turns", "(?i)Navis Application", "(?i)same organization's", "One organization", "(?i)keeps its history",
         "(?i)learning loop", "(?i)\\bautonomous", "(?i)confidence percentage", r"\bROI\b", "(?i)\bsavings\b", "(?i)only Navis", "(?i)rolling out", r"(?i)\bNavis[ -]AI\b",
         "(?i)coming soon", "(?i)\\broadmap\\b"]
v = V("narrative")
copy_lines = {c["id"]: [l["text"] for l in c["lines"]] for c in copydoc["chunks"]}
tl_lines = {c["id"]: [l["text"] for l in c["lines"]] for c in CHUNKS}
v.check("the copy source holds the founder's eight chunks word for word", copy_lines == SCRIPT, [k for k in SCRIPT if copy_lines.get(k) != SCRIPT[k]])
v.check("the voice timeline speaks the copy source word for word", tl_lines == SCRIPT, [k for k in SCRIPT if tl_lines.get(k) != SCRIPT[k]])
v.check("the [pause] marks are the script's", {(c["id"], i) for c in copydoc["chunks"] for i, l in enumerate(c["lines"]) if l["pause_after"]} == MARKED_PAUSES)
v.check("chunks play in order P1 → P8", [c["id"] for c in CHUNKS] == list(SCRIPT))
stale_hits = sorted({f"{pat}: {m}" for pat in STALE for m in hits(pat)})
v.check("no stale, forbidden or roadmap copy can reach the screen, the copy or the VO", not stale_hits, stale_hits)
v.check("thesis: One understanding. Two ways in.", copydoc["positioning"]["thesis"] == "One understanding. Two ways in.")
v.done()

# 1 · brand -------------------------------------------------------------------------------
v = V("brand")
v.check("no 'NAVIS AI' / 'Navis-AI' label on screen, in copy or in VO", not hits(r"\bnavis[\s_-]?ai\b", flags=re.I), hits(r"\bnavis[\s_-]?ai\b", flags=re.I))
v.check("no 'Navis Labs' (company is one word: NavisLabs)", not hits(r"\bNavis Labs\b"))
v.check("no repository names as product labels ('Devtool')", not hits(r"\bDevtool\b", "\n".join(SCREEN_STRINGS)))
v.check("company name is NavisLabs", COPY.get("company") == "NavisLabs")
v.check("products are the Navis App and Navis Developer", COPY.get("product.application", "").lower() == "navis app" and COPY.get("product.developer", "").lower() == "navis developer")
v.check("tagline is the website headline", COPY.get("tagline") == "The shared understanding for your organization.")
v.check("approved logo assets exist (mark without tile, dark + light)", all(os.path.isfile(os.path.join(PUBLIC, "images", "brand", f)) for f in ("navislabs-mark-dark.png", "navislabs-mark-light.png")))
v.done()

# 2 · entity ------------------------------------------------------------------------------
v = V("entity")
audited = {e["entity"].split(":", 1)[1].split(".")[0] for e in entity_audit["entities"]}
ids = [data["company"]["id"]] + [x["id"] for k in ("people", "teams", "customers", "projects", "decisions", "commitments", "meetings", "emails", "documents", "repositories", "agents", "runs", "crm_records", "knowledge") for x in data[k]]
ids += [data["developer_workspace"]["solo"]["id"]] + [x["id"] for x in data["engineering_context"]["issues"] + data["engineering_context"]["code"]]
missing = [i for i in ids if i not in audited]
v.check("every launch-state entity has an entity-audit row", not missing, missing)
v.check("every row has a known provenance", all(e["real_or_synthetic"] in ("REAL_AUTHORIZED", "REAL_PUBLIC_PRODUCT", "SYNTHETIC", "REAL_PERSON", "REAL_COMPANY") for e in entity_audit["entities"]))
shown_unauth = [e["entity"] for e in entity_audit["entities"] if not e["authorized_for_public_video"] and e["scenes"]]
v.check("nothing unauthorized appears in a scene", not shown_unauth, shown_unauth)
restricted = hits(r"mulayam|digantara", flags=re.I)
v.check("restricted names (Mulayam, Digantara) appear nowhere on screen, in copy, VO or demo values", not restricted, restricted)
emails = sorted(set(re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", "\n".join(SCREEN_STRINGS))))
v.check("emails are the founder's own or reserved example domains", all(e == "abhishek@navislabs.in" or e.endswith("@example.com") or e.endswith(".example") for e in emails), emails)
v.check("customer, opportunity, knowledge, issue and repository records are SYNTHETIC", all(x["provenance"] == "SYNTHETIC" for x in data["customers"] + data["crm_records"] + data["knowledge"] + data["engineering_context"]["issues"] + data["engineering_context"]["code"]))
SECRET = r"navis_(?!<)[A-Za-z0-9]{6,}_[A-Za-z0-9]{12,}|\bsk-[A-Za-z0-9]{20,}|sk_live_[A-Za-z0-9]+|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|ELEVENLABS_API_KEY\s*[=:]\s*['\"]?[A-Za-z0-9]{16,}|xi-api-key\s*[:=]\s*['\"]?[A-Za-z0-9]{16,}"
scan = fa.ts_files() + [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".json")] + [os.path.join(ROOT, "scripts", f) for f in os.listdir(os.path.join(ROOT, "scripts"))] + [os.path.join(fa.SRC, "data", f) for f in os.listdir(os.path.join(fa.SRC, "data"))]
leaks = [fa.rel(p) for p in scan if os.path.isfile(p) and re.search(SECRET, fa.read(p))]
v.check("no API keys, tokens or private keys in src, scripts or JSON", not leaks, leaks)
gi = fa.read(os.path.join(ROOT, ".gitignore")) if os.path.isfile(os.path.join(ROOT, ".gitignore")) else ""
v.check(".env is git-ignored", ".env" in gi)
v.done()

# 3 · product_claim ------------------------------------------------------------------------
v = V("product_claim")
legend = set(surfaces["claim_status_legend"])
v.check("every surface has a known claim status", all(s["claim_status"] in legend for s in surfaces["surfaces"]))
v.check("launch-state surfaces are marked LAUNCH_STATE", all(s["claim_status"] == "LAUNCH_STATE" for s in surfaces["surfaces"] if s["id"] in ("integrations.launch_state", "app.crm", "app.engineering", "app.knowledge")))
d = COPY.get("disclosure", "").lower()
v.check("end-card disclosure: launch configuration, fictional demo data, private preview", all(k in d for k in ("launch configuration", "fictional", "demo", "private preview")), COPY.get("disclosure"))
v.check("SDK shown as not on npm", "not on npm" in SCREEN_TEXT)
pub = hits(r"npm install @navis/sdk|npm i @navis/sdk|pip install navis", "\n".join(VISIBLE.values()))
v.check("no public-registry install shown as working", not pub, pub)
v.check("the run's outcome is 'Not judged'", data["runs"][0]["outcome"] == "Not judged")
v.check("no invented economics on run steps", not [k for r_ in data["runs"] for st in r_.get("steps", []) for k in st if k in ("tokens", "cost", "latency", "model")])
v.check("no amounts on the CRM record", not re.search(r"amount|\$|₹|\barr\b|revenue|\d[\d,]*\s*(?:k|m|usd|inr)\b", "\n".join(data_values(data["crm_records"])), re.I))
v.check("no 'Projects' page in the Console", '"Projects"' not in VISIBLE.get(os.path.join(fa.SRC, "ui", "developer", "Console.tsx"), ""))
v.check("central policy engine not shown as live", not hits(r"policy engine (?:is )?(?:enabled|active|live)|policies enforced", flags=re.I))
v.check("Navis is never presented as the model", not hits(r"Navis (is|=) (the|a) (model|LLM)", "\n".join(SCREEN_STRINGS), re.I))
across = const_body("ACROSS_SYSTEMS").split("= [", 1)[-1]  # the rows, without the type annotation
v.check("after the reply only the Gmail action is done; other systems show who owns the next step", across.count('status: "done"') == 1 and across.count("owner:") == across.count("system:"))
v.check("Outcome and Learning stay labelled Building / Next", all(k in "\n".join(VISIBLE.values()) for k in ("Building", "Next")))
clients = re.findall(r'name: "([^"]+)", status: "([^"]+)"', fa.read(os.path.join(fa.SRC, "config", "navisBrand.ts")))
v.check("only Claude Code is shown as live verified", [n for n, s_ in clients if s_ == "live verified"] == ["Claude Code"], clients)
v.check("placeholders only for credentials", "NAVIS_API_KEY" in SCREEN_TEXT and "navis_<prefix>_<secret>" in SCREEN_TEXT)
v.done()

# 4 · integration (film launch state) ------------------------------------------------------------
v = V("integration")
launch = data["integrations"]["FILM_LAUNCH_INTEGRATIONS"]
lids = [x["id"] for x in launch]
brand_src = fa.read(os.path.join(fa.SRC, "config", "navisBrand.ts"))
registry = re.findall(r'\{ id: "(\w+)", label:', brand_src)
v.check("thirteen systems in the film's launch state", len(lids) == 13 and len(set(lids)) == 13, lids)
v.check("the film's connector set is the launch state (demoContent LIVE_IDS)", data["integrations"]["connected"] == lids)
v.check("every launch-state system has a brand mark", set(lids) <= set(registry), sorted(set(lids) - set(registry)))
v.check("every system is CONNECTED in the film", all(x["film_status"].startswith("CONNECTED") for x in launch))
v.check("every system records its public-website and local-source status", all(x.get("public_website_status") and x.get("local_source_status") for x in launch))
web = os.path.expanduser("~/Desktop/navis-labs-website/components/site/logos.tsx")
if os.path.isfile(web):  # read-only: the website repository is never modified
    src = open(web).read()
    status = {m.group(1): m.group(2) for m in re.finditer(r'id: "(\w+)",\s*label: "[^"]+",\s*status: "(\w+)"', src)}
    alias = {"calendar": "googlecalendar", "meet": "googlemeet", "drive": "googledrive", "docs": "googledocs"}
    word = {"supported": "Supported", "soon": "Coming soon"}
    mism = [x["id"] for x in launch if status.get(alias.get(x["id"], x["id"])) and word[status[alias.get(x["id"], x["id"])]] != x["public_website_status"]]
    v.check("recorded website statuses match the website source today", not mism, mism)
v.check("every system has a semantic", all(i in data["integrations"]["semantics"] for i in lids))
NO_RECORD = {"hubspot": "HubSpot", "microsoft365": "Microsoft 365", "zoom": "Zoom"}
EVIDENCE_CONSTS = ["OPENING_SIGNALS", "HAND_COPIES", "PRIORITIES", "ACME_SIGNALS", "SYSTEM_FACTS", "FLOW_SIGNALS", "RESULT_ROWS", "AGENT_LINES", "ACME_DRAFT", "ACME_CONTEXT", "ACROSS_SYSTEMS"]
fab = [f"{name}: {i}" for name in EVIDENCE_CONSTS for i, label in NO_RECORD.items() if re.search(rf'"{i}"|\b{re.escape(label)}\b', const_body(name))]
v.check("no fabricated evidence from systems without a demo record (HubSpot, Microsoft 365, Zoom)", not fab, fab)
v.check("systems with records carry evidence; the rest are connected infrastructure", all(x["in_film"].startswith("evidence") == (x["id"] not in NO_RECORD) for x in launch))
v.done()

# 5 · interaction ----------------------------------------------------------------------------
v = V("interaction")
for it in machine["interactions"]:
    times = [s["at_s"] for s in it["states"]]
    v.check(f"{it['id']}: states are in time order", times == sorted(times), times)
    if it["cursor"]:
        names_ = [s["state"] for s in it["states"]]
        v.check(f"{it['id']}: before → settle → click → feedback → after", names_ == ["before", "settle", "click", "feedback", "after"], names_)
        gap = round(it["states"][2]["at_s"] - it["states"][1]["at_s"], 3)
        v.check(f"{it['id']}: cursor settles ≥ 0.1 s before the click", gap >= 0.1 - 1e-6, gap)
v.check("cursor has no click ring", machine["cursor_rules"]["ring"] is False and "<circle" not in fa.visible_text(os.path.join(fa.SRC, "components", "Cursor.tsx")))
PRESS = {"click", "approve", "select", "confirm"}
clicks = sorted(e["at"] for e in cfg["SFX_EVENTS"] if e["sfx"] in PRESS)
unheard = [it["id"] for it in machine["interactions"] if it["cursor"] and not any(abs(c - next(s["at_s"] for s in it["states"] if s["state"] == "click")) < 0.05 for c in clicks)]
v.check("every cursor click has a press sound at the same moment", not unheard, unheard)
cursor_clicks = {next(s["at_s"] for s in it["states"] if s["state"] == "click") for it in machine["interactions"] if it["cursor"]} | {cfg["BEAT"][k] for k in ("copy1", "copy2", "copy3")}
blind = [round(e["at"], 2) for e in cfg["SFX_EVENTS"] if e["category"] == "CURSOR CLICK" and not any(abs(e["at"] - c) < 0.06 for c in cursor_clicks)]
v.check("no click sound without a visible click", not blind, blind)
v.done()

# 6 · timeline ---------------------------------------------------------------------------------
v = V("timeline")
scenes = cfg["FILM_SCENES"]
v.check("18 scenes S01–S18 in order", [s["id"] for s in scenes] == fa.SCENE_IDS)
v.check("starts at 0 and ends at the voice-derived length", scenes[0]["from"] == 0 and abs(scenes[-1]["to"] - END) < 1e-6)
v.check("scenes are contiguous", all(abs(a["to"] - b["from"]) < 1e-6 for a, b in zip(scenes, scenes[1:])))
v.check("length set by the founder's performance: 115–126 s", 115 <= END <= 126, END)
v.check("frames = duration × 30", cfg["FILM_FRAMES"] == round(END * 30) == spec["format"]["frames"], cfg["FILM_FRAMES"])
short = [s["id"] for s in scenes if s["to"] - s["from"] < 1.5]
v.check("every scene holds at least 1.5 s", not short, short)
bad_t = [a["id"] for a, b in zip(scenes, scenes[1:]) if a["transitionOut"]["frames"] > min(round((a["to"] - a["from"]) * 30), round((b["to"] - b["from"]) * 30)) / 2]
v.check("transitions are at most half of each neighbour", not bad_t, bad_t)
v.check("all beats lie within the film", all(0 <= t <= END for t in cfg["BEAT"].values()))
v.check("all typing ends within the film", all(t["text"] == "(unused)" or t["start"] + len(t["text"]) / t["cps"] <= END for t in cfg["TYPING"].values()))
v.done()

# 7 · voice_audio --------------------------------------------------------------------------------


def wav_info(rel):
    p = os.path.join(PUBLIC, rel)
    if not os.path.isfile(p):
        return None
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate(), w.getframerate(), w.getnchannels()


v = V("voice_audio")
VA = {c["id"]: c for c in analysis["chunks"]}
infos = {c["id"]: wav_info(c["file"]) for c in CHUNKS}
v.check("eight final founder chunks present as 48 kHz WAV", all(i and i[1] == 48000 for i in infos.values()))
v.check("the founder's original files are kept (public/voiceover/source/v6)", all(os.path.isfile(os.path.join(PUBLIC, "voiceover", "source", "v6", f"{k}.mp3")) for k in SCRIPT))
v.check("chunks are not sped up or trimmed (WAV length = measured length)", all(abs(infos[k][0] - VA[k]["duration_s"]) < 0.02 for k in infos if infos[k]))
gaps = [round(b["speech_start_s"] - a["speech_end_s"], 2) for a, b in zip(CHUNKS, CHUNKS[1:])]
v.check("speech never overlaps between chunks (≥ 0.4 s breath)", all(g >= 0.4 for g in gaps), gaps)
marked = [(c["id"], i, round(c["lines"][i + 1]["start_s"] - c["lines"][i]["end_s"], 2)) for c in CHUNKS for i, l in enumerate(c["lines"][:-1]) if l["pause_after"]]
v.check("every [pause] is a real silence of ≥ 1 s in the performance", all(p_ >= 1.0 for *_, p_ in marked), marked)
slots = {r_["id"]: r_ for r_ in audio["voiceover"]}
v.check("audio slots start where the timeline places each chunk", all(abs(slots[c["id"]]["start_s"] - c["at_s"]) < 1e-6 for c in CHUNKS))
v.check("each chunk plays to its end before its slot closes", all(slots[c["id"]]["ceiling_s"] >= c["at_s"] + c["duration_s"] - 1e-6 for c in CHUNKS))
sp = audio["speech"]
v.check("speech windows are ordered and never overlap (ducking follows the real voice)", all(a["to_s"] <= b["from_s"] + 1e-6 for a, b in zip(sp, sp[1:])))
v.check("key lines duck deeper (8 key lines marked)", sum(1 for s_ in sp if s_["key"]) == 8 and audio["music"]["duck_key_line_db"] < audio["music"]["duck_under_vo_db"])
cats = set(cfg["SFX_CATEGORIES"])
v.check("every SFX event is one of the 15 categories", all(e["category"] in cats for e in cfg["SFX_EVENTS"]))
in_sil = [f"{e['category']} @ {e['at']:.2f}" for e in cfg["SFX_EVENTS"] for w in cfg["SFX_SILENCES"] if w["from"] <= e["at"] < w["to"]]
v.check("no SFX inside the deliberate silences", not in_sil, in_sil)
key_sfx = [f"{e['category']} @ {e['at']:.2f}" for e in cfg["SFX_EVENTS"] for s_ in sp if s_["key"] and s_["from_s"] <= e["at"] <= s_["to_s"] and e["category"] != "KEYBOARD"]
v.check("no SFX accents under the key lines (keystrokes excepted)", not key_sfx, key_sfx)
sec_ = audio["music"]["sections"]
v.check("music sections cover the whole film contiguously", sec_[0]["from_s"] == 0 and abs(sec_[-1]["to_s"] - END) < 1e-6 and all(abs(a["to_s"] - b["from_s"]) < 1e-6 for a, b in zip(sec_, sec_[1:])))
ts_ = wav_info(audio["music"]["temp"])
v.check("temp score runs the film's length", ts_ is not None and abs(ts_[0] - END) < 0.1, ts_)
v.check("silent end after the last word", audio["music"]["dips"][-1]["db"] <= -90 and abs(audio["music"]["dips"][-1]["to_s"] - END) < 1e-6)
v.check("SFX library files exist (temp)", all(os.path.isfile(os.path.join(PUBLIC, x["temp"])) for x in audio["sfx"]["library"].values()))
v.done()

# 8 · visual_asset -------------------------------------------------------------------------------
v = V("visual_asset")
ASSET = re.compile(r"^/?[\w./-]+\.(png|jpe?g|svg|webp|gif|wav|mp3|m4a|woff2?|ttf|otf|mp4)$", re.I)
refs = sorted({s.lstrip("/") for p in fa.ts_files() for s in fa.string_literals(fa.visible_text(p)) if ASSET.match(s)})
gone = [r_ for r_ in refs if not os.path.isfile(os.path.join(PUBLIC, r_))]
v.check(f"every literal asset path in src exists in public/ ({len(refs)} paths)", not gone, gone)
logos = re.findall(r'"((?:logos?|images)/[^"]+)"', brand_src)
v.check("every integration logo and brand mark exists", all(os.path.isfile(os.path.join(PUBLIC, x)) for x in logos), [x for x in logos if not os.path.isfile(os.path.join(PUBLIC, x))])
v.done()

# 9 · data_consistency ---------------------------------------------------------------------------
v = V("data_consistency")
people, cust = data["people"], data["customers"][0]
crm, kn, iss, code = data["crm_records"][0], data["knowledge"][0], data["engineering_context"]["issues"][0], data["engineering_context"]["code"][0]
literals = ([p["name"] for p in people] + [p["email"] for p in people] + [p["mac_host"] for p in people if p.get("mac_host")]
            + [cust["name"], cust["caps"], cust["slug"], cust["renewal_was"], cust["renewal_now"], cust["renewal_was_iso"], cust["renewal_now_iso"]]
            + [e["date_iso"] for e in data["emails"]] + [d_["date_iso"] for d_ in data["decisions"]] + [data["application_workspace"]["date_iso"]]
            + [x["ticket"] for x in data["projects"] if x.get("ticket")] + [x["file"] for x in data["projects"] if x.get("file")]
            + [r_["id"] for r_ in data["runs"]] + [r_["task"] for r_ in data["runs"]] + [d_["short"] for d_ in data["decisions"]] + [e["subject"] for e in data["emails"]]
            + [r_["name"] for r_ in data["repositories"] if r_["name"] != data["company"]["name"]] + [data["developer_workspace"]["solo"]["name"]]
            + [crm["name"], kn["title"], iss["title"], code["path"], data["team_workstate"]["open"], data["team_workstate"]["decision"]])
WORD = [p["first"] for p in people if p["provenance"] == "SYNTHETIC"] + [cust["short"]]
ALLOWED = {fa.DEMO_CONTENT, os.path.join(fa.SRC, "config", "navisBrand.ts")}
found = set()
for p in fa.ts_files():
    if p in ALLOWED or p.endswith("evidence.ts"):
        continue
    code_txt = fa.visible_text(p)
    found |= {f"{fa.rel(p)}: {val}" for val in literals if val and val in code_txt}
    found |= {f"{fa.rel(p)}: {w}" for w in WORD if re.search(rf"\b{re.escape(w)}\b", code_txt)}
v.check("no entity value hardcoded in components (all from the launch-state file)", not found, sorted(found))
run = data["runs"][0]
ts_steps = [st["at"] for st in run["steps"]]
secs = lambda t: int(t[:2]) * 3600 + int(t[3:5]) * 60 + int(t[6:8])  # noqa: E731
mins, ss = re.match(r"(\d+)m (\d+)s", run["duration"]).groups()
v.check("run steps are in order and fit the run's duration", ts_steps == sorted(ts_steps) and secs(ts_steps[-1]) - secs(ts_steps[0]) <= int(mins) * 60 + int(ss))
v.check("'Updates' tile is 0 (the product always reports 0)", data["application_workspace"]["glance"]["updates"] == 0)
v.check("same customer, decision and commitment in both products", all(consistency["checks"][k] for k in ("customer_in_both_products", "decision_in_both_products", "commitment_in_both_products")))
v.check("one coherent run: the agent's task is the run's task", re.search(r"export const AGENT_TASK = RUN\.task", dc) is not None)
v.check("the CRM close date is the customer's old renewal date (one consistent story)", crm["close_date"] == cust["renewal_was"])
v.check("the GitHub file is the workflow the agent edits", code["path"] == next(x["file"] for x in data["projects"] if x.get("file")))
v.done()

# 10 · captions -----------------------------------------------------------------------------------
v = V("captions")
srt = os.path.join(ROOT, "captions", "navislabs-v6.srt")
vtt = os.path.join(ROOT, "captions", "navislabs-v6.vtt")
cj = os.path.join(PUBLIC, "captions", "navislabs-v6-captions.json")
v.check("SRT, VTT and word-level JSON exist", all(os.path.isfile(p) for p in (srt, vtt, cj)))
if os.path.isfile(srt):
    blocks = [b.split("\n") for b in open(srt).read().strip().split("\n\n")]
    joined = re.sub(r"\s+", " ", " ".join(" ".join(b[2:]) for b in blocks))
    v.check("captions read exactly the script", joined == " ".join(l for c in SCRIPT.values() for l in c))
    to_s = lambda x: int(x[0:2]) * 3600 + int(x[3:5]) * 60 + int(x[6:8]) + int(x[9:12]) / 1000  # noqa: E731
    times = [(to_s(b[1].split(" --> ")[0]), to_s(b[1].split(" --> ")[1])) for b in blocks]
    speech = [(ln["start_s"], ln["end_s"]) for c in CHUNKS for ln in c["lines"]]
    off = [round(a, 2) for a, _ in times if not any(s_ - 0.06 <= a <= e_ + 0.06 for s_, e_ in speech)]
    v.check("every cue starts on spoken words (from the measured voice)", not off, off)
    v.check("cues are ordered and never overlap", all(a[1] <= b[0] + 1e-6 and a[0] < a[1] for a, b in zip(times, times[1:])))
if os.path.isfile(cj):
    words = json.load(open(cj))
    v.check("word timings are monotonic", all(a["startMs"] <= b["startMs"] for a, b in zip(words, words[1:])))
v.check("VTT cues sit low in frame (off the UI)", os.path.isfile(vtt) and "line:88%" in open(vtt).read())
v.done()

report = {"about": "V6 film validators (scripts/validate-film.py). All must pass.", "all_pass": all(r_["pass"] for r_ in results.values()),
          "summary": {k: r_["pass"] for k, r_ in results.items()}, "validators": results}
with open(os.path.join(ROOT, "navislabs_v6_validation_report.json"), "w") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
    f.write("\n")
for k, r_ in results.items():
    fails = [c for c in r_["checks"] if not c["pass"]]
    print(f"{'PASS' if r_['pass'] else 'FAIL'}  {k:<17} {len(r_['checks']) - len(fails)}/{len(r_['checks'])}")
    for c in fails:
        print(f"      ✗ {c['check']}: {str(c.get('detail', ''))[:300]}")
sys.exit(0 if report["all_pass"] else 1)
