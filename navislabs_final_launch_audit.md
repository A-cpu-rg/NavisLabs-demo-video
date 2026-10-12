# NavisLabs launch film — final launch audit (V8 final-audio candidate)

Review renders: `out/navislabs-final-audio-review-1080p.mp4` · `out/navislabs-final-audio-review-540p.mp4` — 125.23 s, 3757 frames. The V7 master is untouched (`out/navislabs-v7-review-1080p.mp4`). No 4K.

## Readiness

| Flag | Value | Why |
|---|---|---|
| VOICEOVER_READY | **TRUE** | P1–P8 are the founder's files, unchanged (hashes below); every line placed on the measured performance; captions from the measured voice. |
| PICTURE_READY | **TRUE** | 12 validators pass; frame review and sharpness scan reviewed; dates, names and labels corrected. |
| MUSIC_READY | **FALSE** | The founder-supplied Eleven Music track is in the film (VERIFIED IN PROVIDED ASSET), but its licence tier is NOT VERIFIED (it depends on the ElevenLabs plan it was generated on — free-tier tracks must credit ElevenMusic), and it needs the founder's listening approval in the final mix. |
| SFX_READY | **FALSE** | All SFX are in-project synthesized placeholders (TEMPORARY). No ElevenLabs SFX were supplied and ELEVENLABS_API_KEY is not set, so none were generated. |
| DATA_READY | **TRUE** | Every visible entity comes from one launch-state file; the customer is a labelled fictional demo organization; all dates validated against Oct 6, 2026. |
| INTEGRATIONS_READY | **TRUE** | Six live integrations VERIFIED IN CODE (local Navis backend); seven labelled 'upcoming' on screen and in the disclosure (ROADMAP / demo configuration); no action shown executed through them. |
| AUDIO_QC | **TRUE** | Measured on the master and stems: −14 LUFS, ≤ −1 dBTP, no clipping, no unexpected silence or jumps, voice dominant, A/V in sync. |
| VISUAL_QC | **TRUE** | 3757/3757 frames, no stray black frames, readable camera moves (sharpness scan + stills), clicks synchronized. |
| FINAL_RENDER_READY | **FALSE** | False until the founder approves this review, confirms the music licence, and replaces the temporary SFX (or accepts them). |

## The 20 questions

**1. Is the founder VO unchanged?** — `TRUE` · _VERIFIED IN PROVIDED ASSET_  
Yes. P1–P8 are the founder's files: same WAVs since V6 (48 kHz, gain-matched; originals kept), no regeneration, no speed or pitch change, no trims inside a chunk, every [pause] kept (≥ 1 s measured).

**2. Is every VO section synchronized?** — `TRUE` · _VERIFIED IN CODE_  
Yes. Each chunk starts at its timeline slot; measured onsets in the rendered voice stem are within 36.6 ms of the timeline; audio vs video length differ by 14.7 ms (AAC padding).

**3. Is the music final or temporary?** — `FINAL CANDIDATE` · _VERIFIED IN PROVIDED ASSET_  
Final candidate: the founder-supplied Eleven Music track is what plays. It is not yet declared final — licence tier not verified and the founder has not yet approved it in the mix. The V7 in-project score remains only as an automatic fallback (TEMPORARY, never labelled final).

**4. Are SFX final or temporary?** — `TEMPORARY` · _NOT VERIFIED_  
Temporary. Every SFX is synthesized in-project (no third-party rights). Replacement plan: scripts/elevenlabs-generate.py --sfx (prompts for every sound) or designed files dropped into public/sfx/final/.

**5. What exact music file is being used?** — `TRUE` · _VERIFIED IN PROVIDED ASSET_  
public/music/final/v8/score.wav (48 kHz WAV) made from ~/Downloads/ElevenLabs_NavisLabs_Platform_Introduction.mp3 by scripts/prepare-music-v8.py: −1.5 dB headroom, 44.1 → 48 kHz, −2.5 dB at 3 kHz for dialogue, trimmed to 125.233 s with a 0.8 s fade. Original kept at public/music/source/v8/.

**6. What exact SFX files are being used?** — `TEMPORARY` · _NOT VERIFIED_  
27 files from public/sfx/temp/v7/ (listed in the JSON) plus room tone public/sfx/temp/v8/room.wav; none from public/sfx/final/.

**7. Are all visible company names verified?** — `TRUE` · _VERIFIED IN CODE_  
Yes. NavisLabs is the founder's company (REAL_AUTHORIZED). Kaveri Freightworks is fictional and labelled 'Fictional demo organization' on screen (S05, S07) and in the disclosure. Vendor names (Gmail, Salesforce, Claude Code, …) name connectors/clients nominatively. No real company is shown as a customer; no DailyObjects/Digantara evidence or authorization exists in the repos.

**8. Are all people names verified/fictional?** — `TRUE` · _FICTIONAL DEMO_  
Yes. Abhishek Meena is the founder (REAL_AUTHORIZED, at the founder's request). Meera Iyer, Arjun Rao and Riya are fictional, with reserved example domains. Acme / Jordan Lee / Sam Rivera are gone (validator + project search).

**9. Are all dates chronologically correct?** — `TRUE` · _VERIFIED IN CODE_  
Yes. The film is set on Tue, Oct 6, 2026; past events fall between Sep 30 and Oct 5 (validator dates); the memory card lists them newest first, each dated when it happened; weekdays are correct (Oct 8 is a Thursday).

**10. Are future dates clearly represented as future?** — `TRUE` · _VERIFIED IN CODE_  
Yes. The renewal call reads 'Thu, Oct 8 (upcoming)'; the commitment is 'promised by Oct 7'; the renewal 'closes Nov 14' / 'renews Nov 28'; no November date is phrased as past (validator dates).

**11. Are Salesforce/Notion/Microsoft 365/HubSpot/Jira/GitHub/Zoom claims accurate?** — `TRUE` · _ROADMAP_  
Yes. They are labelled 'upcoming' wherever they appear as a Navis source — S04 column 'Upcoming · demo configuration', priority chips, the evidence chips, the across-systems panel, the agent's context table ('salesforce · upcoming'), the run step — and in the end-card disclosure. In S01/S05 they appear only as the company's own tools (where work lives), not as Navis integrations.

**12. Are any integrations falsely presented as live?** — `NO` · _VERIFIED IN CODE_  
No. Only the six with backend connectors are under 'Live'; validators check that every evidence row from an upcoming system carries the label and that no screen text says an action was executed through one ('updated in Salesforce', 'synced', 'merged', …). The Salesforce and GitHub rows after the reply say 'Next' with a human/agent owner — no update is claimed.

**13. Are any customer claims unsupported?** — `NO` · _FICTIONAL DEMO_  
No. No real customer is named; the disclosure states the organization, people and data are fictional; no metrics, revenue or amounts appear.

**14. Are all UI clicks synchronized?** — `TRUE` · _VERIFIED IN CODE_  
Yes. Every cursor press has its click on the same frame, the cursor settles ≥ 0.1 s before each click, and no click sound plays without a visible click (validator interaction, 29 checks).

**15. Are camera movements readable?** — `TRUE` · _VERIFIED IN CODE_  
Yes. A sharpness scan (with a ±1.5 s window that also catches sustained pushes) was reviewed as stills; fast changes are cuts, eased moves are slow enough to read, S04's pipeline pan runs without blur. Flagged soft moments that remain are fades, dissolves, wipes and sparse frames: 35 listed in navislabs_v8_blur_scan.json.

**16. Is the audio mix suitable for a premium startup showcase?** — `MEASURED PASS · LISTENING PENDING` · _NOT VERIFIED_  
Technically yes, by measurement: the voice leads at ~12.6 LU over the music in speech and ~19 LU under the key lines, the music opens on 'Navis' and rises in the visual-only moments, SFX are felt and below the voice, the room tone keeps the pauses alive at about −50 LUFS. Whether it *feels* premium needs the founder's listening, and the SFX are still temporary.

**17. Is dialogue intelligibility good?** — `TRUE` · _VERIFIED IN CODE_  
By measurement, yes: voice − music 12.64 LU in speech (broadcast guidance ≥ 10 LU), 18.91 LU under the key lines, 13.38 LU on a simulated small speaker; a 3 kHz presence carve in the music; no pumping (music rises 5.7 LU in pauses).

**18. Is the final master free of clipping?** — `TRUE` · _VERIFIED IN CODE_  
Yes: 0 clipped samples, true peak -1.2 dBTP, integrated -14.0 LUFS.

**19. Are there black frames?** — `ONLY THE END FADE` · _VERIFIED IN CODE_  
Only the intended end fade ([[124.97, 125.2]]).

**20. Is the film READY_FOR_FINAL_RENDER?** — `FALSE` · _NOT VERIFIED_  
No — FINAL_RENDER_READY = FALSE until the founder approves this review, confirms the Eleven Music licence, and replaces (or accepts) the temporary SFX. No 4K was rendered.

## Evidence register

### VERIFIED IN CODE

- Live integrations Gmail, Google Calendar, Google Meet, Google Drive, Google Docs, Slack — Backend navis/signals/{gmail,calendar,meet,drive,slack}; Navis-AI ConnectionIds (read-only audit).
- Navis Developer surfaces: MCP (claude mcp add/list), Developer API (X-API-Key), SDK local tarball (not on npm), CLI workstate checkpoint/restore, Members/Invited, roles, permission refusal text, Runs (Running/Completed labels from Devtool lib/runs.ts), 'Not judged' — Devtool (read-only).
- Navis App surfaces (Today, What changed, Why this drawer, Decision drawer, Approve & send, Gmail accepted) — Navis-AI components (read-only).
- Every on-screen entity value is read from src/data/navislabs_v8_launch_state.json (validator data_consistency).

### VERIFIED IN PROVIDED ASSET

- Founder voice P1–P8 (~/Downloads/P1.mp3, p2–p8.mp3 → public/voiceover/source/v6, measured and placed unchanged).
- Music: ~/Downloads/ElevenLabs_NavisLabs_Platform_Introduction.mp3 (ID3 title 'NavisLabs Platform Introduction', 127.84 s, 44.1 kHz stereo; instrumental by spectral analysis) → public/music/final/v8/score.wav.
- NavisLabs brand mark and name (approved assets); founder identity Abhishek Meena (REAL_AUTHORIZED in the dataset).

### FICTIONAL DEMO

- Kaveri Freightworks — Fictional demo organization (Bengaluru logistics; no company with that exact name found in a web search, 2026-10-06)
- People: Meera Iyer (customer contact), Arjun Rao (engineer), Riya (solo developer) — fictional, reserved .example / example.com emails
- Salesforce opportunity, Notion playbook, Jira KVR-142, GitHub file src/workflows/kaveri-renewal.ts, the run 7c2e91a0, all dates, emails and meetings — demo records

### ROADMAP

- Salesforce — shown as 'upcoming' (demo configuration); local source: NOT IN THE LOCAL CHECKOUT — no backend or frontend reference
- Notion — shown as 'upcoming' (demo configuration); local source: NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — enum members only (IntegrationProvider, SignalSource); no credential resolver (tests/execution/test_integration_boundary.py); Navis-AI: 'coming soon, no backend handler'
- Microsoft 365 — shown as 'upcoming' (demo configuration); local source: NOT IN THE LOCAL CHECKOUT — no connector
- HubSpot — shown as 'upcoming' (demo configuration); local source: NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — identity-resolution alias only (AliasProvider.HUBSPOT)
- Jira — shown as 'upcoming' (demo configuration); local source: NOT IN THE LOCAL CHECKOUT — mentioned in comments only
- GitHub — shown as 'upcoming' (demo configuration); local source: NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — identity-resolution alias only (AliasProvider.GITHUB)
- Zoom — shown as 'upcoming' (demo configuration); local source: NOT IN THE LOCAL CHECKOUT — mentioned in a comment only

### NOT VERIFIED

- Eleven Music licence tier for the supplied track (plan unknown; free tier requires crediting ElevenMusic).
- That the seven upcoming integrations will be live at launch (no connector in the local backend checkout).
- Absence of vocals in the music — by spectral analysis only; not confirmed by listening.
- Subjective quality of the final mix and of the temporary SFX — measured, not listened to (no listening is possible in this environment).

## Integrations

| System | In the film | Public website | Local Navis backend |
|---|---|---|---|
| Gmail | LIVE | Supported | LIVE in the local checkout — Backend navis/signals/gmail; Navis-AI ConnectionId 'gmail' |
| Google Calendar | LIVE | Supported | LIVE — Backend navis/signals/calendar; ConnectionId 'calendar' (covers Meet) |
| Google Meet | LIVE | Supported | LIVE — Backend navis/signals/meet; reached through the Calendar grant |
| Google Drive | LIVE | Supported | LIVE — Backend navis/signals/drive; ConnectionId 'drive' (covers Docs) |
| Google Docs | LIVE | Supported | LIVE — Backend navis/signals/drive/docs.py; Docs arrive as Drive files |
| Slack | LIVE | Supported | LIVE — Backend navis/signals/slack; ConnectionId 'slack'; credential resolver shipped (5.4.1) |
| Salesforce | UPCOMING (demo configuration) | Coming soon | NOT IN THE LOCAL CHECKOUT — no backend or frontend reference |
| Notion | UPCOMING (demo configuration) | Coming soon | NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — enum members only (IntegrationProvider, SignalSource); no credential resolver (tests/execution/test_integration_boundary.py); Navis-AI: 'coming soon, no backend handler' |
| Microsoft 365 | UPCOMING (demo configuration) | Coming soon | NOT IN THE LOCAL CHECKOUT — no connector |
| HubSpot | UPCOMING (demo configuration) | Coming soon | NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — identity-resolution alias only (AliasProvider.HUBSPOT) |
| Jira | UPCOMING (demo configuration) | Coming soon | NOT IN THE LOCAL CHECKOUT — mentioned in comments only |
| GitHub | UPCOMING (demo configuration) | Coming soon | NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — identity-resolution alias only (AliasProvider.GITHUB) |
| Zoom | UPCOMING (demo configuration) | Coming soon | NOT IN THE LOCAL CHECKOUT — mentioned in a comment only |

## Dates (film set on Tue, Oct 6, 2026)

| What | Date | Status |
|---|---|---|
| Film 'today' | Tuesday, October 6, 2026 · 09:44 | current |
| Pricing review / decision | Sep 30 | past (Sep 30) |
| Slack commitment made | Sep 30 | past |
| Board metrics committed | Sep 30 (6 days ago) | past |
| Notion renewal playbook | Sep 30 | past |
| Account plan | Oct 1 | past |
| Order form · SSO spec | Oct 2 | past |
| Jira KVR-142 blocked | Oct 3 | past |
| Customer email · call moved | Oct 5 | past |
| Earlier run 3f9a1d27 | Oct 5, 17:31 | past |
| Revised terms due | Oct 7 | future — shown as 'promised by Oct 7' |
| Renewal call | Thu, Oct 8 | future — shown 'Thu, Oct 8 (upcoming)' |
| Contracted renewal / close date | Nov 14 | future — 'closes Nov 14', 'renews' |
| Requested renewal | Nov 28 | future — 'renews Nov 28', 'moving to' |

## Audio QC (measured on the master and the separately rendered stems)

| Measure | Value |
|---|---|
| Master integrated | -14.0 LUFS |
| Master true peak | -1.2 dBTP |
| Clipped samples | 0 |
| LRA | 3.8 LU |
| Voice − music, speech | 12.64 LU |
| Voice − music, key lines | 18.91 LU |
| Voice − music, small speaker | 13.38 LU |
| Music rise in pauses | 5.7 LU |
| Room tone in pauses | -51.56 LUFS |
| Voice peak − SFX peak | 11.53 dB |
| Silence gaps | 0.0–0.4 s (pre-roll: the film opens on the founder's first word); 123.85–125.2 s (the silent end after the tagline) |
| Unexpected volume jumps | 0 |
| Audio − video length | 14.7 ms |
| Max VO onset offset | 36.6 ms |

Stems: voice -16.0 LUFS (peak -1.47 dBFS) · music -25.61 LUFS (peak -8.42 dBFS) · sfx -31.74 LUFS (peak -13.0 dBFS) · room -48.31 LUFS (peak -40.04 dBFS). Stem files: `out/stems/v8-{voice,music,sfx,room}.wav`.

## Music

- File: `public/music/final/v8/score.wav` ← `~/Downloads/ElevenLabs_NavisLabs_Platform_Introduction.mp3 (founder-supplied Eleven Music track, 127.84 s, 44.1 kHz MP3) → scripts/prepare-music-v8.py → 48 kHz WAV`; original kept at `public/music/source/v8/ElevenLabs_NavisLabs_Platform_Introduction.mp3`.
- Processing: −1.5 dB headroom (source peaks +0.4 dBTP), 44.1 → 48 kHz, −2.5 dB presence carve at 3 kHz (Q 1.0) for dialogue intelligibility, trimmed to the film's length with a 0.8 s fade; no time-stretch, no pitch change.
- Status: FINAL CANDIDATE — VERIFIED IN PROVIDED ASSET (founder-supplied ElevenLabs export). Licensing: NOT VERIFIED (depends on the ElevenLabs plan the track was generated on; free-tier tracks require crediting ElevenMusic).
- Act 1 held ~−7 dB (curve) so the opening problem sits over near-silence; the level opens on 'Navis' (14.03 s); the track's own rhythmic entrance follows at 18.6 s, 0.8 s before the S04 wipe.
- The percussion texture starts at 53.3 s — 0.35 s after the cut to Navis Developer (52.95 s).
- The track drops at 118.7 s — 'NavisLabs.' is at 118.8 s; the curve takes it to near-silence after the word and leaves a restrained tail under the tagline.
- Mix: −6.0 dB under every line, −13.5 dB under the 7 key lines (strongest), +2.0 dB in visual-only moments ≥ 1.5 s, act 1 held −7 dB, near-silence after 'NavisLabs.', silent end.

## SFX (TEMPORARY)

| Group | Category | Events |
|---|---|---|
| A · UI interaction | KEYBOARD | 42 |
| A · UI interaction | TERMINAL | 5 |
| A · UI interaction | MOUSE | 0 |
| A · UI interaction | UI CLICK | 9 |
| B · data movement | DATA ARRIVAL | 20 |
| B · data movement | SOURCE APPEAR | 12 |
| D · product moments | MCP CONNECT | 5 |
| B · data movement | API RESPONSE | 1 |
| B · data movement | CONTEXT RETRIEVAL | 4 |
| D · product moments | PERMISSION DENIED | 1 |
| D · product moments | APPROVE | 1 |
| D · product moments | SEND | 1 |
| D · product moments | GMAIL CONFIRM | 1 |
| D · product moments | RUN START | 1 |
| D · product moments | RUN COMPLETE | 1 |
| D · product moments | PRODUCT REVEAL | 1 |
| C · camera transitions | TRANSITION | 5 |
| E · ending | END REVEAL | 1 |
| D · product moments | WORKSPACE CREATED | 1 |
| D · product moments | SHARED UNDERSTANDING | 1 |

Silence is used on purpose (no SFX in the breath before 'Navis', after Approve, under the refusal, under 'Same facts…', after the end lockup). Files: public/sfx/temp/v7/*.wav; room tone public/sfx/temp/v8/room.wav.

## What changed (V7 → V8)

- Music: the founder-supplied Eleven Music track replaces the in-project score (which stays only as an automatic fallback).
- Mix: strongest ducking moved to the brief's 7 lines; music lifts in visual-only moments; act 1 held near silence; room tone added as a 4th layer in the pauses.
- SFX: subtle whooshes on the two world changes, a reverse whoosh into one company, one sweep as the systems appear (S04 ticks halved), 'workspace created', a 'shared understanding' lock, a quieter end resolve; Send/Gmail confirm under 'Then the company acts.' set lower.
- Integrations: Live (6) vs Upcoming · demo configuration (7) on screen and in the disclosure; 'upcoming' on every evidence row from an upcoming system.
- Data: 'Fictional demo organization' on screen; renewal call moved to Thu, Oct 8 (was Oct 9, a Friday, against the reply's 'Thursday'); documents dated Oct 1–2; 'Committed 6 days ago' (was 9); memory card dated by when things happened, newest first.
- Camera: S04 pipeline pan slowed and unblurred; S07 push onto the evidence slowed — both were smeared in V7.

## What I need to do next (founder)

- Watch/listen to the 1080p review on MacBook speakers, iPhone and AirPods.
- Confirm the ElevenLabs plan used for the music allows commercial film use (credit ElevenMusic if it was the free tier).
- Provide final SFX (ElevenLabs Sound Effects with ELEVENLABS_API_KEY set: `npm run audio:eleven`, or designed files in public/sfx/final/), or approve the temporary ones.
- Confirm the launch status of Salesforce, Notion, Microsoft 365, HubSpot, Jira, GitHub and Zoom — they stay 'upcoming' until the team confirms them live.
- Then approve for the final (4K) render.
