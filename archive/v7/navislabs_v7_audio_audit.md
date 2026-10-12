# NavisLabs launch film — V7 audio audit

Voice, music, SFX and the final mix are measured **separately**: Remotion renders each stem on its own (the `stem` prop on `NavisLaunch`, audio-only WAV), and `scripts/measure-stems.py` measures them with ITU-R BS.1770 K-weighting (EBU R128 gating for integrated loudness) against the measured speech windows. Stems are pre-master; the mastering gain applies equally to all of them.

## V6 → V7, measured

| Measure | V6 | V7 | Target | |
|---|---|---|---|---|
| Voice, integrated (pre-master) | -16.0 | -16.0 | unchanged (locked) | ✓ |
| Music, integrated | -30.97 | -25.25 | clearly present | ✓ |
| SFX, integrated | -45.68 | -32.64 | felt, never above the voice | ✓ |
| Voice − music under speech (LU) | 21.26 | 12.6 | 12–13 | ✓ |
| Voice − music under the 8 key lines (LU) | 22.8 | 14.51 | 14–16 (ducks, never disappears) | ✓ |
| Music rise in the founder's pauses (LU) | 10.66 | 6.27 | 4–7 (natural, not pumping) | ✓ |
| SFX peak vs voice peak (dB) | -19.45 | -14.53 | below the voice | ✓ |
| Voice − music under speech, small speaker (LU) | 25.78 | 14.26 | music audible on laptop / phone | ✓ |

Music by act (music stem alone, ungated LUFS):

| Act | V6 | V7 |
|---|---|---|
| 1 · problem (0.0–14.0 s) | -40.18 | -36.76 |
| 2 · Navis reveal (14.0–28.5 s) | -31.45 | -24.56 |
| 3 · Navis App (28.5–52.9 s) | -32.16 | -26.52 |
| 4 · Developer (52.9–83.3 s) | -31.92 | -29.7 |
| 5 · solo / team / company (83.3–104.7 s) | -30.44 | -24.05 |
| 6 · thesis (104.7–118.2 s) | -30.81 | -22.0 |
| 7 · end (118.2–125.2 s) | -29.16 | -41.67 |

## Final mix (mastered 1080p)

Integrated **-14.07 LUFS**, true peak **-1.18 dBTP**, **0 clipped samples**, LRA 4.4 LU; voice present on every line (-18.6 … -12.5 dB RMS); silent end -180.0 dB. Mastering: one static gain to −14 LUFS and a 4×-oversampled peak limiter (`scripts/master-audio.py`) — no dynamic loudness processing, so the pauses and breaths stay as mixed.

## Voice (locked)

The founder's eight ElevenLabs chunks (P1–P8) are unchanged since V6: same files, same placement, no speed change, no trims, no pauses removed (validator voice_audio). The voice remains the master clock; every music section, curve keyframe, SFX and caption is placed on its measured lines and words.

## Music — a six-layer score

Premium cinematic AI-infrastructure score: organic analog synth texture, warm low end, a subtle pulse, restrained percussion, an evolving harmonic bed, technical micro-textures and an emotional final resolution. No EDM, cyberpunk, trailer braams, cheesy piano, corporate stock or generic motivational music. The founder's voice always wins.

| Layer | Role | Mix gain | Share of the voice duck |
|---|---|---|---|
| bed | atmospheric bed: low drone, air, distant shimmer | -3.0 dB | 80 % |
| pulse | low cinematic pulse: soft kick, sub, analog bass | -3.0 dB | 100 % |
| harmony | warm harmonic texture: detuned analog pads, strings-like | -1.5 dB | 100 % |
| rhythm | technical rhythmic layer: plucked 16ths, soft ticks | -4.0 dB | 100 % |
| texture | transition textures: reverse swells, digital micro-texture, the permission tone | -3.0 dB | 50 % |
| resolve | emotional resolution: soft mallet / bell motifs | -3.0 dB | 70 % |

Mixed in Remotion with **keyframed volume curves** (not one static gain): a duck curve built from the measured speech windows (-6.0 dB under a line, -11.0 dB under a key line, 0.15 s attack, 0.6 s release — 202 keyframes) and a curve of controlled dips (27 keyframes):

- 13.18–13.86 s · -14 dB · the breath before Navis (the reverse swell rides through it)
- 45.87–48.8 s · -4 dB · 'A person decides.' — the music drops back to a controlled breath, not silence
- 48.85–49.1 s · -8 dB · held breath on Approve & send
- 78.04–79.68 s · -5 dB · the refusal: quieter, darker, serious
- 119.62–121.28 s · -20 dB · near-silence after 'NavisLabs.'
- 124.31–125.233 s · -96 dB · silent end

The arc (written into the score, not just the mix):

- **M1 problem** 0.00–13.98 s — almost no music, never dead: a low atmosphere under the contradiction; scattered high fragments as the systems appear; heavier on 'by hand'; held on 'without it'; a breath, then a reverse swell into 'Navis'
- **M2 reveal** 13.98–28.50 s — the first wow: on 'Navis' the music opens — warm harmonic bloom, deep pulse, small digital texture; the pipeline builds layer by layer and pulls back on 'next'
- **M3 human** 28.50–52.93 s — the Navis App: warm, intelligent, half-time; drops back to a controlled breath on 'A person decides.', returns on 'Then the company acts.'
- **M4 technical** 52.93–83.30 s — Navis Developer: precise 16th-note rhythm, soft kick, analog bass; thins under the key lines; slows for the permission check with a low tonal shift on DENIED; resolves slightly as the run completes
- **M5 scale** 83.30–104.70 s — solo → team → company: from one voice to the full ensemble; the voice alone carries 'Same facts. Same sources. Same freshness.'; lift on 'One understanding.', resolution on 'Two ways in.'
- **M6 thesis** 104.70–118.20 s — slow, deep, warm, wide; no rhythm; rises in the pause after 'Tools change.'; no crescendo
- **M7 end** 118.20–125.23 s — everything almost stops for 'NavisLabs.'; logo in near-silence; a very soft harmonic tail under the tagline; then silence

Sync points: the music opens on "Navis" (a reverse swell through the breath, then a warm D major 9 bloom; the pulse joins one bar later); drops to a held dyad on "A person decides."; returns with the pulse and a mallet motif on "Then the company acts."; thins under "Navis isn't the model."; half-time for the permission check with a low D → C♯ tonal shift and a darker borrowed chord on DENIED; resolves to D major as the run reads Completed; one voice for the solo builder, more for the team, the ensemble for the company; held under "Same facts…"; lift on "One understanding.", resolution on "Two ways in."; slow and deep under the thesis; almost silent for "NavisLabs."; a barely-there tail under the tagline; silence.

Voice first: every melodic stem carries a −3 dB presence dip at 2.8 kHz; the pulse has a 140 Hz knock and saturation so it reads on small speakers without sub-bass.

**Status: review quality, not final.** The score is synthesized in-project (`scripts/make-score-v7.py`; no samples, no third-party rights). Eleven Music could not be used: `ELEVENLABS_API_KEY` is not set in this environment, and no key was looked for elsewhere. `scripts/elevenlabs-generate.py --music` is ready (composition plan from the seven sections, instrumental, 48 kHz); its output drops into `public/music/final/v7/score.wav` and replaces the stems with no code change. Eleven Music terms: commercial use requires a paid plan, and the Starter plan excludes films, advertising and broadcast — a launch film needs Creator or above.

## SFX — rebuilt

| Category | Events |
|---|---|
| KEYBOARD | 42 |
| TERMINAL | 5 |
| MOUSE | 0 |
| UI CLICK | 9 |
| DATA ARRIVAL | 23 |
| SOURCE APPEAR | 12 |
| MCP CONNECT | 5 |
| API RESPONSE | 1 |
| CONTEXT RETRIEVAL | 4 |
| PERMISSION DENIED | 1 |
| APPROVE | 1 |
| SEND | 1 |
| GMAIL CONFIRM | 1 |
| RUN START | 1 |
| RUN COMPLETE | 1 |
| PRODUCT REVEAL | 1 |
| TRANSITION | 4 |
| END REVEAL | 1 |

113 events, every one on a visible action (validators: every cursor press has its sound on the same frame; no click without a visible click; no SFX inside the deliberate silences; nothing but keystrokes under a key line). MOUSE is intentionally empty — the cursor moves silently. The library is synthesized in-project (`scripts/make-sfx-v7.py`: physical keys and trackpad with a small room, FM chimes tuned to the score's key — D and A, never a C natural against C♯ — a two-note low semitone for DENIED, short air for transitions). Levels: important interactions peak briefly above the music (Approve, Gmail confirm, ✓ Connected, DENIED, run complete); SFX stay well under the voice. ElevenLabs Sound Effects prompts for all 22 sounds are scripted (`scripts/elevenlabs-generate.py --sfx`, `pcm_48000`) but not generated (no key).

## Research used

- ElevenLabs — Sound effects capability: https://elevenlabs.io/docs/overview/capabilities/sound-effects
- ElevenLabs — Sound generation API (POST /v1/sound-generation, duration 0.5–30 s, prompt_influence, pcm_48000): https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert
- ElevenLabs — Eleven Music capability (3 s–5 min, section-by-section composition, commercial clearance): https://elevenlabs.io/docs/overview/capabilities/music
- ElevenLabs — Compose music API (POST /v1/music, composition_plan, force_instrumental): https://elevenlabs.io/docs/api-reference/music/compose
- ElevenLabs — Eleven Music v1 terms (paid plans; Starter excludes films/ads/broadcast): https://elevenlabs.io/eleven-music-v1-terms
- Remotion — controlling volume over time (frame-based volume with interpolate): https://www.remotion.dev/docs/audio/volume
- Remotion — using audio: https://www.remotion.dev/docs/using-audio
- IRPR — mixing audio for YouTube (−14 LUFS, ≤ −1 dBTP; music 15–20 dB under talking, up in the gaps): https://sounddesign.irpr.agency/guides/how-to-mix-audio-for-youtube/
- University of Salford repository — broadcast guidance on commentary-to-music loudness difference (≥ 10 LU): https://salford-repository.worktribe.com/OutputFile/1489990
