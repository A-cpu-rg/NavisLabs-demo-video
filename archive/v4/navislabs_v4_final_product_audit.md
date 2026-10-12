# NavisLabs launch film V4 — final product audit (picture lock)

Generated 2026-10-05T20:11:42Z by `scripts/build-final-audit.py`.

| READY_FOR_VOICEOVER | READY_FOR_MUSIC | READY_FOR_FINAL_RENDER |
|---|---|---|
| **true** | **true** | **false** |

## 1. FILM STATUS

- **title**: NavisLabs launch film — V4 picture lock
- **format**:
  - **width**: 1920
  - **height**: 1080
  - **fps**: 30
  - **duration_s**: 100
  - **frames**: 3000
- **scenes**: 18
- **voiceover**: 26 lines · 217 words (temp voice)
- **renders**:
| file | size_mb | duration_s | video | audio |
|---|---|---|---|---|
| out/navislabs-v4-picture-lock-1080p.mp4 | 62.1 | 100.011 | h264 1920×1080 30/1 yuv420p | aac 48000 Hz 2 ch |
| out/navislabs-v4-picture-lock-540p.mp4 | 7.6 | 100.011 | h264 960×540 30/1 yuv420p | aac 48000 Hz 2 ch |
- **render_qc**:
  - **file**: out/navislabs-v4-picture-lock-1080p.mp4
  - **size_mb**: 62.1
  - **duration_s**: 100.011
  - **video**:
    - **codec**: h264
    - **width**: 1920
    - **height**: 1080
    - **fps**: 30/1
    - **frames**: 3000
    - **pix_fmt**: yuv420p
    - **color_space**: bt709
  - **near_black_runs_s**:
    -
      - 99.67
      - 99.97
  - **luma_jumps**:
    -
      - 186
      - 6.2
    -
      - 1069
      - 35.63
    -
      - 1452
      - 48.4
    -
      - 1487
      - 49.57
    -
      - 1532
      - 51.07
    -
      - 1572
      - 52.4
    -
      - 1915
      - 63.83
    -
      - 1916
      - 63.87
    -
      - 1917
      - 63.9
    -
      - 1918
      - 63.93
    -
      - 1998
      - 66.6
    -
      - 2024
      - 67.47
    -
      - 2063
      - 68.77
  - **audio**:
    - **seconds**: 100.011
    - **peak**: 0.888
    - **clipped_samples**: 0
    - **integrated_lufs**: -14.36
    - **true_peak_dbtp**: -1.02
    - **lra**: 4.1
  - **vo_rms_db**:
    - **V01**: -14.4
    - **V02**: -14.8
    - **V03**: -13.4
    - **V04**: -13.0
    - **V05**: -13.3
    - **V06**: -13.4
    - **V07**: -13.3
    - **V08**: -15.3
    - **V09**: -14.1
    - **V10**: -15.5
    - **V11**: -16.0
    - **V12**: -16.0
    - **V13**: -12.9
    - **V14**: -13.6
    - **V15**: -14.4
    - **V16**: -16.0
    - **V17**: -15.0
    - **V18**: -14.3
    - **V19**: -13.0
    - **V20**: -13.1
    - **V21**: -13.7
    - **V22**: -16.0
    - **V23**: -13.6
    - **V24**: -15.5
    - **V25**: -13.4
    - **V26**: -12.9
  - **vo_silent_lines**: - none

## 2. PICTURE LOCK STATUS

- **locked**: **true**
- **validators_all_pass**: **true**
- **validators**:
  - **brand**: **true**
  - **entity**: **true**
  - **product_claim**: **true**
  - **integration**: **true**
  - **interaction**: **true**
  - **timeline**: **true**
  - **audio_timing**: **true**
  - **visual_asset**: **true**
  - **data_consistency**: **true**
- **renders_present_and_100s**: **true**
- **render_qc_pass**: **true**
- **rule**: Picture is locked: timing, beats and VO ceilings are frozen; VO and music are recorded to this cut.

## 3. BRAND STATUS

- **pass**: **true**
- **checks**:
  - no 'NAVIS AI' / 'Navis-AI' label on screen, in copy or in VO
  - no 'Navis Labs' (company is one word: NavisLabs)
  - no repository names as product labels ('Devtool')
  - company name is NavisLabs
  - products are Navis Application and Navis Developer
  - tagline is the website headline
  - logo assets exist (mark without tile, dark + light)
- **logo**: NavisLabs mark without its tile (public/images/brand/navislabs-mark-dark.png, -light.png), wordmark set in the site's font; no pill, no glow
- **tagline**: The shared understanding for your organization.
- **never_used**:
  - NAVIS AI
  - NAVIS-AI
  - Navis Labs

## 4. COMPANY NAME

NavisLabs

## 5. PRODUCT NAMES

- **Navis Application**: People · teams — for people
- **Navis Developer**: Developers · AI agents

## 6. ALL PEOPLE USED

| name | role | email | provenance | scenes |
|---|---|---|---|---|
| Abhishek Meena | Founder | abhishek@navislabs.in | REAL_AUTHORIZED | S04, S05, S06, S07, S08, S09, S10, S11, S12, S13, S14, S15, S17 |
| Sam Rivera | Engineer | sam@example.com | SYNTHETIC | S05, S06, S07, S08, S09, S11, S17 |
| Jordan Lee | Head of Operations | jordan.lee@acme.example | SYNTHETIC | S01, S02, S04, S05, S06, S07, S08, S09, S10, S12, S14, S15, S17 |
| Riya | Student developer | riya@example.com | SYNTHETIC | S16 |

## 7. ALL ORGANIZATIONS USED

| name | kind | provenance |
|---|---|---|
| NavisLabs | the company (dogfooding its own products) | REAL_AUTHORIZED |
| Acme Corp | customer | SYNTHETIC |
| Another organization | unnamed generic tenant in the S14 own-scope check | SYNTHETIC |
| Integration vendors (13) and MCP clients (4) | named nominatively as connectors / clients; no partnership implied | REAL_PUBLIC_PRODUCT |

## 8. ALL CUSTOMERS USED

| name | contact | provenance | note |
|---|---|---|---|
| Acme Corp | Jordan Lee | SYNTHETIC | Fictional customer; 'Acme' is the conventional placeholder company. No customer relationship is implied. |

## 9. AUTHORIZATION STATUS OF EACH NAME

| value | provenance | authorized_for_public_video | replacement_if_needed |
|---|---|---|---|
| NavisLabs | REAL_AUTHORIZED | True | — |
| navislabs.in | REAL_AUTHORIZED | True | — |
| Abhishek Meena | REAL_AUTHORIZED | True | — |
| abhishek@navislabs.in | REAL_AUTHORIZED | True | remove the address from screen if not approved for public release |
| abhishekmeena@Abhisheks-MacBook-Pro-8 | REAL_AUTHORIZED | True | a neutral prompt such as 'abhishek@navislabs' |
| Sam Rivera | SYNTHETIC | True | Mulayam Kumar (CTO) — only with his written approval |
| sam@example.com | SYNTHETIC | True | — |
| Jordan Lee | SYNTHETIC | True | — |
| jordan.lee@acme.example | SYNTHETIC | True | — |
| Riya | SYNTHETIC | True | — |
| riya@example.com | SYNTHETIC | True | — |
| Leadership | SYNTHETIC | True | — |
| Revenue | SYNTHETIC | True | — |
| Engineering | SYNTHETIC | True | — |
| Acme Corp | SYNTHETIC | True | — |
| SSO export | SYNTHETIC | True | — |
| Acme renewal workflow | SYNTHETIC | True | — |
| Annual plans keep their current terms; usage-based pricing applies to new accounts only. | SYNTHETIC | True | — |
| Revised terms promised to Acme by Oct 7 — not yet sent. | SYNTHETIC | True | — |
| Updated metrics were promised to the board Thursday | SYNTHETIC | True | — |
| Acme renewal call | SYNTHETIC | True | — |
| Pricing review | SYNTHETIC | True | — |
| Moving our renewal to Nov 28 | SYNTHETIC | True | — |
| Acme order form — annual plan, current terms | SYNTHETIC | True | — |
| Acme account plan | SYNTHETIC | True | — |
| SSO export spec | SYNTHETIC | True | — |
| NavisLabs | SYNTHETIC | True | — |
| thesis-tracker | SYNTHETIC | True | — |
| claude-code (Claude Code) | REAL_PUBLIC_PRODUCT | True | — |
| Update the Acme renewal workflow. | SYNTHETIC | True | — |
| Add usage-based pricing for new accounts. | SYNTHETIC | True | — |
| Riya's workspace | SYNTHETIC | True | — |
| Gmail | REAL_PUBLIC_PRODUCT | True | — |
| Google Calendar | REAL_PUBLIC_PRODUCT | True | — |
| Google Meet | REAL_PUBLIC_PRODUCT | True | — |
| Google Drive | REAL_PUBLIC_PRODUCT | True | — |
| Google Docs | REAL_PUBLIC_PRODUCT | True | — |
| Slack | REAL_PUBLIC_PRODUCT | True | — |
| Salesforce | REAL_PUBLIC_PRODUCT | True | — |
| HubSpot | REAL_PUBLIC_PRODUCT | True | — |
| Jira | REAL_PUBLIC_PRODUCT | True | — |
| GitHub | REAL_PUBLIC_PRODUCT | True | — |
| Notion | REAL_PUBLIC_PRODUCT | True | — |
| Zoom | REAL_PUBLIC_PRODUCT | True | — |
| Microsoft 365 | REAL_PUBLIC_PRODUCT | True | — |
| Claude Code | REAL_PUBLIC_PRODUCT | True | — |
| Cursor | REAL_PUBLIC_PRODUCT | True | — |
| Codex | REAL_PUBLIC_PRODUCT | True | — |
| VS Code | REAL_PUBLIC_PRODUCT | True | — |
| Mulayam Kumar | REAL_PERSON | False | Sam Rivera (SYNTHETIC) stands in until written approval |
| Digantara | REAL_COMPANY | False | Acme Corp (SYNTHETIC) |

## 10. APPLICATION USER MODEL

- **organization**: NavisLabs
- **teams**:
  - Leadership
  - Revenue
  - Engineering
- **user**: Abhishek Meena (Founder)
- **model**: Organization → Teams → Employees → Customers / Projects / Commitments → the systems where the work lives → Navis Application (S05 org intro)
- **what_the_user_does**: Reads Today, opens why, reviews and edits the draft, approves; Navis sends through Gmail.

## 11. DEVELOPER USER MODEL

- **company**: Members with an Application role and explicit Developer access (owner · admin · developer · viewer); agents hold credentials with permissions
- **members**:
  - Abhishek Meena — owner · Active
  - Sam Rivera — developer · Invited
- **agent**: Claude Code (view_memory, view_state)
- **solo**: Riya — personal workspace 'Riya's workspace' (Owner)

## 12. ORGANIZATION WORKFLOW

| at_s | step |
|---|---|
| 22.6 | Organization → teams → people → customers · projects · commitments → live systems |
| 24.85 | Today at a glance |
| 26.6 | What changed |
| 29.9 | Why this matters (click) |
| 30.3 | Source · timeline · freshness per signal |
| 31.75 | Evidence opened out: six live systems → one customer state |
| 34.2 | Waiting on you |
| 35.5 | Review & reply (click) → draft |
| 37.5 | Edit: select the sentence, type the change |
| 40.95 | Approve & send (click) |
| 42.8 | Execution: Sending… → Gmail accepted → Reply sent |
| 43.1 | Proof rail: Gmail confirmation |

## 13. SOLO DEVELOPER WORKFLOW

| at_s | step |
|---|---|
| 66.6 | Sign up |
| 67.05 | 'For myself' (click) |
| 67.45 | Personal workspace · Owner |
| 68.75 | navis workstate checkpoint |
| 69.55 | Checkpoint recorded |
| 70.45 | Next session |
| 70.8 | NAVIS WORK CONTINUITY restored |
| 71.15 | Task · decisions · open |

## 14. TEAM / INVITE WORKFLOW

-
  - **at_s**: 48.4
  - **step**: Console › Members
-
  - **at_s**: 48.85
  - **step**: Add member (click)
-
  - **at_s**: 49.05
  - **step**: Row: Invited
-
  - **source**: Devtool/apps/dashboard/src/features/settings/InviteMemberForm.tsx L119, L190; MembersPanel.tsx L179
-
  - **source**: MembersPanel.tsx L146

## 15. MCP WORKFLOW

| at_s | step |
|---|---|
| 49.55 | claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> -- node …/stdio.js |
| 50.1 | claude mcp list |
| 50.6 | ✓ Connected |
| 52.45 | navis_get_relevant_context |
| 52.95 | 5 facts with source and freshness |
| 55.3 | The agent reasons; Navis calls no model |

## 16. API WORKFLOW

| at_s | step |
|---|---|
| 57.2 | curl -s "$NAVIS_BASE_URL/developer/context" -H "X-API-Key: $NAVIS_API_KEY" |
| 57.55 | items · sources · freshness |
| 58 | No model is called · Navis grounds · your agent reasons |

## 17. SDK WORKFLOW

| at_s | step |
|---|---|
| 55.9 | npm install ./navis-sdk-0.1.0.tgz (local package · not on npm yet) |
| 56.45 | added 1 package |
| 56.55 | new Navis({ apiKey: process.env.NAVIS_API_KEY }) |

## 18. CLI WORKFLOW

| at_s | step |
|---|---|
| 68.75 | navis workstate checkpoint --objective … --decision … --open … |
| 70.8 | SessionStart hook restores the work state |

## 19. RUN / CONSOLE WORKFLOW

| at_s | step |
|---|---|
| 62.25 | The agent edits the workflow file |
| 63 | Done |
| 63.75 | Console › Runs |
| 64.4 | Open run (click) |
| 64.65 | Timeline: Context · Tool · Tool · Tool · Outcome with times |
| 65.85 | Outcome: Not judged; economics '—' |

## 20. APPLICATION DATA FLOW

Gmail · Calendar · Meet · Drive · Docs · Slack signals → NavisLabs memory and context → Today priority with sources and freshness → draft → a person approves → Gmail sends → reply sent.

## 21. DEVELOPER DATA FLOW

Agent (Claude Code) → MCP / API / SDK with the organization's key → navis_get_relevant_context → facts with source and freshness (organization from the key) → the agent reasons and edits code → the run is recorded in the Console.

## 22. SHARED DATA FLOW

- **S04**: Signals → Memory → Context → Intelligence → Decision → Execution → Outcome (Building) → Learning (Next)
- **S17**: One organization · NavisLabs: one shared organizational context feeds Navis Application (people · teams) and Navis Developer (developers · AI agents) — same fact, same source, same freshness
- **consistency**:
  - **customer_in_both_products**: **true**
  - **decision_in_both_products**: **true**
  - **commitment_in_both_products**: **true**
  - **run_steps_cite_live_systems_only**: **true**
  - **run_window**: 09:44:03 → 09:48:15 (4m 12s)
  - **updates_tile_is_zero**: **true**

## 23. LIVE INTEGRATIONS

| id | semantic |
|---|---|
| gmail | customer response |
| calendar | meeting & commitment |
| meet | discussion & decision |
| drive | project documents |
| docs | account context |
| slack | team signal |

## 24. EXPANDING ECOSYSTEM

- **label**: Expanding ecosystem · rolling out
- **where**: S04 only, dashed, apart from the live column; never evidence
- **systems**:
| id | semantic |
|---|---|
| salesforce | account context |
| hubspot | customer activity |
| jira | project state |
| github | code activity |
| notion | organizational knowledge |
| zoom | meeting signal |
| microsoft365 | work context |

## 25. CURRENT VS TARGET-STATE CLAIMS

- **legend**:
  - **PROVEN**: verified in the product source / live site
  - **PRIVATE_PREVIEW**: implemented, not publicly released (packages unpublished, nothing hosted publicly)
  - **DESIGNED**: implemented or designed, not yet proven in production use
  - **ROADMAP**: not built yet; shown only with an explicit label
  - **FILM_SIMULATION**: a film graphic or demo data, not a product claim
  - **FUTURE_STATE**: intended complete product shown in the film; not live today; labelled on screen ('Expanding ecosystem · rolling out') and in the end-card disclosure; never evidence in a demonstrated workflow
- **by_status**:
  - **PROVEN**:
    - LIVE_CURRENT — Gmail · Google Calendar · Google Meet · Google Drive · Google Docs · Slack
    - NavisLabs mark without its tile (dark + light-ground variants) and the wordmark
    - The shared understanding for your organization.
    - Today · Navis — Good morning, <name>.
    - Today at a glance: Decisions · Risks · Actions today · Meetings · Waiting on you · Updates
    - What changed · Verified shifts only (learning narratives only)
    - NarrativeCard: kind label, Next, Review & reply / Mark decided / Ask Navis / Snooze / Why this matters
    - Why Navis surfaced this: What's happening / Who this is about / Why it matters / What supports this / What you can do
    - Waiting on you — 1 thing is waiting on you · 1 person is waiting on your reply
    - Preparing the draft… · Why this · To / Subject / Message · Approve & send · Saved / Save changes
    - Claude Code (LIVE VERIFIED, real Claude.app icon) · Cursor / Codex / VS Code (CONFIG VERIFIED, text only) · Any MCP client
    - No model is called · Navis grounds · your agent reasons
    - Your attention: Revenue at risk · Delivery blocked · Commitment due
  - **DESIGNED**:
    - Approved — sending · Sending… · Reply sent · Gmail accepted the message.
    - Runs: Task · Agent · Status · Started · Duration · CLI session
    - Run — What happened · Timeline (# · Type · What · Status · Model · Tokens · Cost · Latency; types Context/Tool/Model/Outcome) · Outcome ('Not judged')
  - **PRIVATE_PREVIEW**:
    - Overview · Agents · Context · Policies · API · SDKs · API keys · MCP · Runs · Outcomes · Economics · Learning · Memory · State
    - MCP — claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> -- node <repo>/services/mcp-server/dist/stdio.js
    - Developer API — POST /developer/context (navis_get_relevant_context, view_memory)
    - SDKs — TypeScript @navis/sdk (installToday: npm install ./navis-sdk-0.1.0.tgz), Python navis-sdk (wheel); unpublished
    - CLI — navis status · navis hook <event> · navis workstate checkpoint · navis workstate show · navis config show
    - items (kind, text, source, occurred_at) · freshness (as_of, newest_fact_at) · sources.detail (auth_state, last_success_at)
    - Credential permissions checked server-side on every request; exact view_memory refusal
    - claude mcp add navis … / claude mcp list → ✓ Connected
    - X-API-Key: navis_… — the organization comes from the key, never a parameter
    - A key only reads its own organization ('OWN SCOPE')
    - Console › Members: 'Add a member' (Email · Application role · Developer access) → 'Invited'
    - Sign-up 'For myself' → Personal workspace (Owner; 'A personal workspace holds one member')
    - navis workstate checkpoint → next session: NAVIS WORK CONTINUITY restored (SessionStart hook)
  - **ROADMAP**:
    - Central policy enforcement — 'Not enabled yet'
  - **FUTURE_STATE**:
    - Expanding ecosystem — Salesforce · HubSpot · Jira · GitHub · Notion · Zoom · Microsoft 365, shown only in S04 with 'Expanding ecosystem · rolling out'; never evidence in a workflow
  - **FILM_SIMULATION**:
    - Evidence opened out: six live systems → one customer state
    - More systems → more signals → more entities resolved → more decisions & commitments connected → more history → better understanding → more useful
    - Signals → Memory → Context → Intelligence → Decision → Execution → Outcome (building) → Learning (next)

## 26. EVERY BUTTON AUDITED

- **pressed**:
| control | product | states |
|---|---|---|
| Why this matters (link) | Navis Application | before 28.6s, settle 29.78s, click 29.9s, feedback 30.0s, after 30.3s |
| Review & reply (button) | Navis Application | before 35.0s, settle 35.38s, click 35.5s, feedback 35.6s, after 35.98s |
| Review draft (button) | Navis Application | before 35.7s, settle 35.9s, click 36.0s, feedback 36.05s, after 36.5s |
| message body (text selection + typing) | Navis Application | before 37.0s, settle 37.36s, click 37.5s, feedback 37.95s, after 39.288s |
| Approve & send (button) | Navis Application | before 39.85s, settle 40.5s, click 40.95s, feedback 41.15s, after 42.8s |
| Add member (button, Console › Members) | Navis Developer | before 48.4s, settle 48.73s, click 48.85s, feedback 49.05s, after 49.35s |
| terminal: claude mcp add / claude mcp list | Navis Developer | before 49.55s, click 49.6s, feedback 49.85s, after 50.6s |
| MCP tool call navis_get_relevant_context | Navis Developer | before 52.45s, feedback 52.95s, after 53.65s |
| request → authorization | Navis Developer | before 58.85s, feedback 59.45s, feedback2 59.9s, after 60.35s |
| Runs row → Run page | Navis Developer | before 63.75s, feedback 63.9s, click 64.4s, after 64.65s |
| Sign up: 'For myself' workspace option | Navis Developer | before 66.6s, settle 66.93s, click 67.05s, feedback 67.17s, after 67.45s |
| terminal: navis workstate checkpoint | Navis Developer | before 68.75s, feedback 69.55s, after 70.45s |
- **visible_not_pressed**:
  -
    - **control**: Mark decided · Ask Navis · Snooze
    - **where**: S06 priority card
    - **source**: Navis-AI NarrativeCard.tsx
    - **pressed**: **false**
  -
    - **control**: Start my day · Refresh workspace
    - **where**: S05 Today
    - **source**: Navis-AI DailyBriefHero.tsx
    - **pressed**: **false**
  -
    - **control**: Save changes · Rewrite · Ignore
    - **where**: S08 draft
    - **source**: Navis-AI DraftReviewPanel.tsx
    - **pressed**: **false**
    - **note**: 'Saved' → 'Save changes' state change shown after the edit
  -
    - **control**: Console navigation (Overview … State)
    - **where**: S11, S15, S16
    - **source**: Devtool lib/navigation.ts
    - **pressed**: **false**
  -
    - **control**: For my organization
    - **where**: S16 sign-up
    - **source**: Devtool SignUpForm.tsx
    - **pressed**: **false**

## 27. EVERY CURSOR INTERACTION AUDITED

- **rules**:
  - **settle_s_min**: 0.1
  - **press**: pointer scale 1 → 0.92 → 1 over 0.12 s
  - **ring**: **false**
  - **speed**: arc easeInOut 0.35–0.7 s per move
  - **hidden**: while evidence is read (drawer → exploded → waiting macro) and in terminal scenes
- **interactions**:
| id | settle_to_click_s |
|---|---|
| why_this_matters | 0.12 |
| review_and_reply | 0.12 |
| review_draft | 0.1 |
| edit_sentence | 0.14 |
| approve_and_send | 0.45 |
| add_member | 0.12 |
| for_myself | 0.12 |
- **validator**: **true**

## 28. CAMERA MOVEMENTS AUDITED

- **model**: wide → medium → macro → wide; hard cuts between framings; drifts while reading; glides only to follow information
- **motion_blur**: CameraMotionBlur (6 samples, 180°) only on frames where the camera moves faster than 14 px/frame; samples look forward within the frame so hard cuts never ghost
- **scenes**:
  -
    - **scene**: S01
    - **keyframes**: 4
    - **hard_cuts**: - none
    - **glides**: 1
    - **drifts**: 3
    - **scale_range**:
      - 0.85
      - 1.0
    - **language**: wide
  -
    - **scene**: S02
    - **camera**: static frame (no camera keyframes)
    - **keyframes**: 0
  -
    - **scene**: S03
    - **camera**: static frame (no camera keyframes)
    - **keyframes**: 0
  -
    - **scene**: S04
    - **keyframes**: 8
    - **hard_cuts**: - none
    - **glides**: 3
    - **drifts**: 5
    - **scale_range**:
      - 0.655
      - 1.0
    - **language**: wide
  -
    - **scene**: S05
    - **keyframes**: 6
    - **hard_cuts**:
      - Today at a glance
      - Your attention
    - **glides**: 0
    - **drifts**: 6
    - **scale_range**:
      - 0.86
      - 1.52
    - **language**: medium
  -
    - **scene**: S06
    - **keyframes**: 5
    - **hard_cuts**:
      - What changed
      - the customer priority
    - **glides**: 2
    - **drifts**: 3
    - **scale_range**:
      - 1.42
      - 2.0
    - **language**: macro
  -
    - **scene**: S07
    - **keyframes**: 6
    - **hard_cuts**: - none
    - **glides**: 4
    - **drifts**: 2
    - **scale_range**:
      - 1.0
      - 1.72
    - **language**: medium
  -
    - **scene**: S08
    - **keyframes**: 12
    - **hard_cuts**:
      - Waiting on you
      - back to the customer card
    - **glides**: 6
    - **drifts**: 6
    - **scale_range**:
      - 1.1
      - 2.15
    - **language**: macro
  -
    - **scene**: S09
    - **keyframes**: 6
    - **hard_cuts**: - none
    - **glides**: 3
    - **drifts**: 3
    - **scale_range**:
      - 0.86
      - 2.02
    - **language**: macro
  -
    - **scene**: S10
    - **keyframes**: 6
    - **hard_cuts**: - none
    - **glides**: 2
    - **drifts**: 4
    - **scale_range**:
      - 0.86
      - 1.6
    - **language**: medium
  -
    - **scene**: S11
    - **keyframes**: 7
    - **hard_cuts**:
      - terminal
      - Console › Connect
    - **glides**: 0
    - **drifts**: 7
    - **scale_range**:
      - 1.08
      - 1.33
    - **language**: medium
  -
    - **scene**: S12
    - **keyframes**: 10
    - **hard_cuts**:
      - back to the agent
    - **glides**: 4
    - **drifts**: 6
    - **scale_range**:
      - 1.5
      - 2.02
    - **language**: macro
  -
    - **scene**: S13
    - **keyframes**: 4
    - **hard_cuts**: - none
    - **glides**: 1
    - **drifts**: 3
    - **scale_range**:
      - 1.3
      - 1.32
    - **language**: medium
  -
    - **scene**: S14
    - **keyframes**: 2
    - **hard_cuts**: - none
    - **glides**: 0
    - **drifts**: 2
    - **scale_range**:
      - 1.0
      - 1.02
    - **language**: wide
  -
    - **scene**: S15
    - **keyframes**: 8
    - **hard_cuts**:
      - the diff
      - what it relied on
      - the run
    - **glides**: 0
    - **drifts**: 8
    - **scale_range**:
      - 1.16
      - 1.58
    - **language**: medium
  -
    - **scene**: S16
    - **keyframes**: 9
    - **hard_cuts**:
      - personal workspace
      - terminal
      - next session
    - **glides**: 1
    - **drifts**: 8
    - **scale_range**:
      - 1.08
      - 1.43
    - **language**: medium
  -
    - **scene**: S17
    - **keyframes**: 12
    - **hard_cuts**:
      - same fact
      - same source
      - same freshness
      - all three
    - **glides**: 2
    - **drifts**: 10
    - **scale_range**:
      - 0.95
      - 1.215
    - **language**: medium
  -
    - **scene**: S18
    - **camera**: static frame (no camera keyframes)
    - **keyframes**: 0

## 29. ZOOM IN / OUT AUDITED

| scene | scale_range | language |
|---|---|---|
| S01 | 0.85, 1.0 | wide |
| S02 | — | static |
| S03 | — | static |
| S04 | 0.655, 1.0 | wide |
| S05 | 0.86, 1.52 | medium |
| S06 | 1.42, 2.0 | macro |
| S07 | 1.0, 1.72 | medium |
| S08 | 1.1, 2.15 | macro |
| S09 | 0.86, 2.02 | macro |
| S10 | 0.86, 1.6 | medium |
| S11 | 1.08, 1.33 | medium |
| S12 | 1.5, 2.02 | macro |
| S13 | 1.3, 1.32 | medium |
| S14 | 1.0, 1.02 | wide |
| S15 | 1.16, 1.58 | medium |
| S16 | 1.08, 1.43 | medium |
| S17 | 0.95, 1.215 | medium |
| S18 | — | static |

## 30. TRANSITIONS AUDITED

-
  - **from**: S01
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: The answer exists, scattered
-
  - **from**: S02
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: People rebuild; agents start empty
-
  - **from**: S03
  - **transition_out**:
    - **type**: wipe
    - **frames**: 27
    - **direction**: from-bottom
  - **why**: NavisLabs and its two products
-
  - **from**: S04
  - **transition_out**:
    - **type**: fade
    - **frames**: 18
    - **direction**: None
  - **why**: Signals → memory → context → intelligence → decision → execution → outcome → learning
-
  - **from**: S05
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: An organization opens Navis Application
-
  - **from**: S06
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: Priorities → what changed → the Acme priority
-
  - **from**: S07
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: Why: source, timeline, freshness → one customer state
-
  - **from**: S08
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: Waiting on you → draft → the person edits
-
  - **from**: S09
  - **transition_out**:
    - **type**: wipe
    - **frames**: 18
    - **direction**: from-top
  - **why**: Approve & send → Gmail accepted → reply sent
-
  - **from**: S10
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: Same organization: the engineering side
-
  - **from**: S11
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: Invite the team → connect over MCP → four surfaces
-
  - **from**: S12
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: Cited facts, with freshness
-
  - **from**: S13
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: SDK and API; the model stays the agent's
-
  - **from**: S14
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: Authorized / own scope / denied
-
  - **from**: S15
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: The work, and the run on record
-
  - **from**: S16
  - **transition_out**:
    - **type**: fade
    - **frames**: 18
    - **direction**: None
  - **why**: Solo developer: personal workspace, work state carries over
-
  - **from**: S17
  - **transition_out**:
    - **type**: fade
    - **frames**: 18
    - **direction**: None
  - **why**: One organization, two products, one shared context
-
  - **from**: S18
  - **transition_out**:
    - **type**: none
    - **frames**: 0
    - **direction**: None
  - **why**: What stays; NavisLabs

## 31. SOUND EFFECT PLAN

- **categories**:
  - KEYBOARD
  - TERMINAL ENTER
  - MCP CONNECTION
  - CONTEXT RETRIEVAL
  - SOURCE APPEARING
  - CURSOR CLICK
  - PERMISSION DENIED
  - SAVE
  - APPROVE
  - SENDING
  - GMAIL CONFIRMATION
  - RUN START
  - RUN COMPLETE
  - PRODUCT TRANSITION
  - NAVISLABS REVEAL
- **rules**:
  - VO is always the hero.
  - Music ducks −9 dB under speech (attack 0.15 s, release 0.5 s).
  - SFX sit below speech; no whoosh on ordinary moves; no booms on buttons.
  - Silence is used on purpose: before NavisLabs, on Approve, under the refusal, at the end.
  - No clipping: true peak ≤ −1 dBTP on the mix.
- **layers**:
  - **vo**:
    - **gain_db**: 0
  - **music**:
    - **gain_db**: -7
  - **ui_sfx**:
    - **gain_db**: -2
  - **transitions**:
    - **gain_db**: -4
  - **ambience**:
    - **gain_db**: -10
- **events**:
  - **air**: 4
  - **approve**: 1
  - **brand**: 2
  - **click**: 9
  - **confirm**: 2
  - **connect**: 1
  - **deny**: 1
  - **enter**: 5
  - **gmail**: 1
  - **key**: 24
  - **key2**: 11
  - **key3**: 12
  - **retrieve**: 4
  - **run**: 1
  - **save**: 1
  - **select**: 18
  - **sent**: 1
- **status**: temp SFX (synthesized placeholders)

## 32. MUSIC PLAN

- **style**: One continuous score: a low bed, a subtle pulse, precise developer rhythm, warmer human texture, a merged motif, quiet resolution, silence. No stock-corporate, no trailer drums, no 'AI' arpeggios, nothing that competes with a male voice (leave 120–350 Hz and 2–4 kHz open under speech).
- **sections**:
| id | role | from_s | to_s | brief |
|---|---|---|---|---|
| M1 | restrained | 0.0 | 12.0 | restrained, almost silent: a low bed; the NavisLabs reveal at 10.5 s is carried by silence and one tonal SFX |
| M2 | emergence | 12.0 | 22.0 | subtle brand emergence under the products and the data flow |
| M3 | human | 22.0 | 45.0 | human / organizational: warm, unhurried, the person's decision |
| M4 | technical | 45.0 | 68.0 | technical developer momentum: precise, light rhythm |
| M5 | convergence | 68.0 | 82.0 | convergence: the human and technical motifs meet; shared understanding |
| M6 | conviction | 82.0 | 94.0 | conviction / moat: steady, grounded, no riser |
| M7 | resolve | 94.0 | 100.0 | resolution under the end card, then silence |
- **dips**:
| from_s | to_s | db | why |
|---|---|---|---|
| 10.0 | 10.5 | -96 | breath before NavisLabs |
| 40.95 | 41.2 | -96 | held breath on Approve & send |
| 60.9 | 62.1 | -18 | the refusal: quieter, not louder |
| 98.6 | 100.0 | -96 | silent end |
- **duck_under_vo_db**: -9
- **status**: brief only; temp bed in the picture lock; final score not generated

## 33. VO PREPARATION

- **lines**: 26
- **words**: 217
- **elevenlabs_fields**:
  - text
  - audio_tag
  - emotion
  - delivery
  - pace
  - pause
  - pronunciation
  - max_duration_s
  - visual_moment
- **audio_tags_used**: 8
- **final_paths**: public/voiceover/final/v4/V01–V26.wav
- **final_present**: - none
- **key**: ELEVENLABS_API_KEY from the environment only; never in JSON
- **voice**: the founder's own voice, with his permission, if cloned
- **lines_detail**:
| id | start_s | ceiling_s | max_duration_s | voice_line |
|---|---|---|---|---|
| V01 | 0.6 | 3.0 | 2.4 | Your company already has the answer. |
| V02 | 3.1 | 6.3 | 3.2 | It's scattered across the systems where work happens. |
| V03 | 6.6 | 10.2 | 3.6 | People rebuild it by hand. Agents start without it. |
| V04 | 10.6 | 14.4 | 3.8 | NavisLabs turns those signals into one shared understanding. |
| V05 | 14.6 | 18.3 | 3.7 | Every email, meeting, document and message becomes a signal — |
| V06 | 18.4 | 22.5 | 4.1 | remembered, connected, and turned into what should happen next. |
| V07 | 22.8 | 26.5 | 3.7 | Inside an organization, Navis Application is for people. |
| V08 | 26.8 | 29.6 | 2.8 | It shows what changed — Acme's renewal moved. |
| V09 | 29.9 | 34.3 | 4.4 | And why: every fact with its source, its time, and how fresh it is. |
| V10 | 34.5 | 37.7 | 3.2 | It's waiting on you, so Navis drafts the reply. |
| V11 | 37.8 | 40.2 | 2.4 | A person decides. |
| V12 | 41.2 | 44.6 | 3.4 | Then the company acts. |
| V13 | 45.0 | 48.4 | 3.4 | The same organization's agents use Navis Developer. |
| V14 | 48.5 | 52.4 | 3.9 | Invite the team. Connect once — MCP, API, SDK or CLI. |
| V15 | 52.5 | 55.9 | 3.4 | The agent asks — and gets cited facts, with their freshness. |
| V16 | 56.0 | 58.9 | 2.9 | Navis isn't the model. It supplies the company's truth. |
| V17 | 59.0 | 62.1 | 3.1 | Every request is checked against its permissions. |
| V18 | 62.4 | 66.5 | 4.1 | The agent does the work, and the run is on record. |
| V19 | 66.8 | 73.2 | 6.4 | A solo builder gets a private workspace — and the work state carries into the next session. |
| V20 | 73.6 | 77.6 | 4.0 | One organization. The person and the agent acted on the same event. |
| V21 | 77.7 | 81.3 | 3.6 | Same facts. Same sources. Same freshness. |
| V22 | 81.4 | 84.2 | 2.8 | One understanding. Two ways in. |
| V23 | 84.4 | 88.3 | 3.9 | Models change. Agents change. Tools change. |
| V24 | 88.4 | 90.3 | 1.9 | Your company keeps its history. |
| V25 | 90.4 | 94.0 | 3.6 | Company-owned. Model-neutral. Shared by people and agents. |
| V26 | 94.2 | 98.4 | 4.2 | NavisLabs. The shared understanding for your organization. |

## 34. UNSUPPORTED CLAIMS

- **found**: - none
- **validator_product_claim**: **true**
- **avoided**:
  - no npm install @navis/sdk shown as working
  - no public base URL
  - no real key
  - no economics numbers
  - no outcome judgement
  - no Cursor/Codex/VS Code shown as live

## 35. SIMULATED UI

- **how**: Every product screen is rebuilt in React from the real source (src/ui/evidence.ts lists file, source and verbatim strings); no screen recordings
- **film_graphics**:
  - Evidence opened out: six live systems → one customer state
  - More systems → more signals → more entities resolved → more decisions & commitments connected → more history → better understanding → more useful
  - Signals → Memory → Context → Intelligence → Decision → Execution → Outcome (building) → Learning (next)
- **demo_data**: all customer, project, run and solo-developer data is SYNTHETIC (src/data/navislabs_demo_data.json)

## 36. FUTURE FEATURES

- **future_state**:
  - Expanding ecosystem — Salesforce · HubSpot · Jira · GitHub · Notion · Zoom · Microsoft 365, shown only in S04 with 'Expanding ecosystem · rolling out'; never evidence in a workflow
- **roadmap**:
  - Central policy enforcement — 'Not enabled yet'
- **in_pipeline**:
  - Outcome (Building)
  - Learning (Next)
- **shown_as_live**: - none

## 37. FILES CREATED

- README.md
- developer_capability_audit.json
- interaction_state_machine.json
- navislabs_audio_design_plan.json
- navislabs_entity_audit.json
- navislabs_entity_consistency.json
- navislabs_v4_audio_production_plan.json
- navislabs_v4_audio_readiness_report.md
- navislabs_v4_final_product_audit.json
- navislabs_v4_final_product_audit.md
- navislabs_v4_music_production_brief.json
- navislabs_v4_render_check.json
- navislabs_v4_sfx_map.json
- navislabs_v4_validation_report.json
- public/music/temp/v4/score.wav
- public/sfx/temp/approve.wav
- public/sfx/temp/brand.wav
- public/sfx/temp/connect.wav
- public/sfx/temp/flow.wav
- public/sfx/temp/gmail.wav
- public/sfx/temp/retrieve.wav
- public/sfx/temp/save.wav
- public/voiceover/temp/v4/V01.wav
- public/voiceover/temp/v4/V02.wav
- public/voiceover/temp/v4/V03.wav
- public/voiceover/temp/v4/V04.wav
- public/voiceover/temp/v4/V05.wav
- public/voiceover/temp/v4/V06.wav
- public/voiceover/temp/v4/V07.wav
- public/voiceover/temp/v4/V08.wav
- public/voiceover/temp/v4/V09.wav
- public/voiceover/temp/v4/V10.wav
- public/voiceover/temp/v4/V11.wav
- public/voiceover/temp/v4/V12.wav
- public/voiceover/temp/v4/V13.wav
- public/voiceover/temp/v4/V14.wav
- public/voiceover/temp/v4/V15.wav
- public/voiceover/temp/v4/V16.wav
- public/voiceover/temp/v4/V17.wav
- public/voiceover/temp/v4/V18.wav
- public/voiceover/temp/v4/V19.wav
- public/voiceover/temp/v4/V20.wav
- public/voiceover/temp/v4/V21.wav
- public/voiceover/temp/v4/V22.wav
- public/voiceover/temp/v4/V23.wav
- public/voiceover/temp/v4/V24.wav
- public/voiceover/temp/v4/V25.wav
- public/voiceover/temp/v4/V26.wav
- scripts/build-audio-production.py
- scripts/build-final-audit.py
- scripts/build-v4-audits.py
- scripts/build-v4-data.py
- scripts/check-render.py
- scripts/dump-config.mjs
- scripts/film_analysis.py
- scripts/validate-film.py
- src/components/Cursor.tsx
- src/compositions/NavisLaunch.tsx
- src/config/loadBlueprint.ts
- src/config/timeline.ts
- src/data/navislabs_demo_data.json
- src/film/DataFlow.tsx
- src/film/OrgIntro.tsx
- src/scenes/AppFlow.tsx
- src/scenes/S15.tsx
- src/scenes/S16.tsx
- src/scenes/S17.tsx
- src/scenes/S18.tsx
- src/ui/demoContent.ts
- src/ui/developer/Console.tsx
- team_permission_audit.json
- out/navislabs-v4-picture-lock-1080p.mp4
- out/navislabs-v4-picture-lock-540p.mp4

## 38. FILES MODIFIED

- navislabs_v4_audio_map.json
- navislabs_v4_film_spec.json
- navislabs_v4_product_surface_map.json
- navislabs_v4_voiceover_screen_map.json
- package.json
- public/sfx/temp/air.wav
- public/sfx/temp/click.wav
- public/sfx/temp/confirm.wav
- public/sfx/temp/deny.wav
- public/sfx/temp/enter.wav
- public/sfx/temp/key.wav
- public/sfx/temp/key2.wav
- public/sfx/temp/key3.wav
- public/sfx/temp/notify.wav
- public/sfx/temp/run.wav
- public/sfx/temp/select.wav
- public/sfx/temp/sent.wav
- scripts/make-temp-audio.py
- src/components/AudioLayer.tsx
- src/components/Camera.tsx
- src/config/audioMap.ts
- src/config/beats.ts
- src/config/filmSpec.ts
- src/config/navisBrand.ts
- src/config/types.ts
- src/config/validateSpec.ts
- src/film/CodeEditor.tsx
- src/film/EvidenceExploded.tsx
- src/film/ProductSplit.tsx
- src/scenes/DevFlow.tsx
- src/scenes/S01.tsx
- src/scenes/S02.tsx
- src/scenes/S03.tsx
- src/scenes/S04.tsx
- src/scenes/S05.tsx
- src/scenes/S06.tsx
- src/scenes/S07.tsx
- src/scenes/S08.tsx
- src/scenes/S09.tsx
- src/scenes/S10.tsx
- src/scenes/S11.tsx
- src/scenes/S12.tsx
- src/scenes/S13.tsx
- src/scenes/S14.tsx
- src/scenes/index.ts
- src/ui/application/TodayDashboard.tsx
- src/ui/application/WhyThisDrawer.tsx
- src/ui/developer/Context.tsx
- src/ui/developer/SdkApi.tsx
- src/ui/developer/WorkState.tsx
- src/ui/evidence.ts

## 39. FILES NOT TOUCHED

- **read_only_repositories**:
  - ~/Desktop/Devtool
  - ~/Desktop/Navis-AI
  - ~/Desktop/Backend
  - ~/Desktop/navis-labs-website
- **protected_json**:
  - navis_code_audit.json
  - navis_master_cinematic_launch_spec.json
  - navis_launch_production_blueprint.json
- **protected_json_unchanged**: **true**
- **never_opened**:
  - Devtool/.claude/settings.local.json
  - Navis-AI .env*

## 40. REMAINING BLOCKERS

- Final founder VO: record or generate V01–V26 to the ceilings (ElevenLabs with the founder's own voice, with his permission); drop files into public/voiceover/final/v4/.
- Final music: score to the arc in navislabs_audio_design_plan.json; drop into public/music/final/v4/score.wav.
- Confirm public display of the founder's email and Mac user/host (or switch to the neutral prompt listed in the entity audit).
- Optional: written approval before replacing the SYNTHETIC engineer with Mulayam Kumar.
- Legal check of nominative vendor marks (13 integrations, Claude Code icon) before public release.
- 4K master (npm run render:4k) after final VO and music.

## 41. FINAL RECOMMENDATION

- **decision**: Lock picture. Record the founder VO to the ceilings in navislabs_v4_voiceover_screen_map.json and commission the score from the music brief; then mix and render the 4K master.
- **creative_test**:
  - **muted**: The UI carries the story without narration: one customer event, its evidence, a human approval and a sent reply; then the same facts reaching an agent with source and freshness.
  - **audio_only**: The VO script states the problem, the shared understanding, both products and the ending line; the temp voice is a placeholder.
  - **serious_company**: Real product strings and flows from the source, real commands with placeholders, no invented metrics; future systems labelled.

## 42. READY_FOR_VOICEOVER

**true**

## 43. READY_FOR_MUSIC

**true**

## 44. READY_FOR_FINAL_RENDER

**false**
