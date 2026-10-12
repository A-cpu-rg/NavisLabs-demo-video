"""Static analysis of the film source, shared by build-audits.py and
validate-film.py. Read-only: it parses src/ and the generated JSONs.

  entity_scenes()   entity id -> scenes whose import closure reads it
  visible_text(p)   a TS/TSX file with comments removed (what can reach the screen)
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
DATA_PATH = os.path.join(SRC, "data", "navislabs_v8_launch_state.json")
DEMO_CONTENT = os.path.join(SRC, "ui", "demoContent.ts")
SCENE_IDS = [f"S{i:02d}" for i in range(1, 19)]


def load(name):
    with open(os.path.join(ROOT, name)) as f:
        return json.load(f)


def demo_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def ts_files():
    out = []
    for d, _, files in os.walk(SRC):
        for f in files:
            if f.endswith((".ts", ".tsx")):
                out.append(os.path.join(d, f))
    return sorted(out)


def rel(p):
    return os.path.relpath(p, ROOT)


def read(p):
    with open(p) as f:
        return f.read()


_STR = r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|`(?:[^`\\]|\\.)*`'


def strip_comments(src):
    """Removes // and /* */ comments (and JSX {/* */}), keeping string literals intact."""
    out, i, n = [], 0, len(src)
    tok = re.compile(_STR + r"|/\*.*?\*/|//[^\n]*", re.S)
    for m in tok.finditer(src):
        out.append(src[i:m.start()])
        t = m.group(0)
        if t.startswith("/*"):
            out.append("\n" * t.count("\n"))
        elif t.startswith("//"):
            # A "//" right after ":" is a URL inside JSX text, not a comment.
            out.append(t if src[max(0, m.start() - 1)] == ":" else "")
        else:
            out.append(t)
        i = m.end()
    out.append(src[i:n])
    return re.sub(r"\{\s*\}", "", "".join(out))


def visible_text(p):
    return strip_comments(read(p))


def string_literals(code):
    return [m.group(0)[1:-1] for m in re.finditer(_STR, code)]


# ---- import graph -----------------------------------------------------------

def resolve(frm, spec):
    base = os.path.normpath(os.path.join(os.path.dirname(frm), spec))
    for cand in (base, base + ".ts", base + ".tsx", os.path.join(base, "index.ts"), os.path.join(base, "index.tsx")):
        if os.path.isfile(cand):
            return cand
    return None


def imports_of(p):
    code = read(p)
    out = {}
    for m in re.finditer(r'import\s+(?:type\s+)?([\s\S]*?)\s+from\s+"(\.[^"]+)"', code):
        target = resolve(p, m.group(2))
        if target:
            names = re.findall(r"\b(\w+)\b", m.group(1).replace("type ", ""))
            out.setdefault(target, set()).update(names)
    for m in re.finditer(r'export\s+\*\s+from\s+"(\.[^"]+)"|export\s+\{[^}]*\}\s+from\s+"(\.[^"]+)"', code):
        target = resolve(p, m.group(1) or m.group(2))
        if target:
            out.setdefault(target, set())
    return out


def closure(p, skip_dirs=("config", "data")):
    seen, stack = set(), [p]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for t in imports_of(cur):
            parts = os.path.relpath(t, SRC).split(os.sep)
            if parts[0] in skip_dirs:
                continue
            if t.endswith(os.path.join("ui", "demoContent.ts")):
                continue
            stack.append(t)
    return seen


# ---- demoContent: which entities each exported constant carries -------------

BASE = {
    "COMPANY": ["org_navislabs"], "USER": ["p_abhishek"], "ENGINEER": ["p_arjun"], "CONTACT": ["p_meera"],
    "SOLO": ["p_solo"], "CUSTOMER": ["c_kaveri"], "C": ["c_kaveri"], "PROJECT": ["pr_sso"],
    "WORKFLOW_RAW": ["pr_renewal_workflow"], "WORKFLOW": ["pr_renewal_workflow"], "REPO": ["r_navislabs"],
    "SOLO_REPO": ["r_riya"], "DECISION": ["d_annual_terms"], "COMMITMENT": ["m_revised_terms"],
    "COMMITMENT_DATE": ["m_revised_terms"], "CHANNEL": ["m_revised_terms"], "BOARD": ["m_board_metrics"],
    "RENEWAL_CALL": ["mt_renewal_call"], "MOVED_ON": ["mt_renewal_call"], "EMAIL": ["e_move_renewal"],
    "ORDER_FORM": ["doc_order_form"], "ACCOUNT_PLAN": ["doc_account_plan"], "PLAN_FACT": ["doc_account_plan"],
    "SSO_SPEC": ["doc_sso_spec"], "AGENT": ["a_claude_code"], "RUNS": ["run_7c2e91a0", "run_3f9a1d27"],
    "RUN": ["run_7c2e91a0"], "DEV_WORKSPACE": ["p_abhishek", "p_arjun", "org_navislabs"],
    "SOLO_WORKSPACE": ["w_riya", "p_solo", "r_riya"], "APP_WORKSPACE": ["org_navislabs", "p_abhishek"],
    "CRM": ["crm_kaveri_opportunity"], "KNOWLEDGE": ["kn_renewal_playbook"], "JIRA": ["eng_kvr_142"],
    "CODE": ["code_kaveri_renewal"], "TEAM_STATE": ["p_abhishek", "r_navislabs"],
}
HELPERS = {"person", "firstOf"}
ID_RE = re.compile(r'"((?:p|c|pr|d|m|mt|e|doc|r|a|t|w|org)_[a-z0-9_]+)"')


def demo_constants():
    """Top-level declaration in demoContent.ts -> set of entity ids it carries."""
    code = strip_comments(read(DEMO_CONTENT))
    decls = list(re.finditer(r"^(?:export\s+)?(?:const|function)\s+(\w+)", code, re.M))
    bodies = {}
    for i, m in enumerate(decls):
        end = decls[i + 1].start() if i + 1 < len(decls) else len(code)
        bodies[m.group(1)] = code[m.end():end]
    ents = {k: set(BASE.get(k, [])) for k in bodies}
    for k, body in bodies.items():
        if k in HELPERS:
            continue
        ents[k].update(ID_RE.findall(body))
        if re.search(r"data\.teams\b", body):
            ents[k].update(t["id"] for t in demo_data()["teams"])
    changed = True
    while changed:
        changed = False
        for k, body in bodies.items():
            if k in HELPERS or k in BASE:
                continue
            for other in bodies:
                if other != k and other not in HELPERS and re.search(rf"\b{other}\b", body):
                    before = len(ents[k])
                    ents[k] |= ents[other]
                    changed |= len(ents[k]) != before
    return {k: v for k, v in ents.items() if k not in HELPERS}


DEMO_FIELDS = {
    "org": ["org_navislabs"], "repo": ["r_navislabs"], "macUser": ["p_abhishek"], "macHost": ["p_abhishek"],
    "user": ["p_abhishek"], "userFirst": ["p_abhishek"], "userEmail": ["p_abhishek"], "owner": ["p_abhishek"],
    "customer": ["c_kaveri"], "contact": ["p_meera"], "contactEmail": ["p_meera"],
}


def file_entities(p, consts):
    """Entities a single file reads (through demoContent, DEMO, or the JSON directly)."""
    code = strip_comments(read(p))
    out = set()
    for target, names in imports_of(p).items():
        if target == DEMO_CONTENT:
            for n in names:
                if n in consts and len(re.findall(rf"\b{n}\b", code)) > 1:
                    out |= consts[n]
    for f in re.findall(r"\bDEMO\.(\w+)", code):
        out.update(DEMO_FIELDS.get(f, []))
    if re.search(r"\bmacPrompt\(", code):
        out.add("p_abhishek")
    if re.search(r'from\s+"[^"]*navislabs_(?:demo_data|v6_launch_state)\.json"', code):
        data = demo_data()
        for coll in set(re.findall(r"\bdata\.(\w+)", code)):
            val = data.get(coll)
            if isinstance(val, list):
                out.update(x["id"] for x in val if isinstance(x, dict) and "id" in x)
            elif isinstance(val, dict) and "id" in val:
                out.add(val["id"])
        out.update(ID_RE.findall(code))
    return out


def entity_scenes():
    consts = demo_constants()
    per_file = {p: file_entities(p, consts) for p in ts_files()}
    scenes = {}
    for sid in SCENE_IDS:
        sp = os.path.join(SRC, "scenes", f"{sid}.tsx")
        for f in closure(sp):
            for e in per_file.get(f, ()):
                scenes.setdefault(e, set()).add(sid)
    return {e: sorted(s) for e, s in scenes.items()}, per_file


def scenes_using(pattern):
    """Scenes whose import closure contains code matching a regex (comments removed)."""
    rx = re.compile(pattern)
    hits = {p for p in ts_files() if rx.search(strip_comments(read(p)))}
    return sorted(sid for sid in SCENE_IDS if closure(os.path.join(SRC, "scenes", f"{sid}.tsx")) & hits)


def const_scenes():
    """demoContent constant -> scenes whose closure has a file that reads it."""
    consts = demo_constants()
    users = {}
    for p in ts_files():
        if p == DEMO_CONTENT:
            continue
        code = strip_comments(read(p))
        for target, names in imports_of(p).items():
            if target == DEMO_CONTENT:
                for n in names:
                    if n in consts and len(re.findall(rf"\b{n}\b", code)) > 1:
                        users.setdefault(n, set()).add(p)
    out = {}
    for sid in SCENE_IDS:
        cl = closure(os.path.join(SRC, "scenes", f"{sid}.tsx"))
        for n, files in users.items():
            if cl & files:
                out.setdefault(n, set()).add(sid)
    return {k: sorted(v) for k, v in out.items()}


def integration_scenes(live_ids, expanding_ids):
    """Integration id -> scenes that show it (demo constants citing it, or files listing a whole set)."""
    code = strip_comments(read(DEMO_CONTENT))
    decls = list(re.finditer(r"^(?:export\s+)?(?:const|function)\s+(\w+)", code, re.M))
    cs = const_scenes()
    out = {i: set() for i in list(live_ids) + list(expanding_ids)}
    for k, m in enumerate(decls):
        body = code[m.end():decls[k + 1].start() if k + 1 < len(decls) else len(code)]
        for i in out:
            if re.search(rf'"{i}"', body):
                out[i] |= set(cs.get(m.group(1), []))
    sets = {r"\b(LIVE_IDS|LIVE_CURRENT|INTEGRATIONS)\b": live_ids, r"\b(EXPANDING_IDS|FUTURE_CONNECTED|ROADMAP_INTEGRATIONS)\b": expanding_ids}
    for p in ts_files():
        if p == DEMO_CONTENT or os.path.relpath(p, SRC).split(os.sep)[0] == "config" or p.endswith("Integrations.tsx") or p.endswith("evidence.ts"):
            continue
        c = strip_comments(read(p))
        lits = set(re.findall(r'"([a-z0-9]+)"', c))
        for rx, ids in sets.items():
            hit = bool(re.search(rx, c))
            for i in ids:
                if hit or i in lits:
                    for sid in SCENE_IDS:
                        if p in closure(os.path.join(SRC, "scenes", f"{sid}.tsx")):
                            out[i].add(sid)
    return {k: sorted(v) for k, v in out.items()}


# ---- syllables (pace checks, caption timing) ------------------------------
def syllables(text):
    n = 0
    for w in re.findall(r"[A-Za-z][A-Za-z'’-]*", text):
        if re.fullmatch(r"[A-Z]{2,4}", w):  # spelled acronym: MCP, API, SDK, CLI
            n += sum(3 if c == "W" else 1 for c in w)
            continue
        for part in re.split(r"[-]", w.lower().replace("’", "'")):
            part = part.replace("'s", "s")
            if not part:
                continue
            groups = re.findall(r"[aeiouy]+", part)
            k = len(groups)
            if part.endswith("e") and not part.endswith(("le", "ee")) and k > 1:
                k -= 1
            if part.endswith("ed") and not part.endswith(("ted", "ded")) and k > 1:
                k -= 1
            n += max(1, k)
    return n
