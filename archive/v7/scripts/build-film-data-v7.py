#!/usr/bin/env python3
"""Builds the V6 data for the NavisLabs launch film. THE FOUNDER'S VOICE IS THE MASTER CLOCK.

Reads:
  src/data/navislabs_v7_copy.json          the eight approved voice chunks (P1–P8) + on-screen copy
  navislabs_v6_voice_analysis.json         measured audio: each line's start/end inside its chunk
  src/data/navislabs_v7_launch_state.json  every entity, record and connector status (film-only)
Writes (project root):
  navislabs_v7_voice_timeline.json         where each chunk, line and word lands in the film
  navislabs_v7_film_spec.json              scenes, transitions, shots, copy, beats, typing, format
  navislabs_v7_audio_map.json              VO chunks, speech windows (ducking), music arc, SFX library
  navislabs_v7_product_surface_map.json    surfaces and claim status (incl. LAUNCH_STATE)
  interaction_state_machine.json           every control: before → settle → click → feedback → after
  navislabs_audio_design_plan.json         per scene: VO, music, SFX, ducking, silence

Chunks are placed back to back with breathing room between them (GAP_AFTER, measured from
the end of one chunk's speech to the start of the next); nothing inside a chunk is edited,
sped up or trimmed. Every beat below is a word or line of that performance.
Run: npm run data:build
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
FPS = 30
COPYDOC = fa.load("src/data/navislabs_v7_copy.json")
VA = {c["id"]: c for c in fa.load("navislabs_v6_voice_analysis.json")["chunks"]}
DATA = fa.load("src/data/navislabs_v7_launch_state.json")
COPY = COPYDOC["onscreen_copy"]
IDS = [c["id"] for c in COPYDOC["chunks"]]
P, PP, D, R, F, FUT, LS_ = "PROVEN", "PRIVATE_PREVIEW", "DESIGNED", "ROADMAP", "FILM_SIMULATION", "FUTURE_STATE", "LAUNCH_STATE"

# ------------------------------------------------------------------ the master clock
LEAD = 0.6  # silence before the first word
GAP_AFTER = {  # speech end → next speech start (s): breath, reveal, result, cut
    "P1": 1.05,  # black, then "Navis" on the mark
    "P2": 0.85,  # the pipeline lands; the company opens
    "P3": 2.20,  # the reply is sent; the same event across the company's systems
    "P4": 0.90,  # the run detail reads
    "P5": 0.65,  # "One company." is already on screen
    "P6": 1.15,  # "Two ways in." lands before the cut
    "P7": 0.85,  # everything stops for the name
}
HOLD = 1.4  # after the last word: the end card holds, then black

AT = {}
t = LEAD - VA["P1"]["speech_start_s"]
for i, cid in enumerate(IDS):
    AT[cid] = round(t, 3)
    if i + 1 < len(IDS):
        nxt = IDS[i + 1]
        t = AT[cid] + VA[cid]["speech_end_s"] + GAP_AFTER[cid] - VA[nxt]["speech_start_s"]
END = round(math.ceil((AT["P8"] + VA["P8"]["speech_end_s"] + HOLD) * FPS) / FPS, 3)
FRAMES = round(END * FPS)


def LS(c, i):
    return round(AT[c] + VA[c]["lines"][i]["start_s"], 3)


def LE(c, i):
    return round(AT[c] + VA[c]["lines"][i]["end_s"], 3)


def norm(w):
    return re.sub(r"[^\w'’-]", "", w).lower()


def words(c, i):
    """(word, start, end) for line i of chunk c.

    The line's speech bursts (gaps ≥ 0.15 s) are matched to contiguous groups of
    words by syllable count (a small DP), so a word never straddles a real pause
    ("Connect once — | through MCP, | API, | SDK | or | CLI."); inside a burst,
    syllables are spread over its voiced time."""
    line = VA[c]["lines"][i]
    a, b = line["start_s"], line["end_s"]
    voiced = [(max(s_, a), min(e_, b)) for s_, e_ in VA[c]["segments"] if e_ > a and s_ < b]
    bursts = []
    for s_, e_ in voiced:
        if bursts and s_ - bursts[-1][1] < 0.15:
            bursts[-1] = (bursts[-1][0], e_)
        else:
            bursts.append((s_, e_))
    raw = line["text"].split()
    toks, punct = [], []  # punct[k]: word k ends a phrase (comma, dash, full stop …)
    for w in raw:
        if w == "—":
            if punct:
                punct[-1] = True
            continue
        toks.append(w)
        punct.append(bool(re.search(r"[,.;:?!]$", w)))
    syl = [max(1, fa.syllables(w)) for w in toks]
    n, m = len(toks), len(bursts)
    groups = None
    if 1 < m <= n:
        rate = sum(e_ - s_ for s_, e_ in bursts) / sum(syl)
        INF = float("inf")
        cost = [[INF] * (n + 1) for _ in range(m + 1)]
        back = [[0] * (n + 1) for _ in range(m + 1)]
        cost[0][0] = 0.0
        for g in range(1, m + 1):
            for j in range(g, n - (m - g) + 1):
                for k in range(g - 1, j):
                    if cost[g - 1][k] == INF:
                        continue
                    want = sum(syl[k:j]) * rate
                    have = bursts[g - 1][1] - bursts[g - 1][0]
                    c_ = cost[g - 1][k] + math.log(max(have, 0.05) / max(want, 0.05)) ** 2
                    if j < n:  # a burst that ends on punctuation is the founder's own phrasing
                        c_ += -0.15 if punct[j - 1] else 0.05
                    if c_ < cost[g][j]:
                        cost[g][j], back[g][j] = c_, k
        groups, j = [], n
        for g in range(m, 0, -1):
            k = back[g][j]
            groups.append((k, j))
            j = k
        groups = groups[::-1]
    else:
        groups = [(0, n)]
        bursts = [(a, b)] if m == 0 else [(bursts[0][0], bursts[-1][1])]
    out = []
    for (k, j), (s_, e_) in zip(groups, bursts):
        W_ = sum(syl[k:j])
        acc = 0
        for t_ in range(k, j):
            ws = s_ + (e_ - s_) * acc / W_
            acc += syl[t_]
            we = s_ + (e_ - s_) * acc / W_
            out.append((toks[t_], round(AT[c] + ws, 3), round(AT[c] + we, 3)))
    return out


def W(c, i, word, k=0):
    hits = [s for w, s, _ in words(c, i) if norm(w) == norm(word)]
    assert len(hits) > k, (c, i, word)
    return hits[k]


# ------------------------------------------------------------------ scenes (from the voice)
# id, from, to, transition_out, beat, act
S = [
    ("S01", 0.0, LS("P1", 2) - 0.35, ("none", 0, None), "People and agents see different truths; the truth is scattered", "Problem"),
    ("S02", None, LS("P2", 0) - 0.4, ("none", 0, None), "People rebuild by hand; AI agents start without it", "Problem"),
    ("S03", None, LS("P2", 1) - 0.6, ("wipe", 27, "from-bottom"), "Navis — the mark and its two products", "NavisLabs"),
    ("S04", None, LS("P3", 0) - 0.45, ("fade", 18, None), "Thirteen connected systems → signals → memory → context → intelligence → decision → execution → outcome (building) → learning (next)", "NavisLabs"),
    ("S05", None, LS("P3", 1) - 0.3, ("none", 0, None), "A company opens the Navis App", "Navis App"),
    ("S06", None, LS("P3", 2) - 0.25, ("none", 0, None), "What changed → the customer priority", "Navis App"),
    ("S07", None, LS("P3", 4) - 0.3, ("none", 0, None), "Why it matters: every fact with source, time, freshness → one customer state", "Navis App"),
    ("S08", None, LS("P3", 6) - 0.6, ("none", 0, None), "A decision is needed → Navis prepares the next step → a person decides", "Navis App"),
    ("S09", None, LS("P4", 0) - 0.3, ("wipe", 18, "from-top"), "Approve & send → Gmail accepted → the same event across the company's systems", "Navis App"),
    ("S10", None, LS("P4", 1) - 0.35, ("none", 0, None), "The same company's agents use Navis Developer", "Navis Developer"),
    ("S11", None, LS("P4", 3) - 0.3, ("none", 0, None), "Invite the team → connect once: MCP · API · SDK · CLI", "Navis Developer"),
    ("S12", None, LS("P4", 5) - 0.35, ("none", 0, None), "The agent asks → the company's context, with sources and freshness", "Navis Developer"),
    ("S13", None, LS("P4", 7) - 0.45, ("none", 0, None), "SDK and API; Navis isn't the model", "Navis Developer"),
    ("S14", None, LS("P4", 8) - 0.25, ("none", 0, None), "Every request checked: allowed / own scope / denied", "Navis Developer"),
    ("S15", None, LS("P5", 0) - 0.35, ("none", 0, None), "The work, and the run on record", "Navis Developer"),
    ("S16", None, LS("P5", 3) - 0.65, ("fade", 18, None), "Solo → team → the work state carries over", "Navis Developer"),
    ("S17", None, LS("P7", 0) - 0.5, ("fade", 18, None), "One company: the same event, the same facts — two ways in", "Same company"),
    ("S18", None, END, ("none", 0, None), "Models change; what the company knows stays; NavisLabs", "Moat + ending"),
]
SCENES, prev = [], 0.0
for sid, a, b, tr, beat, act in S:
    a = prev if a is None else a
    fa_, fb = round(a * FPS) / FPS, round(b * FPS) / FPS
    if sid == "S18":
        fb = END
    SCENES.append((sid, round(fa_, 3), round(fb, 3), tr, beat, act))
    prev = fb

# ------------------------------------------------------------------ beats (absolute seconds, from the voice)
B = {}
# P1 · S01–S02
B["truthLabels"] = LS("P1", 0) - 0.45
B["truthPeople"] = W("P1", 0, "people") - 0.1
B["truthAgent"] = W("P1", 0, "agents")
B["truthDiff"] = W("P1", 0, "different")
B["scatter"] = W("P1", 1, "scattered") - 0.05
for k, key in enumerate(["signalDecision", "signalCustomer", "signalCommitment", "signalMeeting", "signalContext", "signalAccount", "signalCrm", "signalJira", "signalKnowledge"]):
    B[key] = B["scatter"] + 0.6 + 0.16 * k
B["tilesSettle"] = B["scatter"] + 1.0
B["problem"] = LE("P1", 1) - 0.2
B["memoryPoint"] = B["memoryLine"] = 0
B["peopleStart"] = LS("P1", 2) - 0.3
B["copy1"], B["copy2"], B["copy3"] = LS("P1", 2) + 0.15, LS("P1", 2) + 0.6, LS("P1", 2) + 1.05
B["agentsStart"] = LS("P1", 3) - 0.05
B["blackout"] = LE("P1", 3) + 0.3
B["taskPreview"] = B["questionCard"] = 0
# P2 · S03–S04
B["logoTile"] = LS("P2", 0) - 0.05  # "Navis" lands on the mark
B["logoWord"] = B["logoTile"] + 0.25
B["logoLine"] = B["logoTile"] + 0.5
B["archApp"] = LE("P2", 0) - 0.2
B["archDev"] = B["archApp"] + 0.3
B["toLight"] = LS("P2", 1) - 0.35
B["iconsIn"] = B["toLight"] + 0.2
B["signalsOut"] = LS("P2", 1) + 0.3
B["roadmapIn"] = B["expandIn"] = 0
B["flowMemory"] = W("P2", 2, "remembered")
B["flowContext"] = W("P2", 2, "connected")
B["understanding"] = B["entitiesIn"] = B["flowContext"]
B["flowIntel"] = W("P2", 2, "turned")
B["intelIn"] = B["flowIntel"]
B["flowDecision"] = W("P2", 2, "what")
B["flowExecution"] = W("P2", 2, "happen")
B["flowOutcome"] = B["flowExecution"] + 0.25
B["flowLearning"] = W("P2", 2, "next")
# P3 · S05–S09
B["orgIn"] = LS("P3", 0) - 0.35
B["appRise"] = W("P3", 0, "Navis") - 0.15
B["glance"] = B["appRise"] + 0.75
B["prioritiesIn"] = LE("P3", 0) + 0.05
B["whatChanged"] = W("P3", 1, "what") - 0.1
B["priorityFocus"] = LE("P3", 1) - 0.2
B["backToCard"] = LE("P3", 1) + 0.05
B["whyClick"] = W("P3", 2, "why")
B["whyOpen"] = B["whyClick"] + 0.1
for k in range(7):
    B[f"evidence{k}"] = LS("P3", 3) + 0.05 + 0.12 * k
B["freshness"] = LS("P3", 3) + 0.85
B["youCanDo"] = B["freshness"] + 0.2
B["explodeIn"] = LS("P3", 3) + 1.45
B["resolveIn"] = B["explodeIn"] + 1.05
B["whyClose"] = LS("P3", 4) - 0.15
B["waiting"] = LS("P3", 4) - 0.1
B["reviewReplyClick"] = W("P3", 4, "decision")
B["drawerOpen"] = B["reviewReplyClick"] + 0.1
B["reviewDraftClick"] = B["reviewReplyClick"] + 0.6
B["preparing"] = B["reviewDraftClick"] + 0.05
B["draftShown"] = max(W("P3", 4, "prepares") + 0.3, B["preparing"] + 0.45)
B["selectStart"] = LE("P3", 4) + 0.15
B["selectEnd"] = B["selectStart"] + 0.45
B["caption"] = 0
B["approveHover"] = LE("P3", 5) - 0.15
B["approveClick"] = LS("P3", 6) - 0.3
B["approved"] = B["approveClick"] + 0.2
B["sending"] = LS("P3", 6) + 0.15
B["gmailAccepted"] = W("P3", 6, "company")
B["replySent"] = W("P3", 6, "acts") + 0.1
B["proofRail"] = B["replySent"] + 0.25
B["acrossIn"] = B["replySent"] + 0.35
# P4 · S10–S15
B["devCut"] = LS("P4", 0) - 0.3
B["devCaption"] = B["devCut"] + 0.05
TASK = DATA["runs"][0]["task"]
task_start, task_cps = LS("P4", 0) + 0.35, 32
B["agentEnter"] = task_start + len(TASK) / task_cps + 0.08
B["agentRead"] = B["agentEnter"] + 0.2
B["agentNeeds"] = B["agentRead"] + 0.3
B["membersIn"] = LS("P4", 1) - 0.35
B["addMember"] = W("P4", 1, "team") - 0.05
B["invited"] = B["addMember"] + 0.2
B["mcpAdd"] = B["invited"] + 0.35  # the cut to the terminal falls in the breath after "Invite the team."
B["mcpAdded"] = B["mcpAdd"] + 0.25
mcp_list_start = B["mcpAdd"] + 0.45
B["mcpList"] = mcp_list_start
B["mcpConnected"] = mcp_list_start + len("claude mcp list") / 40 + 0.15
B["mcpCommand"] = 0
B["connectIn"] = W("P4", 2, "through") - 0.15
B["surfaceMcp"], B["surfaceApi"], B["surfaceSdk"], B["surfaceCli"] = W("P4", 2, "MCP"), W("P4", 2, "API"), W("P4", 2, "SDK"), W("P4", 2, "CLI")
B["contextCall"] = LS("P4", 3) + 0.05
B["contextResult"] = B["contextCall"] + 0.5
B["contextSource"] = W("P4", 4, "sources")
B["contextFresh"] = W("P4", 4, "freshness")
B["agentReason"] = LE("P4", 4) + 0.15
B["sdkIn"] = LS("P4", 5) - 0.35
B["sdkInstalled"] = B["sdkIn"] + 0.55
B["sdkCode"] = B["sdkIn"] + 0.65
B["apiIn"] = LE("P4", 5) + 0.3
B["apiResponse"] = B["apiIn"] + 0.35
B["modelNeutral"] = LS("P4", 6)
B["permIdentity"] = LS("P4", 7) - 0.45
B["permAuthorized"] = LS("P4", 7) + 0.2
B["permOwnScope"] = W("P4", 7, "checked")
B["permDenied"] = W("P4", 7, "against")
B["refusal"] = W("P4", 7, "permissions")
B["agentUses"] = LS("P4", 8) - 0.15
B["agentDone"] = W("P4", 8, "work")
B["runs"] = LS("P4", 9) - 0.1
B["runRow"] = B["runs"] + 0.15
B["runOpen"] = W("P4", 9, "run")
B["runTimeline"] = B["runOpen"] + 0.25
B["runOutcome"] = LE("P4", 9) + 0.2
B["runComplete"] = B["runTimeline"] + 0.15 * 4 + 0.1  # the last step lands; the run reads Completed
# P5 · S16
B["soloIn"] = LS("P5", 0) - 0.35
B["soloPick"] = W("P5", 0, "solo") + 0.25  # "For myself" is chosen as "solo builder" is said
B["soloWorkspace"] = W("P5", 0, "private") - 0.1  # the personal workspace holds ~1 s, through "private workspace."
B["teamIn"] = LS("P5", 1) - 0.1
B["soloCheckpoint"] = LS("P5", 2) - 0.1
B["soloCheckpointOk"] = B["soloCheckpoint"] + 0.55
B["soloDayTwo"] = W("P5", 2, "next") - 0.1
B["soloRestore"] = B["soloDayTwo"] + 0.3
B["soloSections"] = B["soloRestore"] + 0.35
for k in ("dayOne", "dayTwo", "restore", "restoreTask", "restoreDecisions", "restoreOpen", "notChatbot", "notAutomation", "loopIn", "yours", "wordsIn", "collapse"):
    B[k] = 0
# P5–P6 · S17
B["heroIn"] = LS("P5", 3) - 0.35
B["sharedSignal"] = W("P5", 4, "same") - 0.2
B["sameFacts"], B["sameSources"], B["sameFreshness"] = LS("P6", 0), LS("P6", 1), LS("P6", 2)
B["sharedUnderstanding"] = LS("P6", 3)
B["peopleAgents"] = LS("P6", 4)
# P7–P8 · S18
B["modelsChange"], B["agentsChange"], B["toolsChange"] = LS("P7", 0), LS("P7", 1), LS("P7", 2)
B["clientsIn"] = LS("P7", 0) + 0.3
B["staysYours"] = LS("P7", 3) - 0.1
B["recordIn"] = B["staysYours"] + 0.3
B["pillars"] = LS("P7", 4)
B["endLockup"] = LS("P8", 0) - 0.3
B["endTagline"] = LS("P8", 1) - 0.05
B["endProducts"] = B["endUnderstanding"] = B["endTagline"] + 0.9
B["endUrl"] = B["endProducts"] + 0.5
B["fadeOut"] = END - 0.5
BEATS = {k: round(v, 3) for k, v in B.items()}

TYPING = {
    "taskPreview": {"start": 0.0, "text": "(unused)", "cps": 30},
    "agentTask": {"start": round(task_start, 3), "text": TASK, "cps": task_cps},
    "humanEdit": {"start": round(B["selectEnd"] + 0.15, 3), "text": "Happy to walk you through it Thursday.", "cps": 36},
    "mcpList": {"start": round(mcp_list_start, 3), "text": "claude mcp list", "cps": 40},
    "sdkInstall": {"start": round(B["sdkIn"] + 0.05, 3), "text": "npm install ./navis-sdk-0.1.0.tgz", "cps": 75},
}

# ------------------------------------------------------------------ voice timeline (chunks · lines · words)
KEY_LINES = {("P2", 0), ("P3", 5), ("P4", 5), ("P4", 6), ("P6", 3), ("P6", 4), ("P7", 3), ("P8", 0)}
timeline = {"about": "Where the founder's voice lands in the film: each chunk's start, every line and every word (seconds, absolute). Built by scripts/build-film-data-v7.py from navislabs_v6_voice_analysis.json.",
            "duration_s": END, "frames": FRAMES, "lead_s": LEAD, "gap_after_s": GAP_AFTER, "hold_s": HOLD, "chunks": []}
for c in IDS:
    va = VA[c]
    timeline["chunks"].append({
        "id": c, "file": va["file"], "at_s": AT[c], "duration_s": va["duration_s"], "speech_start_s": round(AT[c] + va["speech_start_s"], 3), "speech_end_s": round(AT[c] + va["speech_end_s"], 3),
        "pauses": [{"from_s": round(AT[c] + p_["from"], 3), "to_s": round(AT[c] + p_["to"], 3), "s": p_["s"]} for p_ in va["pauses"] if p_["s"] >= 0.5],
        "lines": [{"text": ln["text"], "start_s": LS(c, i), "end_s": LE(c, i), "pause_after": ln["pause_after"], "key": (c, i) in KEY_LINES,
                   "words": [{"text": w, "start_s": s, "end_s": e} for w, s, e in words(c, i)]} for i, ln in enumerate(va["lines"])],
    })

# ------------------------------------------------------------------ spec
SHOTS = [
    ("S01-A", "S01", "P1", "PEOPLE | AI AGENTS: the person's inbox says the renewal moved to Nov 28; the agent's workflow file still says Nov 14. The views break apart; the truth sits across the company's systems.", "People and agents see different truths; the truth is scattered.", "—", F),
    ("S02-A", "S02", "P1", "PEOPLE copy by hand | AI AGENTS start empty.", "Both audiences' problem.", "—", F),
    ("S03-A", "S03", "P2", "'Navis' lands on the NavisLabs mark; branches to Navis App (people) / Navis Developer (developers + AI agents).", "Company and products.", "NavisLabs", P),
    ("S04-A", "S04", "P2", "Thirteen connected systems (launch state) → signals → memory → context → intelligence → decision → execution → outcome (Building) → learning (Next).", "How it works.", "NavisLabs", LS_),
    ("S05-A", "S05", "P3", "Company → teams → people → customers · projects · commitments → where the work lives → the Navis App opens; Today at a glance.", "Who uses the App.", "Navis App", P),
    ("S06-A", "S06", "P3", "Your attention (3 priorities, chips from Gmail, Salesforce, Calendar, Jira, Docs, Meet) → What changed → the Kaveri card.", "The event appears.", "Navis App", LS_),
    ("S07-A", "S07", "P3", "Why this matters → seven sources with time and freshness → evidence opened out: eight systems → one customer state.", "Traceable understanding.", "Navis App", LS_),
    ("S08-A", "S08", "P3", "Waiting on you → Review & reply → Navis prepares the draft → the person edits → cursor rests on Approve & send.", "Navis prepares; a person decides.", "Navis App", P),
    ("S09-A", "S09", "P3", "Approve & send → Sending… → Gmail accepted → Reply sent → the same event across Gmail, Salesforce, GitHub, Jira (who owns the next step).", "The company acts; the event lands in more than one system.", "Navis App", LS_),
    ("S10-A", "S10", "P4", "Light → dark: VS Code + Claude Code on the same company's repository; the task.", "Same company, developers and agents.", "Navis Developer", PP),
    ("S11-A", "S11", "P4", "Console › Members: Add a member → Invited; claude mcp add / list → ✓ Connected; Connect › Access surfaces lighting MCP, API, SDK, CLI as each is said.", "Team + connection.", "Navis Developer", PP),
    ("S12-A", "S12", "P4", "navis_get_relevant_context → six cited facts (incl. the CRM close date) with source and freshness.", "Company context, not prose.", "Navis Developer", PP),
    ("S13-A", "S13", "P4", "npm install ./navis-sdk-0.1.0.tgz (local package) + SDK example; curl the Developer API → items · sources · freshness; 'No model is called'.", "Navis grounds; the model reasons.", "Navis Developer", PP),
    ("S14-A", "S14", "P4", "Credential → organization → scope: AUTHORIZED / OWN SCOPE / DENIED + the exact refusal.", "A real security boundary.", "Navis Developer", PP),
    ("S15-A", "S15", "P4", "The diff to src/workflows/kaveri-renewal.ts → Runs → Run detail: timeline, '—' economics, Outcome 'Not judged'.", "The run is on record.", "Navis Developer", D),
    ("S16-A", "S16", "P5", "Sign up 'For myself' → personal workspace (Owner) → the company's Members (roles) → navis workstate checkpoint → next session restores the work state.", "Solo, team, continuity — no Navis App required.", "Navis Developer", PP),
    ("S17-A", "S17", "P5–P6", "One company · NavisLabs: Navis App and Navis Developer either side of the shared understanding; same fact / source / freshness; One understanding. Two ways in.", "The thesis.", "NavisLabs", F),
    ("S18-A", "S18", "P7–P8", "Agent clients change; the company's record stays; pillars. Then everything stops: the mark, 'NavisLabs.', silence, the tagline, both products, navislabs.in.", "What stays; the name.", "NavisLabs", F),
]
spec = {
    "about": "NavisLabs launch film V7 — the founder's final voice is the master clock. Copy: src/data/navislabs_v7_copy.json. Entities + launch-state connectors: src/data/navislabs_v7_launch_state.json. Voice: navislabs_v7_voice_timeline.json. Audio: navislabs_v7_audio_map.json.",
    "version": "v6",
    "format": {"width": 1920, "height": 1080, "fps": FPS, "duration_s": END, "frames": FRAMES},
    "brand": {"company": "NavisLabs", "products": [{"name": "Navis App", "audience": "people / teams"}, {"name": "Navis Developer", "audience": "developers + AI agents (teams and solo builders)", "status": "Private preview"}], "tagline": COPY["tagline"], "cta": "navislabs.in"},
    "narrative": {
        "thesis": COPYDOC["positioning"]["thesis"],
        "business_event": f"{DATA['customers'][0]['name']}'s renewal moved (fictional demo data).",
        "integrations": {"film_launch_state": DATA["integrations"]["connected"], "rule": "The film shows the founder-supplied launch state: all thirteen systems connected. Detailed evidence only where the film demo data holds a record; Microsoft 365, HubSpot and Zoom appear as connected infrastructure. Public website status may lag this film configuration."},
        "shape": [f"{a:.1f}–{b:.1f} {sid} · {act}: {beat}" for sid, a, b, _, beat, act in SCENES],
    },
    "voiceover": {"chunks": IDS, "ids": IDS, "lines": sum(len(VA[c]["lines"]) for c in IDS), "words": sum(len(l["text"].split()) for c in IDS for l in VA[c]["lines"]), "source": "navislabs_v7_voice_timeline.json"},
    "scenes": [{"id": sid, "from_s": a, "to_s": b, "overlap_frames": tr[1], "transition_out": {"type": tr[0], "frames": tr[1], "direction": tr[2]}, "beat": beat, "act": act} for sid, a, b, tr, beat, act in SCENES],
    "shots": [{"id": i, "scene": sc, "from_s": next(a for s_, a, *_ in SCENES if s_ == sc), "to_s": next(b for s_, _, b, *_ in SCENES if s_ == sc), "said": said, "shown": shown, "why": why, "product": prod, "feature": "—", "source": "—", "proof": "—", "claim_status": cl} for i, sc, said, shown, why, prod, cl in SHOTS],
    "onscreen_copy": COPY,
    "timing": {"beats": BEATS, "typing": TYPING},
}

# ------------------------------------------------------------------ audio map
speech = []
for c in IDS:
    for i, ln in enumerate(VA[c]["lines"]):
        speech.append({"from_s": LS(c, i), "to_s": LE(c, i), "chunk": c, "key": (c, i) in KEY_LINES})
MUSIC_SECTIONS = [
    ("M1", "problem", 0.0, B["logoTile"], "almost no music, never dead: a low atmosphere under the contradiction; scattered high fragments as the systems appear; heavier on 'by hand'; held on 'without it'; a breath, then a reverse swell into 'Navis'"),
    ("M2", "reveal", B["logoTile"], SCENES[4][1], "the first wow: on 'Navis' the music opens — warm harmonic bloom, deep pulse, small digital texture; the pipeline builds layer by layer and pulls back on 'next'"),
    ("M3", "human", SCENES[4][1], SCENES[9][1], "the Navis App: warm, intelligent, half-time; drops back to a controlled breath on 'A person decides.', returns on 'Then the company acts.'"),
    ("M4", "technical", SCENES[9][1], SCENES[15][1], "Navis Developer: precise 16th-note rhythm, soft kick, analog bass; thins under the key lines; slows for the permission check with a low tonal shift on DENIED; resolves slightly as the run completes"),
    ("M5", "scale", SCENES[15][1], SCENES[17][1], "solo → team → company: from one voice to the full ensemble; the voice alone carries 'Same facts. Same sources. Same freshness.'; lift on 'One understanding.', resolution on 'Two ways in.'"),
    ("M6", "thesis", SCENES[17][1], B["endLockup"] - 0.3, "slow, deep, warm, wide; no rhythm; rises in the pause after 'Tools change.'; no crescendo"),
    ("M7", "end", B["endLockup"] - 0.3, END, "everything almost stops for 'NavisLabs.'; logo in near-silence; a very soft harmonic tail under the tagline; then silence"),
]
# Controlled dips on top of the ducking (the score itself also breathes at these moments).
DIPS = [
    {"from_s": round(B["blackout"] - 0.1, 3), "to_s": round(B["logoTile"] - 0.12, 3), "db": -14, "ramp_s": 0.5, "why": "the breath before Navis (the reverse swell rides through it)"},
    {"from_s": round(LS("P3", 5) - 0.2, 3), "to_s": round(B["approveClick"] - 0.05, 3), "db": -4, "ramp_s": 0.6, "why": "'A person decides.' — the music drops back to a controlled breath, not silence"},
    {"from_s": round(B["approveClick"], 3), "to_s": round(LS("P3", 6) - 0.05, 3), "db": -8, "ramp_s": 0.12, "why": "held breath on Approve & send"},
    {"from_s": round(B["permDenied"] - 0.05, 3), "to_s": round(LE("P4", 7) + 0.3, 3), "db": -5, "ramp_s": 0.4, "why": "the refusal: quieter, darker, serious"},
    {"from_s": round(LE("P8", 0) + 0.15, 3), "to_s": round(LS("P8", 1) - 0.15, 3), "db": -20, "ramp_s": 0.5, "why": "near-silence after 'NavisLabs.'"},
    {"from_s": round(LE("P8", 1) + 0.5, 3), "to_s": END, "db": -96, "ramp_s": 0.8, "why": "silent end"},
]
DUCK = {"normal_db": -6.0, "key_db": -11.0, "attack_s": 0.15, "release_s": 0.6}


def rdp(pts, eps):
    """Ramer–Douglas–Peucker: the fewest keyframes that keep the curve within eps dB."""
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    best, bi = 0.0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        yl = y0 + (y1 - y0) * (x - x0) / (x1 - x0) if x1 != x0 else y0
        if abs(y - yl) > best:
            best, bi = abs(y - yl), i
    if best <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[: bi + 1], eps)[:-1] + rdp(pts[bi:], eps)


def curve(fn, step=0.02, eps=0.15):
    n = int(END / step) + 1
    pts = [(round(i * step, 3), round(fn(i * step), 2)) for i in range(n)] + [(END, round(fn(END), 2))]
    k = rdp(pts, eps)
    return {"t": [a for a, _ in k], "db": [b for _, b in k]}


def duck_at(t):
    d = 0.0
    for w in speech:
        a, b = w["from_s"], w["to_s"]
        if a - DUCK["attack_s"] <= t <= b + DUCK["release_s"]:
            k = min(1.0, (t - (a - DUCK["attack_s"])) / DUCK["attack_s"]) if t < a else (1.0 if t <= b else 1.0 - (t - b) / DUCK["release_s"])
            d = min(d, k * (DUCK["key_db"] if w["key"] else DUCK["normal_db"]))
    return d


def dip_at(t):
    d = 0.0
    for x in DIPS:
        a, b, r = x["from_s"], x["to_s"], x["ramp_s"]
        if a - r <= t <= b + r:
            k = (t - (a - r)) / r if t < a else (1.0 if t <= b else 1.0 - (t - b) / r)
            d = min(d, k * x["db"])
    return d


# Six score stems (public/music/temp/v7/*.wav from scripts/make-score-v7.py). duck = how much of the
# voice ducking each stem takes (the bed and textures stay a little more present).
MUSIC_STEMS = [
    ("bed", "atmospheric bed: low drone, air, distant shimmer", -3.0, 0.8),
    ("pulse", "low cinematic pulse: soft kick, sub, analog bass", -3.0, 1.0),
    ("harmony", "warm harmonic texture: detuned analog pads, strings-like", -1.5, 1.0),
    ("rhythm", "technical rhythmic layer: plucked 16ths, soft ticks", -4.0, 1.0),
    ("texture", "transition textures: reverse swells, digital micro-texture, the permission tone", -3.0, 0.5),
    ("resolve", "emotional resolution: soft mallet / bell motifs", -3.0, 0.7),
]
SFX_LIB = {
    "key1": (-25, "KEYBOARD"), "key2": (-25, "KEYBOARD"), "key3": (-25, "KEYBOARD"), "key4": (-25, "KEYBOARD"),
    "enter": (-19, "TERMINAL"), "save": (-21, "TERMINAL"),
    "click": (-15, "UI CLICK"),
    "data": (-21, "DATA ARRIVAL"),
    "source": (-21, "SOURCE APPEAR"),
    "connect": (-18, "MCP CONNECT"), "surface": (-23, "MCP CONNECT"),
    "api": (-13, "API RESPONSE"),
    "retrieve": (-22, "CONTEXT RETRIEVAL"),
    "deny": (-17, "PERMISSION DENIED"),
    "approve": (-15, "APPROVE"),
    "sent": (-21, "SEND"),
    "gmail": (-13, "GMAIL CONFIRM"),
    "run": (-18, "RUN START"), "complete": (-14, "RUN COMPLETE"),
    "reveal": (-18, "PRODUCT REVEAL"),
    "air": (-24, "TRANSITION"),
    "end": (-20, "END REVEAL"),
}
SFX_CATEGORIES = ["KEYBOARD", "TERMINAL", "MOUSE", "UI CLICK", "DATA ARRIVAL", "SOURCE APPEAR", "MCP CONNECT", "API RESPONSE", "CONTEXT RETRIEVAL",
                  "PERMISSION DENIED", "APPROVE", "SEND", "GMAIL CONFIRM", "RUN START", "RUN COMPLETE", "PRODUCT REVEAL", "TRANSITION", "END REVEAL"]
chunk_rows = []
for i, c in enumerate(IDS):
    ceiling = AT[IDS[i + 1]] if i + 1 < len(IDS) else END
    ch = next(x for x in COPYDOC["chunks"] if x["id"] == c)
    chunk_rows.append({"id": c, "scene": next(s for s, a, b, *_ in SCENES if a <= AT[c] + VA[c]["speech_start_s"] < b), "start_s": AT[c], "end_s": round(AT[c] + VA[c]["duration_s"], 3),
                       "ceiling_s": round(max(ceiling, AT[c] + VA[c]["duration_s"]), 3), "text": " ".join(l["text"] for l in ch["lines"]), "final": ch["final"], "temp": ch["final"]})
audio_map = {
    "about": "V7 audio: the founder's final voice in eight chunks (P1–P8), placed by the measured performance; a six-stem score mixed with keyframed volume curves (duck under every line, deeper under the key lines, rise in the pauses, controlled dips); SFX on visible actions only. Each slot plays FINAL, else TEMP, else silence.",
    "fps": FPS, "duration_s": END, "resolve_order": ["final", "temp"],
    "layers": {"vo": {"gain_db": 0}, "music": {"gain_db": -4}, "ui_sfx": {"gain_db": 0}, "transitions": {"gain_db": 0}, "ambience": {"gain_db": -96}},
    "voiceover": chunk_rows,
    "speech": speech,
    "music": {"final": "music/final/v7/score.wav", "temp": "music/temp/v7/score-mixdown.wav",
              "style": "Premium cinematic AI-infrastructure score: organic analog synth texture, warm low end, a subtle pulse, restrained percussion, an evolving harmonic bed, technical micro-textures and an emotional final resolution. No EDM, cyberpunk, trailer braams, cheesy piano, corporate stock or generic motivational music. The founder's voice always wins.",
              "stems": [{"id": i, "role": role, "final": f"music/final/v7/{i}.wav", "temp": f"music/temp/v7/{i}.wav", "gain_db": g, "duck": k} for i, role, g, k in MUSIC_STEMS],
              "sections": [{"id": i, "role": role, "from_s": round(a, 3), "to_s": round(b, 3), "brief": br} for i, role, a, b, br in MUSIC_SECTIONS],
              "gain_db": 0, "duck_under_vo_db": DUCK["normal_db"], "duck_key_line_db": DUCK["key_db"], "duck_attack_s": DUCK["attack_s"], "duck_release_s": DUCK["release_s"],
              "dips": DIPS, "curves": {"duck": curve(duck_at), "dips": curve(dip_at)}},
    "sfx": {"style": "Felt, subtle, realistic, premium: real-sounding keys and trackpad, small precise confirmations, a serious low tone for a refusal; never louder than the voice; silence on purpose.",
            "library": {k: {"final": f"sfx/final/v7/{k}.wav", "temp": f"sfx/temp/v7/{k}.wav", "gain_db": g, "category": c_} for k, (g, c_) in SFX_LIB.items()}},
    "ambience": {"temp": "sfx/temp/flow.wav", "final": "sfx/final/flow.wav", "from_s": 0, "to_s": 0.1, "gain_db": -96, "why": "retired in V7: the score's texture stem carries the data flow"},
}

# ------------------------------------------------------------------ product surfaces
_base = next(p_ for p_ in ("navislabs_v7_product_surface_map.json", "navislabs_v5_product_surface_map.json", "archive/v5/navislabs_v5_product_surface_map.json") if os.path.isfile(os.path.join(ROOT, p_)))
base = json.load(open(os.path.join(ROOT, _base)))
ADDED = [
    {"id": "integrations.launch_state", "product": "NavisLabs", "label": "Connected systems (film launch state): Gmail · Google Calendar · Google Meet · Google Drive · Google Docs · Slack · Salesforce · Notion · Microsoft 365 · HubSpot · Jira · GitHub · Zoom", "source": "src/data/navislabs_v7_launch_state.json FILM_LAUNCH_INTEGRATIONS (founder-supplied launch state). Local checkout: the first six live; website: the last seven 'Coming soon'.", "claim_status": LS_},
    {"id": "app.crm", "product": "Navis App", "label": "Salesforce opportunity in the evidence: Kaveri renewal still closes Nov 14 in the CRM (FILM DEMO RECORD; no amounts)", "source": "launch state crm_records", "claim_status": LS_},
    {"id": "app.engineering", "product": "Navis App", "label": "Jira KVR-142 and the GitHub workflow file as engineering context", "source": "launch state engineering_context", "claim_status": LS_},
    {"id": "app.knowledge", "product": "Navis App", "label": "Notion renewal playbook as company knowledge (S01, S04)", "source": "launch state knowledge", "claim_status": LS_},
    {"id": "app.acrossSystems", "product": "Navis App", "label": "After the reply: the same event across Gmail, Salesforce, GitHub, Jira — who owns each next step (no system is shown updating itself)", "source": "film graphic; launch state", "claim_status": F},
    {"id": "dev.team", "product": "Navis Developer", "label": "Company workspace Members with roles (owner · developer) after the solo sign-up", "source": "Devtool MembersPanel.tsx; DEVELOPER_ROLES", "claim_status": PP},
]
drop = {"integrations.live_current", "integrations.expanding", "integrations.future_connected"} | {x["id"] for x in ADDED}
surf = [x for x in base["surfaces"] if x["id"] not in drop] + ADDED
legend = dict(base["claim_status_legend"])
legend["LAUNCH_STATE"] = "shown as available in the founder-supplied launch state (film-only configuration); not yet in the local product checkout and/or shown as 'Coming soon' on the public website at the time of this build"
surfaces = {"about": "Every product surface the V6 film shows, its source and claim status.", "claim_status_legend": legend, "surfaces": surf}

# ------------------------------------------------------------------ interactions
INTERACTIONS = [
    {"id": "why_this_matters", "product": "Navis App", "control": "Why this matters (link)", "cursor": True,
     "states": [("before", B["backToCard"], "cursor leaves the card"), ("settle", B["whyClick"] - 0.12, "settles on the link; hover underline"), ("click", B["whyClick"], "press on 'why'"), ("feedback", B["whyOpen"], "drawer opens"), ("after", B["evidence0"], "sources arrive with time and freshness")]},
    {"id": "review_and_reply", "product": "Navis App", "control": "Review & reply (button)", "cursor": True,
     "states": [("before", B["waiting"] + 0.8, "back on the card; cursor travels"), ("settle", B["reviewReplyClick"] - 0.12, "hover darkens button"), ("click", B["reviewReplyClick"], "press"), ("feedback", B["drawerOpen"], "DecisionDrawer slides in"), ("after", B["drawerOpen"] + 0.38, "drawer open with 'Review draft'")]},
    {"id": "review_draft", "product": "Navis App", "control": "Review draft (button)", "cursor": True,
     "states": [("before", B["drawerOpen"] + 0.1, "cursor moves to the button"), ("settle", B["reviewDraftClick"] - 0.1, "hover"), ("click", B["reviewDraftClick"], "press"), ("feedback", B["preparing"], "'Preparing draft…'"), ("after", B["draftShown"], "the prepared draft")]},
    {"id": "edit_sentence", "product": "Navis App", "control": "message body (selection + typing)", "cursor": True,
     "states": [("before", B["selectStart"] - 0.5, "cursor to the sentence"), ("settle", B["selectStart"] - 0.14, "I-beam settles"), ("click", B["selectStart"], "click-drag selection"), ("feedback", B["selectEnd"], "sentence selected"), ("after", TYPING["humanEdit"]["start"] + len(TYPING["humanEdit"]["text"]) / TYPING["humanEdit"]["cps"], "the person's own sentence")]},
    {"id": "approve_and_send", "product": "Navis App", "control": "Approve & send (button)", "cursor": True,
     "states": [("before", B["approveHover"] - 0.65, "travels during 'A person decides.'"), ("settle", B["approveHover"], "rests on the button — the pause"), ("click", B["approveClick"], "press; music holds its breath"), ("feedback", B["approved"], "'Approved — sending'"), ("after", B["replySent"], "Gmail accepted → Reply sent")]},
    {"id": "add_member", "product": "Navis Developer", "control": "Add member (Console › Members)", "cursor": True,
     "states": [("before", B["membersIn"], "Members + 'Add a member' form"), ("settle", B["addMember"] - 0.12, "hover"), ("click", B["addMember"], "press; 'Adding…'"), ("feedback", B["invited"], "new row"), ("after", B["invited"] + 0.3, "'Invited'")]},
    {"id": "mcp_connect", "product": "Navis Developer", "control": "terminal: claude mcp add / list", "cursor": False,
     "states": [("before", B["mcpAdd"], "the Console's command, key as placeholder"), ("click", B["mcpAdd"] + 0.05, "Enter"), ("feedback", B["mcpAdded"], "'Added stdio MCP server navis…'"), ("after", B["mcpConnected"], "✓ Connected")]},
    {"id": "context_call", "product": "Navis Developer", "control": "MCP tool call navis_get_relevant_context", "cursor": False,
     "states": [("before", B["contextCall"], "tool call"), ("feedback", B["contextResult"], "result header"), ("after", B["contextResult"] + 0.7, "facts with source and freshness")]},
    {"id": "permission_check", "product": "Navis Developer", "control": "request → authorization", "cursor": False,
     "states": [("before", B["permIdentity"], "credential → organization → scope"), ("feedback", B["permAuthorized"], "AUTHORIZED"), ("feedback2", B["permOwnScope"], "OWN SCOPE"), ("after", B["permDenied"], "DENIED → the exact refusal")]},
    {"id": "open_run", "product": "Navis Developer", "control": "Runs row → Run page", "cursor": False,
     "states": [("before", B["runs"], "Runs list"), ("feedback", B["runRow"], "new run row"), ("click", B["runOpen"], "cut into the run"), ("after", B["runTimeline"], "timeline; Outcome 'Not judged'")]},
    {"id": "for_myself", "product": "Navis Developer", "control": "Sign up: 'For myself'", "cursor": True,
     "states": [("before", B["soloIn"], "For my organization / For myself"), ("settle", B["soloPick"] - 0.12, "hover"), ("click", B["soloPick"], "select"), ("feedback", B["soloPick"] + 0.12, "selected"), ("after", B["soloWorkspace"], "Personal workspace · Owner")]},
    {"id": "workstate_checkpoint", "product": "Navis Developer", "control": "terminal: navis workstate checkpoint", "cursor": False,
     "states": [("before", B["soloCheckpoint"], "the agent runs the checkpoint"), ("feedback", B["soloCheckpointOk"], "'Checkpoint recorded'"), ("after", B["soloDayTwo"], "next session restores the work state")]},
]
state_machine = {"about": "Every interactive control in the V6 film: before → (settle) → click → feedback → after, in absolute seconds on the voice clock.",
                 "cursor_rules": {"settle_s_min": 0.1, "press": "pointer scale 1 → 0.92 → 1 over 0.12 s", "ring": False, "speed": "arc easeInOut, faster where the voice is dense", "hidden": "while evidence is read, in terminal scenes; fades, never pops"},
                 "interactions": [{"id": x["id"], "product": x["product"], "control": x["control"], "cursor": x["cursor"], "states": [{"state": s_, "at_s": round(t_, 3), "what": w_} for s_, t_, w_ in x["states"]]} for x in INTERACTIONS]}
PLAN = [
    ("S01–S02", "P1", "M1 problem: low atmosphere, scattered fragments, heavier on 'by hand'", ["SOURCE APPEAR: the person's view, the agent's view; quieter ticks as the truth lands in each system", "UI CLICK ×3 as fragments are copied by hand"], "the pause after 'different truths' keeps only the atmosphere; a breath before 'Navis'", "Something fundamental is broken."),
    ("S03–S04", "P2", "M2 reveal: the music opens on 'Navis'", ["PRODUCT REVEAL: a low bloom as 'Navis' lands on the mark", "TRANSITION: soft air on the wipe into the light world", "DATA ARRIVAL per signal", "CONTEXT RETRIEVAL as memory becomes context"], "the breath before 'Navis' (reverse swell)", "All the scattered pieces become one."),
    ("S05–S09", "P3", "M3 human: warm, half-time", ["UI CLICK on Why / Review & reply / Review draft / the sentence", "SOURCE APPEAR per evidence row", "KEYBOARD under the person's own sentence", "APPROVE · SEND · GMAIL CONFIRM"], "'A person decides.' — the music drops back to a breath; a held breath on Approve; returns on 'Then the company acts.'", "Navis prepares. A person decides. The company acts."),
    ("S10–S15", "P4", "M4 technical: precise rhythm", ["KEYBOARD + TERMINAL", "UI CLICK Add member", "MCP CONNECT on ✓ Connected; tiny accents as MCP · API · SDK · CLI light", "CONTEXT RETRIEVAL on the tool call; DATA ARRIVAL as each fact lands", "API RESPONSE", "PERMISSION DENIED: a low, serious tone", "RUN START · RUN COMPLETE"], "the rhythm thins under 'Navis isn't the model.' and stops for the permission check", "Technically deep, always readable."),
    ("S16–S17", "P5–P6", "M5 scale: one voice → the ensemble", ["UI CLICK 'For myself'", "TERMINAL Enter + checkpoint recorded", "CONTEXT RETRIEVAL as the next session restores", "TRANSITION as the event reaches both products"], "no SFX under 'Same facts. Same sources. Same freshness.' — the voice carries it", "Solo, team, company: the same understanding."),
    ("S18", "P7–P8", "M6 thesis → M7 end", ["END REVEAL on the end lockup"], "near-silence after 'NavisLabs.'; a soft harmonic tail under the tagline; silent end", "This company has a thesis."),
]
design_plan = {"about": "Sound design plan for the V7 film (founder voice = master clock). The score and SFX in the review cut are synthesized in-project (scripts/make-score-v7.py, scripts/make-sfx-v7.py); ElevenLabs-generated replacements drop into the final/ slots.", "layers": audio_map["layers"], "categories": SFX_CATEGORIES,
               "rules": ["The founder's voice always wins: about 12–13 LU above the music under normal speech, about 15–16 LU under the key lines.", "Music ducks −6 dB under every spoken line and −11 dB under the key lines (attack 0.15 s, release 0.6 s); it rises naturally in the pauses; it never disappears under speech.", "SFX are felt, never louder than the voice; important interactions may peak briefly above the music; no whoosh on ordinary moves; no booms.", "Controlled breaths, not dead silence: before 'Navis', 'A person decides.', Approve, the refusal; near-silence after 'NavisLabs.'; silence at the end.", "Master: −14 LUFS integrated, ≤ −1 dBTP, no clipping."],
               "scenes": [{"scenes": s_, "vo": vo_, "music": m_, "sfx": x_, "silence": sil_, "reason": why_} for s_, vo_, m_, x_, sil_, why_ in PLAN]}

for name, obj in [("navislabs_v7_voice_timeline.json", timeline), ("navislabs_v7_film_spec.json", spec), ("navislabs_v7_audio_map.json", audio_map), ("navislabs_v7_product_surface_map.json", surfaces), ("interaction_state_machine.json", state_machine), ("navislabs_audio_design_plan.json", design_plan)]:
    with open(os.path.join(ROOT, name), "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

# sanity
for a_, b_ in zip(SCENES, SCENES[1:]):
    assert abs(a_[2] - b_[1]) < 1e-9 and a_[2] > a_[1] + 0.5, (a_, b_)
assert abs(SCENES[-1][2] - END) < 1e-6
for k_, v_ in BEATS.items():
    assert 0 <= v_ <= END, (k_, v_)
print(f"duration {END:.2f}s ({FRAMES} frames) · scenes {len(SCENES)} · beats {len(BEATS)}")
for sid, a, b, tr, beat, act in SCENES:
    print(f"  {sid} {a:7.2f}–{b:7.2f} ({b - a:5.2f}s) {tr[0]:5s} {beat[:70]}")
print("  chunks:", {c: AT[c] for c in IDS})
