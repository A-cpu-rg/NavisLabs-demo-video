# NavisLabs — launch film (V8 · final-audio candidate)

Remotion project for the NavisLabs launch film: **125.23 s (3757 frames), 1920×1080, 30 fps**.
The length is set by the founder's final voice performance — the voice is the master clock.
One company, NavisLabs, and two products on one shared understanding:

- **Navis App** — for people inside a company: what changed, why it matters (every fact with
  source, time and freshness), what is waiting on you; Navis prepares the next step, a person
  decides, then the company acts.
- **Navis Developer** — for developers, AI agents, teams and solo builders (private preview):
  company context over MCP / API / SDK / CLI, cited facts with source and freshness,
  permission checks, recorded runs, work state that carries into the next session.

Thesis: **One understanding. Two ways in.** NavisLabs (real) uses its own products; one
fictional Indian customer, Kaveri Freightworks (Bengaluru logistics — disclosed as fictional on
the end card), and one business event — its renewal moved from Nov 14 to Nov 28, while the CRM
still says Nov 14 — run through both products and across the company's connected systems. No
real company is shown as a customer: no authorized NavisLabs customer exists in any public or
provided source. The Navis product repositories and the website are read-only sources.

**Status:** V8 final-audio candidate (`out/navislabs-final-audio-review-{1080p,540p}.mp4`;
the V7 review is untouched). Founder VO final and locked (P1–P8). Music: the founder-supplied
Eleven Music track (`public/music/final/v8/score.wav`; licence tier not verified). SFX and room
tone: in-project temporary sounds. Six integrations are live; seven are shown as "upcoming"
(demo configuration). See `navislabs_final_launch_audit.md` / `.json`.

## Sources of truth

- `src/data/navislabs_v8_copy.json` — **every word**: the founder's eight VO chunks (exact
  text, `[pause]` marks) and all on-screen copy, plus the positioning rules.
- `src/data/navislabs_v8_launch_state.json` — **every entity**, film-only: company, people,
  customer, emails, meetings, documents, the Salesforce opportunity, the Notion playbook, the
  Jira issue, the GitHub file, runs, workspaces, team work state, and the film's launch-state
  integrations (`FILM_LAUNCH_INTEGRATIONS`). Each record has a provenance (REAL_AUTHORIZED /
  REAL_PUBLIC_PRODUCT / SYNTHETIC). `src/ui/demoContent.ts` phrases it per screen; no component
  names an entity (validator `data_consistency`).
- `public/voiceover/source/v6/P1–P8.mp3` — the founder's files as delivered (untouched);
  `public/voiceover/final/v6/P1–P8.wav` — 48 kHz WAVs gain-matched to −19 LUFS (no speed
  change, no trims, no pauses removed).
- `scripts/analyze-voice.py` — measures the (locked) performance → `navislabs_v6_voice_analysis.json`
  (per chunk: length, loudness, speech segments, pauses, every line's start/end).
- `scripts/build-film-data-v8.py` — places the chunks and derives every scene and beat from
  the measured lines and words → `navislabs_v8_voice_timeline.json`,
  `navislabs_v8_film_spec.json`, `navislabs_v8_audio_map.json` (music, room tone, keyframed volume curves),
  `navislabs_v8_product_surface_map.json`, `interaction_state_machine.json`.
- `scripts/build-audits.py` — entity, consistency, developer-capability, team-permission audits.
- `scripts/build-captions.py` — `captions/navislabs-v8.srt|.vtt` and the word-level
  `public/captions/navislabs-v8-captions.json` (@remotion/captions format), from the voice.
- `scripts/make-score-v7.py` / `scripts/make-sfx-v7.py` — the fallback score stems and the 27 temporary SFX,
  synthesized in-project (no samples, no third-party rights).
- `scripts/prepare-music-v8.py` — the supplied Eleven Music track → 48 kHz film WAV (original kept).
- `scripts/make-room-v8.py` — temporary room tone (4th layer, pauses only).
- `scripts/build-v8-audio.py` — `navislabs_v8_voiceover_screen_map.json` (every line → scene,
  camera, cursor, SFX, music, captions), `navislabs_v8_sfx_map.json`,
  `navislabs_v8_music_production_brief.json`.
- `scripts/qc-final-audio.py`, `scripts/blur-scan.py`, `scripts/build-final-audit.py` — final QC and audit.
- `archive/` — superseded V7 / V6 / V5 / V4 / V3 data and scripts, read by nothing (see
  `archive/README.md`). The three protected legacy files stay in place.

## Integrations

Live in the Navis backend (verified in code): Gmail, Google Calendar, Google Meet, Google Drive,
Google Docs, Slack. Upcoming, shown only as a labelled demo configuration: Salesforce, Notion,
Microsoft 365, HubSpot, Jira, GitHub, Zoom — "upcoming" wherever they appear as a Navis source
and in the end-card disclosure; no action is ever shown executed through them.

## Story

| s       | scenes  | what happens |
| ------- | ------- | ------------ |
| 0–14    | S01–S02 | PEOPLE \| AI AGENTS see different truths; the truth is scattered across thirteen systems; people rebuild it by hand, agents start without it |
| 14–28   | S03–S04 | Navis → Navis App / Navis Developer; every signal remembered, connected, turned into what should happen next |
| 28–53   | S05–S09 | The App: what changed → why (source, time, freshness; the CRM still says Nov 14) → Navis prepares the reply → a person decides → Approve & send → the same event across Gmail, Salesforce, GitHub, Jira |
| 53–83   | S10–S15 | Developer: the agent's task; invite the team; connect once (MCP · API · SDK · CLI); context with sources and freshness; Navis isn't the model; permissions; the run on record |
| 83–92   | S16     | A solo builder ("For myself") → a team → the work state carries into the next session |
| 92–105  | S17     | One company: same facts, same sources, same freshness — One understanding. Two ways in. |
| 105–125 | S18     | Models, agents, tools change; what the company knows stays; NavisLabs; end card, silence |

## Compositions

| id                    | size      | fps | frames            |
| --------------------- | --------- | --- | ----------------- |
| `NavisLaunch`         | 1920x1080 | 30  | 3757 (125.23 s)   |
| `NavisLaunchVertical` | 1080x1920 | 30  | 1350 (placeholder — no cut built) |
| `NavisPoster`         | 1920x1080 | —   | still             |

`NavisLaunch` props: `endingVariant` (`A` default), `mode`: `preview` (default, temp audio
allowed), `development` (adds a HUD), `final` (refuses to render until every VO chunk, the final
score and the logo are final files; the VO already is).

## Audio

Each slot plays `public/<kind>/final/…` if present, else `public/<kind>/temp/…`, else silence.
The score is six stems (bed, pulse, harmony, rhythm, texture, resolve) mixed in Remotion through
keyframed volume curves built from the measured speech: −6 dB under every line, −11 dB under the
eight key lines, rising in the pauses, with controlled dips (the breath before "Navis", "A person
decides.", Approve, the refusal, after "NavisLabs."). A final mixed score
(`public/music/final/v8/score.wav`, the supplied Eleven Music track) replaces the stems; final SFX drop into
`public/sfx/final/v7/` under the same names; final room tone into `public/sfx/final/v8/room.wav` — no code change. `scripts/elevenlabs-generate.py`
generates both from `ELEVENLABS_API_KEY` in the environment (never printed or stored; never commit
`.env`); Eleven Music commercial film use needs a paid plan above Starter. Stems can be rendered
and measured separately: `npm run render:stems`.

## Commands

```bash
npm run dev            # Remotion Studio
npm run data:build     # voice analysis → timeline, spec, maps, audits, captions, audio docs
npm run audio:temp     # synthesize the six score stems and the SFX library
npm run audio:eleven   # optional: Eleven Music + Sound Effects (needs ELEVENLABS_API_KEY)
npm run render:stems   # voice / music / SFX rendered and measured separately
npm run validate:film  # the eleven film validators
npm run copy:stale     # project-wide stale-copy search
npm run lint           # eslint + tsc
npm run render:review  # 1080p render → master (−14 LUFS, ≤ −1 dBTP) → out/navislabs-final-audio-review-{1080p,540p}.mp4
npm run check:render   # duration, frames, black runs, loudness, sharpness → navislabs_v8_render_check*.json, navislabs_v8_blur_scan.json
npm run audit:final    # navislabs_final_launch_audit.md + .json
```

No 4K render until the review cut is approved.
