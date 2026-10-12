"""Builds the V5 data for the NavisLabs launch film (V4 picture, V5 narrative).

Reads:
  src/data/navislabs_v5_copy.json        THE copy: 26 voice lines + every on-screen word
  src/data/navislabs_demo_data.json      every entity (people, customer, dates, runs)
Writes (project root):
  navislabs_v5_film_spec.json            scenes, transitions, shots, copy, beats, typing
  navislabs_v5_voiceover_screen_map.json 26 lines: timing, screen, caption beats, product claims, ElevenLabs prep
  navislabs_v5_audio_map.json            VO slots, music arc, SFX library + layers
  navislabs_v5_product_surface_map.json  surfaces and claim status
  interaction_state_machine.json         every button: before → click → feedback → after
  navislabs_audio_design_plan.json       per scene: VO, music, SFX, ducking, silence

This file only times the film; it never defines words or entities.
Run: npm run data:build
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "src/data/navislabs_demo_data.json")))
COPYDOC = json.load(open(os.path.join(ROOT, "src/data/navislabs_v5_copy.json")))
P, PP, D, R, F, FUT = "PROVEN", "PRIVATE_PREVIEW", "DESIGNED", "ROADMAP", "FILM_SIMULATION", "FUTURE_STATE"
CUST = DATA["customers"][0]
USER = DATA["people"][0]
RUN = DATA["runs"][0]

# ------------------------------------------------------------------ scenes
# id, from, to, transition_out (type, frames, direction), beat, act
SCENES = [
 ("S01", 0.0, 6.2, ("none", 0, None), "People and agents see different truths; the truth is scattered", "Problem"),
 ("S02", 6.2, 10.3, ("none", 0, None), "People rebuild by hand; AI agents start without it", "Problem"),
 ("S03", 10.3, 14.3, ("wipe", 27, "from-bottom"), "NavisLabs and its two products", "NavisLabs"),
 ("S04", 14.3, 22.6, ("fade", 18, None), "Signals → memory → context → intelligence → decision → execution → outcome → learning", "NavisLabs"),
 ("S05", 22.6, 26.6, ("none", 0, None), "A company opens the Navis App", "Navis App"),
 ("S06", 26.6, 29.7, ("none", 0, None), "Priorities → what changed → the Acme priority", "Navis App"),
 ("S07", 29.7, 34.2, ("none", 0, None), "Why: source, timeline, freshness → one customer state", "Navis App"),
 ("S08", 34.2, 40.6, ("none", 0, None), "Waiting on you → draft → the person edits", "Navis App"),
 ("S09", 40.6, 44.8, ("wipe", 18, "from-top"), "Approve & send → Gmail accepted → reply sent", "Navis App"),
 ("S10", 44.8, 48.4, ("none", 0, None), "Same company: the engineering side", "Navis Developer"),
 ("S11", 48.4, 52.4, ("none", 0, None), "Invite the team → connect over MCP → four surfaces", "Navis Developer"),
 ("S12", 52.4, 55.9, ("none", 0, None), "Cited facts, with freshness", "Navis Developer"),
 ("S13", 55.9, 58.8, ("none", 0, None), "SDK and API; the model stays the agent's", "Navis Developer"),
 ("S14", 58.8, 62.2, ("none", 0, None), "Authorized / own scope / denied", "Navis Developer"),
 ("S15", 62.2, 66.6, ("none", 0, None), "The work, and the run on record", "Navis Developer"),
 ("S16", 66.6, 73.4, ("fade", 18, None), "Solo developer: personal workspace, work state carries over", "Navis Developer"),
 ("S17", 73.4, 84.0, ("fade", 18, None), "One company, two products, one shared understanding", "Same company"),
 ("S18", 84.0, 100.0, ("none", 0, None), "Models change; what it knows stays yours; NavisLabs", "Moat + ending"),
]

# ------------------------------------------------------------------ voice
# The 26 lines, their locked timing and direction: src/data/navislabs_v5_copy.json.
VO = [(l["id"], l["scene"], l["start_s"], l["end_s"], l["ceiling_s"], l["text"], l["visual"], l["emotion"], l["delivery"], l["pace"], l["pause"], l["audio_tag"] or "", l["pronunciation"] or "") for l in COPYDOC["voiceover"]]

# ------------------------------------------------------------------ beats (absolute seconds)
BEATS = {
 # problem
 "memoryPoint": 0, "memoryLine": 0,
 # V01: PEOPLE | AI AGENTS, two truths about one customer.
 "truthLabels": 0.3, "truthPeople": 0.9, "truthAgent": 1.5, "truthDiff": 2.2,
 # V02: the views break apart; a piece of the truth lands in each system.
 "scatter": 3.4, "signalDecision": 3.95, "signalCustomer": 4.1, "signalCommitment": 4.25, "signalMeeting": 4.4, "signalContext": 4.55, "signalAccount": 4.7,
 "tilesSettle": 4.4, "problem": 5.2,
 "peopleStart": 6.3, "copy1": 6.8, "copy2": 7.25, "copy3": 7.7, "agentsStart": 8.6, "blackout": 10.0,
 "taskPreview": 0, "questionCard": 0,
 # reveal
 "logoTile": 10.5, "logoWord": 10.75, "logoLine": 11.0, "archApp": 12.6, "archDev": 12.9, "toLight": 14.3,
 # data flow
 "iconsIn": 14.5, "signalsOut": 14.9, "roadmapIn": 15.4, "expandIn": 15.4,
 "flowMemory": 16.3, "flowContext": 17.4, "flowIntel": 18.5, "flowDecision": 19.5, "flowExecution": 20.3, "flowOutcome": 21.0, "flowLearning": 21.5,
 "understanding": 17.4, "entitiesIn": 17.4, "intelIn": 18.5,
 # application
 "orgIn": 22.6, "appRise": 24.1, "glance": 24.85, "prioritiesIn": 25.6, "whatChanged": 26.6, "priorityFocus": 27.75, "backToCard": 28.6,
 "whyClick": 29.9, "whyOpen": 30.0,
 "evidence0": 30.3, "evidence1": 30.42, "evidence2": 30.54, "evidence3": 30.66, "evidence4": 30.78, "evidence5": 30.9,
 "freshness": 31.05, "youCanDo": 31.3, "explodeIn": 31.75, "resolveIn": 32.7, "whyClose": 34.0,
 "waiting": 34.2, "reviewReplyClick": 35.5, "drawerOpen": 35.6, "reviewDraftClick": 36.0, "preparing": 36.05, "draftShown": 36.5,
 "selectStart": 37.5, "selectEnd": 37.95, "caption": 0, "approveHover": 40.5, "approveClick": 40.95,
 "approved": 41.15, "sending": 41.5, "gmailAccepted": 42.5, "replySent": 42.8, "proofRail": 43.1,
 # developer (organization)
 "devCut": 44.8, "devCaption": 44.85, "agentEnter": 47.2, "agentRead": 47.4, "agentNeeds": 47.7,
 "membersIn": 48.4, "addMember": 48.85, "invited": 49.05,
 "mcpAdd": 49.55, "mcpAdded": 49.85, "mcpList": 50.1, "mcpConnected": 50.6,
 "connectIn": 51.05, "surfaceMcp": 51.1, "surfaceApi": 51.35, "surfaceSdk": 51.65, "surfaceCli": 51.95, "mcpCommand": 0,
 "contextCall": 52.45, "contextResult": 52.95, "contextSource": 53.8, "contextFresh": 54.6, "agentReason": 55.3,
 "sdkIn": 55.9, "sdkInstalled": 56.45, "sdkCode": 56.55, "apiIn": 57.2, "apiResponse": 57.55, "modelNeutral": 58.0,
 "permIdentity": 58.85, "permAuthorized": 59.45, "permOwnScope": 59.9, "permDenied": 60.35, "refusal": 60.9,
 "agentUses": 62.25, "agentDone": 63.0, "runs": 63.75, "runRow": 63.9, "runOpen": 64.4, "runTimeline": 64.65, "runOutcome": 65.85,
 # solo developer
 "soloIn": 66.6, "soloPick": 67.05, "soloWorkspace": 67.45, "soloCheckpoint": 68.75, "soloCheckpointOk": 69.55, "soloDayTwo": 70.45, "soloRestore": 70.8, "soloSections": 71.15,
 "dayOne": 0, "dayTwo": 0, "restore": 0, "restoreTask": 0, "restoreDecisions": 0, "restoreOpen": 0,
 # same organization
 "notChatbot": 0, "notAutomation": 0, "heroIn": 73.4, "sharedSignal": 74.4, "sameFacts": 77.7, "sameSources": 78.8, "sameFreshness": 79.9, "sharedUnderstanding": 81.4, "peopleAgents": 82.9,
 # moat + end
 "modelsChange": 84.4, "agentsChange": 85.6, "toolsChange": 86.8, "clientsIn": 85.0,
 "staysYours": 88.35, "loopIn": 0, "recordIn": 88.6, "pillars": 90.4,
 "yours": 0, "wordsIn": 0, "collapse": 0,
 "endLockup": 94.0, "endTagline": 94.6, "endProducts": 95.5, "endUnderstanding": 95.5, "endUrl": 96.4, "fadeOut": 99.4,
}
TYPING = {
 "taskPreview": {"start": 0.0, "text": "(unused)", "cps": 30},
 "agentTask": {"start": 46.0, "text": RUN["task"], "cps": 30},
 "humanEdit": {"start": 38.1, "text": "Happy to walk you through it Thursday.", "cps": 32},
 "mcpList": {"start": 50.1, "text": "claude mcp list", "cps": 40},
 "sdkInstall": {"start": 55.95, "text": "npm install ./navis-sdk-0.1.0.tgz", "cps": 75},
}

COPY = COPYDOC["onscreen_copy"]

SHOTS = [
 ("S01-A","S01",0,6.2,"V01–V02","PEOPLE | AI AGENTS: the person's inbox says the renewal moved to Nov 28; the agent's workflow file still says Nov 14. The views break apart; a piece of the truth sits in each of six live systems.","People and agents see different truths; the truth is scattered.","—","Live integrations","demo data; website logos.tsx",F),
 ("S02-A","S02",6.2,10.3,"V03","PEOPLE copy by hand | AI AGENTS start empty.","Both audiences' problem.","—","—","—",F),
 ("S03-A","S03",10.3,14.3,"V04","NavisLabs mark + wordmark; branches to Navis App (people) / Navis Developer (developers + AI agents).","Company and products in one picture.","NavisLabs","Two products, one core","navis-logo.png; deck p.5",P),
 ("S04-A","S04",14.3,22.6,"V05–V06","Live systems → signals → memory → context → intelligence → decision → execution → outcome (building) → learning (next); roadmap systems shown apart, dashed, labelled 'Roadmap · coming soon'.","How it works.","NavisLabs","Signal pipeline","deck p.5 (Signals → Memory → What's true now → What matters → Decide → Learn: BUILDING)",F),
 ("S05-A","S05",22.6,26.6,"V07","Company → teams → people → customers / projects / commitments → where the work lives → the Navis App opens; Today at a glance.","Who uses the App.","Navis App","Today, CountStrip","DailyBriefHero.tsx, CountStrip.tsx; Application sidebar People/Projects/Customers",P),
 ("S06-A","S06",26.6,29.7,"V08","Scroll to Your attention (3 priorities) → What changed → the Acme card.","The event appears.","Navis App","NarrativeCard, What changed","page.tsx",P),
 ("S07-A","S07",29.7,34.2,"V09","Why Navis surfaced this (six live sources with source/time/freshness) → evidence opens out into one customer state.","Traceable conclusion.","Navis App","WhyThisDrawer","WhyThisDrawer.tsx",P),
 ("S08-A","S08",34.2,40.6,"V10–V11","Waiting → Review & reply → Review draft → draft → edit.","Navis prepares; a person decides.","Navis App","DraftReviewPanel","DraftReviewPanel.tsx",P),
 ("S09-A","S09",40.6,44.8,"V12","Approve & send → Sending… → Gmail accepted → Reply sent → proof rail.","The company acts, confirmed by the provider.","Navis App","SendStatus","DraftReviewPanel.tsx",D),
 ("S10-A","S10",44.8,48.4,"V13","Light → dark: VS Code + Claude Code; the task; the agent lacks context.","Same company, engineering side.","Navis Developer","—","CLIENTS.md",PP),
 ("S11-A","S11",48.4,52.4,"V14","Console › Members: Add a member → Invited; claude mcp add / list → ✓ Connected; Console › Connect (MCP, API, SDK, CLI).","Team + connection.","Navis Developer","Members, Connect","InviteMemberForm.tsx, MembersPanel.tsx, surfaces.ts",PP),
 ("S12-A","S12",52.4,55.9,"V15","navis_get_relevant_context → five cited facts; macro SOURCE, FRESHNESS; agent cites them.","Cited facts, not prose.","Navis Developer","MCP context","register.ts",PP),
 ("S13-A","S13",55.9,58.8,"V16","npm install ./navis-sdk-0.1.0.tgz (not on npm) + SDK example; curl POST /developer/context (X-API-Key) → items/sources/freshness.","Navis supplies facts; the model is the agent's.","Navis Developer","SDK, API","surfaces.ts; credentials.ts; openapi",PP),
 ("S14-A","S14",58.8,62.2,"V17","Credential → organization → scope: AUTHORIZED / OWN SCOPE / DENIED + exact refusal.","Access without unrestricted access.","Navis Developer","Permissions","authorize.ts; credentials.ts",PP),
 ("S15-A","S15",62.2,66.6,"V18","Diff → Runs (new row) → Run timeline → Outcome 'Not judged'.","Agent work is on record.","Navis Developer","Runs, Run","RunsPanel.tsx, RunDetailPanel.tsx",D),
 ("S16-A","S16",66.6,73.4,"V19","Sign up 'For myself' → Personal workspace (Owner) → navis workstate checkpoint → next session: NAVIS WORK CONTINUITY restored.","Navis Developer works for one person, too.","Navis Developer","Personal workspace, CLI work state","SignUpForm.tsx, OrganizationPanel.tsx, lib/format.ts, packages/cli workstate.ts/restore.ts",PP),
 ("S17-A","S17",73.4,84.0,"V20–V22","One company · NavisLabs: shared organizational context feeding the Navis App (people · teams) and Navis Developer (developers · AI agents); same fact / source / freshness; thesis.","The brand idea.","NavisLabs","Both products","deck p.6",F),
 ("S18-A","S18",84.0,94.0,"V23–V25","Agent clients keep changing; the company's record (the same facts, sources, freshness) stays put; pillars.","What it knows stays yours.","NavisLabs","Ownership, model-neutral","CLIENTS.md; demo data",F),
 ("S18-B","S18",94.0,100.0,"V26","End card: mark + wordmark, headline, both products, navislabs.in.","Remember NavisLabs.","NavisLabs","—","navislabs.in",P),
]

MUSIC_SECTIONS = [
 # Audio-production arc (approved 2026-10-06). The picture cuts each boundary
 # lands near are in navislabs_v5_music_production_brief.json.
 ("M1","restrained",0.0,12.0,"restrained, almost silent: a low bed; the NavisLabs reveal at 10.5 s is carried by silence and one tonal SFX"),
 ("M2","emergence",12.0,22.0,"subtle brand emergence under the products and the data flow"),
 ("M3","human",22.0,45.0,"human / organizational: warm, unhurried, the person's decision"),
 ("M4","technical",45.0,68.0,"technical developer momentum: precise, light rhythm"),
 ("M5","convergence",68.0,82.0,"convergence: the human and technical motifs meet; shared understanding"),
 ("M6","conviction",82.0,94.0,"conviction / moat: steady, grounded, no riser"),
 ("M7","resolve",94.0,100.0,"resolution under the end card, then silence"),
]
DIPS = [
 {"from_s": 10.0, "to_s": 10.5, "db": -96, "why": "breath before NavisLabs"},
 {"from_s": 40.95, "to_s": 41.2, "db": -96, "why": "held breath on Approve & send"},
 {"from_s": 60.9, "to_s": 62.1, "db": -18, "why": "the refusal: quieter, not louder"},
 {"from_s": 98.6, "to_s": 100.0, "db": -96, "why": "silent end"},
]
SFX_LIB = {
 # name: (gain_db, default category). Each event in src/config/beats.ts names its own category.
 "key": (-26, "KEYBOARD"), "key2": (-26, "KEYBOARD"), "key3": (-26, "KEYBOARD"),
 "enter": (-20, "TERMINAL ENTER"), "click": (-18, "CURSOR CLICK"), "select": (-27, "SOURCE APPEARING"),
 "run": (-28, "RUN START"), "confirm": (-23, "RUN COMPLETE"), "sent": (-21, "SENDING"), "deny": (-27, "PERMISSION DENIED"),
 "air": (-34, "PRODUCT TRANSITION"),
 "connect": (-24, "MCP CONNECTION"), "retrieve": (-29, "CONTEXT RETRIEVAL"), "save": (-27, "SAVE"), "approve": (-22, "APPROVE"),
 "gmail": (-24, "GMAIL CONFIRMATION"), "brand": (-26, "NAVISLABS REVEAL"),
}
SFX_CATEGORIES = ["KEYBOARD", "TERMINAL ENTER", "MCP CONNECTION", "CONTEXT RETRIEVAL", "SOURCE APPEARING", "CURSOR CLICK", "PERMISSION DENIED", "SAVE", "APPROVE", "SENDING", "GMAIL CONFIRMATION", "RUN START", "RUN COMPLETE", "PRODUCT TRANSITION", "NAVISLABS REVEAL"]

def sfx_lib():
    return {k: {"final": f"sfx/final/{k}.wav", "temp": f"sfx/temp/{k}.wav", "gain_db": g, "category": c} for k, (g, c) in SFX_LIB.items()}

# ------------------------------------------------------------------ interactions
def B(k): return BEATS[k]
INTERACTIONS = [
 {"id": "why_this_matters", "product": "Navis App", "control": "Why this matters (link)", "cursor": True,
  "states": [("before", B("backToCard"), "card at rest; cursor enters"), ("settle", B("whyClick") - 0.12, "cursor settles on the link; hover underline"), ("click", B("whyClick"), "press"), ("feedback", B("whyOpen"), "drawer begins to open"), ("after", B("evidence0"), "Why Navis surfaced this: evidence rows arrive")]},
 {"id": "review_and_reply", "product": "Navis App", "control": "Review & reply (button)", "cursor": True,
  "states": [("before", B("waiting") + 0.8, "back on the card; cursor travels"), ("settle", B("reviewReplyClick") - 0.12, "hover darkens button"), ("click", B("reviewReplyClick"), "press scale"), ("feedback", B("drawerOpen"), "DecisionDrawer slides in"), ("after", B("drawerOpen") + 0.38, "drawer open with 'Review draft'")]},
 {"id": "review_draft", "product": "Navis App", "control": "Review draft (button)", "cursor": True,
  "states": [("before", B("drawerOpen") + 0.1, "cursor moves to the button"), ("settle", B("reviewDraftClick") - 0.1, "hover"), ("click", B("reviewDraftClick"), "press"), ("feedback", B("preparing"), "'Preparing draft…' then spinner"), ("after", B("draftShown"), "the draft")]},
 {"id": "edit_sentence", "product": "Navis App", "control": "message body (text selection + typing)", "cursor": True,
  "states": [("before", B("selectStart") - 0.5, "cursor to sentence start"), ("settle", B("selectStart") - 0.14, "cursor settles at the sentence start; I-beam"), ("click", B("selectStart"), "click-drag selection"), ("feedback", B("selectEnd"), "sentence selected"), ("after", TYPING["humanEdit"]["start"] + len(TYPING["humanEdit"]["text"]) / TYPING["humanEdit"]["cps"], "new sentence typed; 'Saved' → 'Save changes'")]},
 {"id": "approve_and_send", "product": "Navis App", "control": "Approve & send (button)", "cursor": True,
  "states": [("before", B("approveHover") - 0.65, "cursor travels to the button"), ("settle", B("approveHover"), "hover"), ("click", B("approveClick"), "press; music held breath"), ("feedback", B("approved"), "'Approved — sending'"), ("after", B("replySent"), "Sending… → Gmail accepted → 'Reply sent · Gmail accepted the message.'")]},
 {"id": "add_member", "product": "Navis Developer", "control": "Add member (button, Console › Members)", "cursor": True,
  "states": [("before", B("membersIn"), "Members table + 'Add a member' form with email filled"), ("settle", B("addMember") - 0.12, "hover"), ("click", B("addMember"), "press; 'Adding…'"), ("feedback", B("invited"), "new row appears"), ("after", B("invited") + 0.3, "row shows 'Invited' (real badge)")]},
 {"id": "mcp_connect", "product": "Navis Developer", "control": "terminal: claude mcp add / claude mcp list", "cursor": False,
  "states": [("before", B("mcpAdd"), "prompt with the Console's command (key as placeholder)"), ("click", B("mcpAdd") + 0.05, "Enter"), ("feedback", B("mcpAdded"), "'Added stdio MCP server navis…'"), ("after", B("mcpConnected"), "'navis: … - ✓ Connected' — tool available")]},
 {"id": "context_call", "product": "Navis Developer", "control": "MCP tool call navis_get_relevant_context", "cursor": False,
  "states": [("before", B("contextCall"), "tool call printed, 'Running…'"), ("feedback", B("contextResult"), "result header"), ("after", B("contextResult") + 0.7, "five facts with source and freshness")]},
 {"id": "permission_check", "product": "Navis Developer", "control": "request → authorization", "cursor": False,
  "states": [("before", B("permIdentity"), "credential → organization → scope"), ("feedback", B("permAuthorized"), "AUTHORIZED"), ("feedback2", B("permOwnScope"), "OWN SCOPE"), ("after", B("permDenied"), "DENIED → exact refusal at refusal beat")]},
 {"id": "open_run", "product": "Navis Developer", "control": "Runs row → Run page", "cursor": False,
  "states": [("before", B("runs"), "Runs list"), ("feedback", B("runRow"), "new run row arrives"), ("click", B("runOpen"), "cut into the run"), ("after", B("runTimeline"), "timeline rows fill; Outcome 'Not judged'")]},
 {"id": "for_myself", "product": "Navis Developer", "control": "Sign up: 'For myself' workspace option", "cursor": True,
  "states": [("before", B("soloIn"), "two options: For my organization / For myself"), ("settle", B("soloPick") - 0.12, "hover"), ("click", B("soloPick"), "select"), ("feedback", B("soloPick") + 0.12, "'For myself' selected: border and check"), ("after", B("soloWorkspace"), "Organization panel: Workspace Personal · Owner")]},
 {"id": "workstate_checkpoint", "product": "Navis Developer", "control": "terminal: navis workstate checkpoint", "cursor": False,
  "states": [("before", B("soloCheckpoint"), "agent runs the checkpoint command"), ("feedback", B("soloCheckpointOk"), "'Checkpoint recorded for <repo> (<branch>).'"), ("after", B("soloDayTwo"), "session closes; next session restores NAVIS WORK CONTINUITY")]},
]

# ------------------------------------------------------------------ build
vo_rows = []
for (i, sc, a, e, c, t, vis, emo, deliv, pace, pause, tag, pron) in VO:
    vo_rows.append({
        "id": i, "scene": sc, "start_s": a, "end_s": e, "ceiling_s": c, "duration_s": round(e - a, 2), "max_duration_s": round(c - a, 2),
        "voice_line": t, "visual": vis,
        "elevenlabs": {"text": (tag + " " + t).strip() if tag else t, "audio_tag": tag or None, "emotion": emo, "delivery": deliv, "pace": pace, "pause": pause, "pronunciation": pron or None, "max_duration_s": round(c - a, 2), "visual_moment": vis},
        # Audio slot paths stay v4: the founder's takes drop in at public/voiceover/final/v4/Vxx.wav.
        "final": f"voiceover/final/v4/{i}.wav", "temp": f"voiceover/temp/v4/{i}.wav",
    })
words = sum(len(r["voice_line"].split()) for r in vo_rows)

scenes = []
for (i, a, b, tr, bt, act) in SCENES:
    kind, frames, direction = tr
    scenes.append({"id": i, "from_s": a, "to_s": b, "overlap_frames": frames, "transition_out": {"type": kind, "frames": frames, "direction": direction}, "beat": bt, "act": act})

spec = {
 "about": "NavisLabs launch film V5 — V4 picture, V5 narrative. Copy: src/data/navislabs_v5_copy.json. Entities: src/data/navislabs_demo_data.json. Voice: navislabs_v5_voiceover_screen_map.json. Audio: navislabs_v5_audio_map.json + navislabs_audio_design_plan.json. Interactions: interaction_state_machine.json.",
 "version": "v5-narrative",
 "format": {"width": 1920, "height": 1080, "fps": 30, "duration_s": 100, "frames": 3000},
 "brand": {"company": "NavisLabs", "products": [{"name": "Navis App", "audience": "people / teams"}, {"name": "Navis Developer", "audience": "developers + AI agents (organizations and solo builders)", "status": "Private preview"}], "tagline": COPY["tagline"], "cta": "navislabs.in"},
 "narrative": {
   "thesis": COPYDOC["positioning"]["thesis"],
   "business_event": f"{CUST['name']}'s renewal moved (synthetic).",
   "integrations": {"live_current": DATA["integrations"]["live_current"], "expanding": DATA["integrations"]["expanding"], "rule": "Roadmap systems appear only in S04, apart from the connected systems, labelled 'Roadmap · coming soon'; they are never shown as connected and never evidence in a demonstrated workflow."},
   "shape": ["0–10.3 problem: people and agents see different truths", "10.3–22.6 NavisLabs + data flow", "22.6–44.8 Navis App (people in a company)", "44.8–66.6 Navis Developer (the same company's developers and agents)", "66.6–73.4 Navis Developer (solo builder)", "73.4–84 one company, two products", "84–94 what stays yours", "94–100 end"],
 },
 "voiceover": {"lines": len(vo_rows), "words": words, "source": "navislabs_v5_voiceover_screen_map.json", "ids": [r["id"] for r in vo_rows]},
 "scenes": scenes,
 "shots": [{"id": i, "scene": sc, "from_s": a, "to_s": b, "said": said, "shown": shown, "why": why, "product": prod, "feature": feat, "source": src, "proof": src, "claim_status": cl} for i, sc, a, b, said, shown, why, prod, feat, src, cl in SHOTS],
 "onscreen_copy": COPY,
 "timing": {"beats": BEATS, "typing": TYPING},
}

# Caption beats: phrases that must land on a picture beat (None = the line's start).
# (phrase, beat key or None, tolerance s, what is on screen)
CAPTION_BEATS = {
 "V01": [("Your people and agents", None, 0.15, "PEOPLE | AI AGENTS labels; the two views of one customer")],
 "V02": [("scattered", "scatter", 0.25, "the two views break apart into the systems")],
 "V03": [("People rebuild it by hand.", None, 0.1, "the PEOPLE side; copy clicks at 6.8–7.7 s"), ("Agents start without it.", "agentsStart", 0.2, "AI AGENTS side: empty session")],
 "V04": [("Navis", None, 0.1, "the NavisLabs mark (10.5 s) and wordmark (10.75 s)")],
 "V05": [("Every email", None, 0.15, "connected systems emitting signals")],
 "V06": [("remembered", None, 0.1, "the pipeline stages"), ("next", "flowLearning", 0.35, "Learning (Next)")],
 "V07": [("the Navis App", "appRise", 0.35, "the Navis App window rises")],
 "V08": [("Acme's renewal moved", "priorityFocus", 0.4, "the Acme priority card")],
 "V09": [("And why", None, 0.12, "click: Why this matters (29.9 s)")],
 "V10": [("drafts the reply", "draftShown", 0.5, "the draft appears")],
 "V11": [("A person decides.", None, 0.2, "the person's own edit (37.5–39.3 s)")],
 "V12": [("Then the company acts.", None, 0.1, "right after the held breath on Approve & send")],
 "V13": [("Navis Developer", "agentTaskTyping", 0.5, "the task is typed to the agent")],
 "V14": [("Invite the team.", None, 0.1, "the Add member click at 48.85 s lands on 'team'"), ("MCP", "mcpConnected", 0.4, "✓ Connected")],
 "V15": [("The agent asks", None, 0.1, "navis_get_relevant_context (52.45 s)"), ("freshness", "contextFresh", 0.5, "the freshness column")],
 "V16": [("It supplies the company's truth.", "modelNeutral", 0.5, "'No model is called'")],
 "V17": [("permissions", "permDenied", 0.6, "the denied key")],
 "V18": [("on record", "runRow", 0.6, "run row: Completed")],
 "V19": [("private workspace", "soloWorkspace", 0.4, "Personal workspace"), ("next session", "soloDayTwo", 0.5, "Next session")],
 "V20": [("One company.", None, 0.1, "One company · NavisLabs (73.4 s)")],
 "V21": [("Same facts.", "sameFacts", 0.1, "macro: same fact"), ("Same sources.", "sameSources", 0.1, "macro: same source"), ("Same freshness.", "sameFreshness", 0.1, "macro: same freshness")],
 "V22": [("One understanding.", "sharedUnderstanding", 0.15, "thesis line"), ("Two ways in.", "peopleAgents", 0.3, "People + AI agents")],
 "V23": [("Models change.", "modelsChange", 0.1, "Models change."), ("Agents change.", "agentsChange", 0.15, "Agents change."), ("Tools change.", "toolsChange", 0.15, "Tools change.")],
 "V24": [("What it knows stays yours.", None, 0.1, "'What it knows stays yours.' on screen (88.35 s)")],
 "V25": [("Company-owned.", "pillar1", 0.15, "pillar: Company-owned"), ("Model-neutral.", "pillar2", 0.2, "pillar: Model-neutral"), ("Shared by people and agents.", "pillar3", 0.25, "pillar: Shared by people + agents")],
 "V26": [("NavisLabs.", None, 0.1, "the end lockup (94.0 s)"), ("The shared understanding for your organization.", "endTagline", 0.6, "the headline on the end card")],
}
EXTRA_BEATS = {"agentTaskTyping": TYPING["agentTask"]["start"] + 0.5, "pillar1": BEATS["pillars"], "pillar2": BEATS["pillars"] + 1.0, "pillar3": BEATS["pillars"] + 2.1}
# Product claims each line makes (ids in navislabs_v5_product_surface_map.json).
LINE_CLAIMS = {
 "V01": ["opening.twoTruths"], "V02": ["integrations.live_current", "opening.twoTruths"], "V03": [], "V04": ["website.hero", "brand.mark"],
 "V05": ["integrations.live_current", "flow.pipeline"], "V06": ["flow.pipeline"], "V07": ["app.today", "app.countstrip"],
 "V08": ["app.whatChanged", "app.priorities"], "V09": ["app.whyThis", "app.evidenceOpened"], "V10": ["app.waiting", "app.draft"],
 "V11": ["app.draft"], "V12": ["app.send"], "V13": ["dev.clients"],
 "V14": ["dev.members", "dev.connect.mcp", "dev.mcpCli", "dev.connect.api", "dev.connect.sdk", "dev.connect.cli"],
 "V15": ["dev.context"], "V16": ["dev.modelFree", "dev.connect.sdk", "dev.connect.api", "dev.apiAuth"],
 "V17": ["dev.permissions", "dev.ownScope"], "V18": ["dev.runs", "dev.runDetail"], "V19": ["dev.personalWorkspace", "dev.workstate"],
 "V20": ["hero.shared"], "V21": ["hero.shared", "dev.context"], "V22": ["hero.shared"], "V23": ["dev.clients"],
 "V24": ["moat.ownership"], "V25": ["moat.ownership", "dev.modelFree"], "V26": ["website.hero"],
}

def caption_beats(r):
    out = []
    for phrase, beat, tol, label in CAPTION_BEATS[r["id"]]:
        at = r["start_s"] if beat is None else EXTRA_BEATS.get(beat, BEATS.get(beat))
        assert r["start_s"] - 1e-6 <= at <= r["ceiling_s"] and phrase in r["voice_line"], (r["id"], phrase, at)
        out.append({"phrase": phrase, "lands_at_s": round(at, 2), "tolerance_s": tol, "picture": label})
    return out

screen_map = {"about": "V5 script (V4 picture timing): 26 lines with timing, what is on screen, caption beats and the product claims each line makes. Copy source: src/data/navislabs_v5_copy.json. Final takes go to public/voiceover/final/v4/Vxx.wav (no code change).", "direction": COPYDOC["voice_direction"], "lines": len(vo_rows), "words": words, "voiceover": vo_rows}

audio_map = {
 "about": "V5 audio slots and layers (slot paths stay public/voiceover/*/v4 and public/music/*/v4). VO is the hero; music ducks under speech; UI SFX sit below speech; transitions and ambience are separate layers. Each slot plays FINAL, else TEMP, else silence.",
 "fps": 30, "resolve_order": ["final", "temp"],
 "layers": {"vo": {"gain_db": 0}, "music": {"gain_db": -7}, "ui_sfx": {"gain_db": -2}, "transitions": {"gain_db": -4}, "ambience": {"gain_db": -10}},
 "voiceover": [{"id": r["id"], "scene": r["scene"], "start_s": r["start_s"], "end_s": r["end_s"], "ceiling_s": r["ceiling_s"], "text": r["voice_line"], "shows": r["visual"], "final": r["final"], "temp": r["temp"]} for r in vo_rows],
 "music": {"final": "music/final/v4/score.wav", "temp": "music/temp/v4/score.wav", "style": "One continuous score: a low bed, a subtle pulse, precise developer rhythm, warmer human texture, a merged motif, quiet resolution, silence. No stock-corporate, no trailer drums, no 'AI' arpeggios, nothing that competes with a male voice (leave 120–350 Hz and 2–4 kHz open under speech).",
   "sections": [{"id": i, "role": role, "from_s": a, "to_s": b, "brief": br} for i, role, a, b, br in MUSIC_SECTIONS],
   "gain_db": -7, "duck_under_vo_db": -9, "duck_attack_s": 0.15, "duck_release_s": 0.5, "dips": DIPS},
 "sfx": {"style": "Understated, physical, quiet: keys, Enter, trackpad clicks, soft ticks; small precise confirmations; no whooshes on ordinary moves, no booms.", "library": sfx_lib()},
 "ambience": {"temp": "sfx/temp/flow.wav", "final": "sfx/final/flow.wav", "from_s": 14.4, "to_s": 22.4, "gain_db": -32, "why": "temp data-flow texture under S04; muted automatically once the final score is in (the score carries S04)"},
}

_base = next(p for p in ("navislabs_v5_product_surface_map.json", "archive/v4/navislabs_v4_product_surface_map.json", "navislabs_v4_product_surface_map.json") if os.path.isfile(os.path.join(ROOT, p)))
surfaces = json.load(open(os.path.join(ROOT, _base)))
ADDED_SURFACES = [
 {"id": "integrations.expanding", "product": "NavisLabs", "label": "Roadmap — Salesforce · HubSpot · Jira · GitHub · Notion · Zoom · Microsoft 365: shown only in S04, apart from the connected systems, labelled 'Roadmap · coming soon'; never shown as connected, never evidence", "source": "website logos.tsx (status 'soon'); /platform", "claim_status": R},
 {"id": "app.evidenceOpened", "product": "Navis App", "label": "Evidence opened out: six live systems → one customer state", "source": "film graphic over WhyThisDrawer evidence (live systems only)", "claim_status": F},
 {"id": "dev.members", "product": "Navis Developer", "label": "Console › Members: 'Add a member' (Email · Application role · Developer access) → 'Invited'", "source": "Devtool features/settings/InviteMemberForm.tsx, MembersPanel.tsx", "claim_status": PP},
 {"id": "dev.personalWorkspace", "product": "Navis Developer", "label": "Sign-up 'For my organization' / 'For myself' → Personal workspace (Owner; 'A personal workspace holds one member') — Navis Developer does not require an organization", "source": "Devtool features/auth/SignUpForm.tsx; lib/format.ts PERSONAL_WORKSPACE_NOTE; OrganizationPanel.tsx", "claim_status": PP},
 {"id": "dev.workstate", "product": "Navis Developer", "label": "navis workstate checkpoint → next session: NAVIS WORK CONTINUITY restored (SessionStart hook)", "source": "Devtool packages/cli workstate.ts, workstate/restore.ts; CLI not yet on npm", "claim_status": PP},
 {"id": "flow.pipeline", "product": "NavisLabs", "label": "Signals → Memory → Context → Intelligence → Decision → Execution → Outcome (Building) → Learning (Next)", "source": "deck p.5 (Learn: BUILDING); research (outcome ledger designed, learning roadmap)", "claim_status": F},
 {"id": "opening.twoTruths", "product": "NavisLabs", "label": "PEOPLE | AI AGENTS: the person's inbox says the renewal moved to Nov 28; the agent's workflow file still says Nov 14 (the same file the agent later updates in S15)", "source": "film graphic; demo data (navislabs_demo_data.json)", "claim_status": F},
 {"id": "hero.shared", "product": "NavisLabs", "label": "One company · NavisLabs: the Navis App and Navis Developer around one shared organizational context; same fact / source / freshness in both", "source": "film graphic; demo data; deck p.6", "claim_status": F},
 {"id": "moat.ownership", "product": "NavisLabs", "label": "Agent clients change; the company's record (the same facts, with sources and freshness) stays the company's: 'What it knows stays yours' · Company-owned · Model-neutral · Shared by people + agents", "source": "positioning (founder brief); CLIENTS.md for the client list; register.ts ('Navis calls no generative model'); no superiority claim", "claim_status": F},
]
_drop = {"integrations.future_connected", "app.evidenceExploded", "moat.mechanism"} | {x["id"] for x in ADDED_SURFACES}
surf = [x for x in surfaces["surfaces"] if x["id"] not in _drop] + ADDED_SURFACES
for x in surf:
    if x.get("product") == "Navis Application":
        x["product"] = "Navis App"
    if x["id"] == "app.priorities":
        x["data"] = "demo; every chip cites a live system (Gmail, Calendar, Slack, Docs, Meet)"
legend = dict(surfaces["claim_status_legend"])
legend["FUTURE_STATE"] = "intended complete product shown in the film; not live today; labelled on screen and in the end-card disclosure; never evidence in a demonstrated workflow"
legend["ROADMAP"] = "not built or not connected yet; shown only with an explicit 'Roadmap · coming soon' label, never as connected"
surfaces = {"about": "Every product surface the V5 film shows, its real source and claim status.", "claim_status_legend": legend, "surfaces": surf}
_ids = {x["id"]: x for x in surf}
for r in vo_rows:
    r["caption_beats"] = caption_beats(r)
    r["product_claims"] = [{"id": c, "label": _ids[c]["label"], "claim_status": _ids[c]["claim_status"]} for c in LINE_CLAIMS[r["id"]]]

state_machine = {
 "about": "Every interactive control in the film: before → (settle) → click → feedback → after, in absolute seconds. Cursor rule: move, settle (≥0.1 s), click with press feedback (no ring), wait for the UI, hold.",
 "cursor_rules": {"settle_s_min": 0.1, "press": "pointer scale 1 → 0.92 → 1 over 0.12 s", "ring": False, "speed": "arc easeInOut 0.35–0.7 s per move", "hidden": "while evidence is read (drawer → exploded → waiting macro) and in terminal scenes"},
 "interactions": [{"id": x["id"], "product": x["product"], "control": x["control"], "cursor": x["cursor"], "states": [{"state": s, "at_s": round(t, 3), "what": w} for s, t, w in x["states"]]} for x in INTERACTIONS],
}

PLAN = [
 ("S01", "V01–V02", "M1 restrained: near silence", ["SOURCE APPEARING: a soft tick as the person's view and the agent's view appear", "SOURCE APPEARING: a quieter tick as each piece of the truth lands in its system"], "music −9 dB under VO", "0–0.85 s: the voice opens the film", "Let the voice open the film."),
 ("S02", "V03", "M1 restrained", ["CURSOR CLICK ×3 as fragments are copied by hand (very low)"], "music −9 dB under VO", "10.0–10.45 s: breath before NavisLabs (music dip)", "The breath makes the reveal land."),
 ("S03", "V04", "M1 → M2 emergence from 12 s", ["NAVISLABS REVEAL: one low tonal lift on the mark (no hit)", "PRODUCT TRANSITION: soft air on the wipe into the light world"], "music −9 dB under VO", "—", "A brand moment, quiet."),
 ("S04", "V05–V06", "M2 emergence", ["SOURCE APPEARING on each of the six live signals", "CONTEXT RETRIEVAL when memory becomes context", "temp only: data-flow texture (muted once the final score is in)"], "music −9 dB under VO", "—", "Infrastructure, not spectacle."),
 ("S05–S07", "V07–V09", "M3 human / organizational", ["PRODUCT TRANSITION (very soft) as the Navis App opens", "CURSOR CLICK on 'Why this matters'", "SOURCE APPEARING per evidence row", "CONTEXT RETRIEVAL when six sources resolve into one customer state"], "music −9 dB under VO", "—", "Each fact gets a tick, nothing louder."),
 ("S08", "V10–V11", "M3", ["CURSOR CLICK Review & reply / Review draft / select", "KEYBOARD under the person's own sentence"], "music −9 dB under VO", "—", "The person's typing is audible: a human decides."),
 ("S09", "V12", "M3", ["APPROVE: small precise click", "SENDING: soft, short", "GMAIL CONFIRMATION: a single soft tone on 'accepted'"], "music −9 dB under VO", "40.95–41.5 s: held breath after Approve (music dip, no SFX)", "Tiny, exact confirmation — no fanfare."),
 ("S10–S11", "V13–V14", "M4 technical", ["PRODUCT TRANSITION: air on light → dark", "KEYBOARD under the task", "TERMINAL ENTER", "CURSOR CLICK Add member", "MCP CONNECTION: two-tone on '✓ Connected'"], "music −9 dB under VO", "—", "Precise rhythm for developers."),
 ("S12–S13", "V15–V16", "M4", ["CONTEXT RETRIEVAL on the tool call and the API response", "SOURCE APPEARING when cited facts arrive", "KEYBOARD + TERMINAL ENTER on npm install"], "music −9 dB under VO", "—", "Retrieval sounds like a tool, not magic."),
 ("S14", "V17", "M4 → dip", ["PERMISSION DENIED: muted low two-note (quiet)"], "music −18 dB dip under the refusal", "60.45–62.2 s: the refusal sits in near-silence", "Denied should feel quieter, not louder."),
 ("S15", "V18", "M4", ["RUN START on the edit", "RUN COMPLETE when the run row reads Completed"], "music −9 dB under VO", "—", "The record is calm."),
 ("S16", "V19", "M4 → M5 convergence at 68 s", ["CURSOR CLICK 'For myself'", "TERMINAL ENTER on checkpoint", "SAVE on 'Checkpoint recorded'", "CONTEXT RETRIEVAL when the next session restores the work state"], "music −9 dB under VO", "—", "Personal, light."),
 ("S17", "V20–V22", "M5 convergence → M6 conviction at 82 s", ["PRODUCT TRANSITION: soft air as the event reaches both products (One company)"], "music −9 dB under VO", "77.4–81.6 s: no SFX under 'Same facts. Same sources. Same freshness.'", "The two worlds merge; the voice carries it."),
 ("S18", "V23–V26", "M6 conviction → M7 resolve at 94 s", ["no SFX while agent clients change and the company's record holds (the voice carries V24)", "NAVISLABS REVEAL on the end lockup"], "music −9 dB under VO; resolve after V26", "94.1–100 s no SFX; 98.6–100 s total silence", "Reduce motion, reduce sound, brand, silence."),
]
design_plan = {"about": "Sound design plan for the V5 film (V4 picture). Temp SFX/music are placeholders; final VO and score are not generated yet.", "layers": audio_map["layers"], "categories": SFX_CATEGORIES,
 "rules": ["VO is always the hero.", "Music ducks −9 dB under speech (attack 0.15 s, release 0.5 s).", "SFX sit below speech; no whoosh on ordinary moves; no booms on buttons.", "Silence is used on purpose: before NavisLabs, on Approve, under the refusal, at the end.", "No clipping: true peak ≤ −1 dBTP on the mix."],
 "scenes": [{"scene": s, "vo": vo, "music": m, "sfx": sfx, "ducking": duck, "silence": sil, "reason": why} for s, vo, m, sfx, duck, sil, why in PLAN]}

for name, obj in [("navislabs_v5_film_spec.json", spec), ("navislabs_v5_voiceover_screen_map.json", screen_map), ("navislabs_v5_audio_map.json", audio_map), ("navislabs_v5_product_surface_map.json", surfaces), ("interaction_state_machine.json", state_machine), ("navislabs_audio_design_plan.json", design_plan)]:
    json.dump(obj, open(os.path.join(ROOT, name), "w"), indent=2, ensure_ascii=False)

# sanity
prev = None
for s in SCENES:
    if prev: assert abs(prev[2] - s[1]) < 1e-9, (prev, s)
    prev = s
assert SCENES[-1][2] == 100.0
for a, b in zip(VO, VO[1:]):
    assert a[4] <= b[2] + 1e-9, ("ceiling overlaps next line", a[0], b[0])
print("scenes", len(SCENES), "VO", len(vo_rows), "words", words, "shots", len(SHOTS), "surfaces", len(surf), "interactions", len(INTERACTIONS))
