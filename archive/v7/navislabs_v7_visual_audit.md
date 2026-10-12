# NavisLabs launch film — V7 visual audit

Review cut 1920×1080, 30 fps, 3757 frames (2:05.23). Reviewed as contact sheets every 2 s across the whole film plus full-resolution stills at every changed moment (the Navis reveal, the S04 pull-back, the CRM conflict, Approve & send, the run states, "One understanding." / "Two ways in.", the end card).

## What changed from V6, and why

- **Navis reveal (S03)** — the mark comes into focus on "Navis" (a 0.65 s lens pull, scale 0.965 → 1, no glow) over a slow 1 → 1.025 push, in sync with the music opening and the PRODUCT REVEAL bloom.
- **Systems → one intelligence (S04)** — the camera now pulls back progressively (1.08 → 1.03 → 0.96 → 0.88 → 0.66) as each stage is named, so the scattered pieces visibly become one chain.
- **CRM story (S07)** — the evidence reads as a chain (customer email → Salesforce opportunity → meeting → decision → documents / commitment / engineering). As the state resolves, an amber link joins the email and the CRM record: "CRM Nov 14 ≠ email Nov 28"; the Opportunity row shows ~~Nov 14~~ → Nov 28 · CRM NOT UPDATED; Next: "Reply to Meera; then the CRM". The CRM alone does not hold the whole truth.
- **Then the company acts (S09)** — the 0.2 s whip that smeared the frame at 49.2 s is now a clean macro cut to the send state; the cursor lifts off Approve & send with a small move-away before it fades; the pull-back to the across-systems panel now takes 1.2 s instead of 0.45 s.
- **Context moment (S12)** — the 0.2 s pushes onto SOURCE and FRESHNESS (smeared in V6 and in the first V7 render) are now clean macro cuts, and so is the return to the agent: precise and readable. S06's return to the card and S08's widening as the drawer opens are clean cuts too (both smeared for three frames).
- **Run moment (S15)** — RUN START → WORK → RUN COMPLETE: the run arrives in Runs as *Running* (duration "—"), its timeline fills step by step with the current step *Running*, and it reads *Completed* as the last step lands — the product's real labels (Devtool lib/runs.ts), in the product's accent tone (a completed run is deliberately not green).
- **One understanding. Two ways in. (S17)** — the camera pulls back on "One understanding." (1.03 → 0.93); on "Two ways in." both product surfaces are outlined and both names underlined at once.
- **Camera easing** — the spec's 'glide' curve starts at ~4.5× its average speed and smeared the first frames of every push and pull (found by a sharpness scan of the first V7 render: 10 smeared moments). The camera now uses a gentle-start glide (bezier 0.45, 0, 0.2, 1 — soft departure, firm settle) set in the Camera component; the protected spec file is untouched. The SDK → API whip in S13 is now a cut, and the camera is still on Approve & send for 'A person decides.' (a cut as the typing ends; only the cursor moves).
- **Motion blur** — shutter halved (180° → 90°) and the threshold doubled (14 → 28 px/frame): fast moves stay readable everywhere.
- **End card** — the disclosure (which now names the fictional customer) is set at 15 px and 90 % so it is readable at 1080p.
- **Consistency fixes** — the run's context step said "5 facts · …calendar" while the agent's table shows 6 facts with Salesforce (now "6 facts · gmail, docs, meet, slack, salesforce"); the hero's agent pane said "count: 5" (now reads the table); the editor's file name was hard-coded (now from the launch state); the evidence card title no longer wraps.
- **Customer** — every Acme / Jordan Lee / Sam Rivera reference is gone from the render path (validator + project search): Kaveri Freightworks (fictional, Bengaluru), Meera Iyer, Arjun Rao, KVR-142, src/workflows/kaveri-renewal.ts, #kaveri.

## Camera language

| Speed | Where |
|---|---|
| Slow | S01 opening, the Navis reveal, "A person decides." (cursor settled on Approve), the thesis, the end card |
| Medium | S04 pipeline pull-back, the App (Today → What changed → Why → evidence → draft), S17 |
| Fast (always readable) | systems arriving, S10–S15 developer cuts, terminal, MCP · API · SDK · CLI, permissions, run |

No random zooms: every move follows a spoken word or a visible action (navislabs_v7_voiceover_screen_map.json lists the camera for each line).

## UI motion

Source chips fade with a ~2–3 % scale; facts arrive sequentially (0.12 s apart); freshness fades with a short slide; the cursor moves, settles ≥ 0.1 s, clicks, gives feedback and moves away (7 interactions, validator interaction); the CRM row highlights and changes state; connections go connecting → ✓ Connected; runs go Running → Completed. Natural easing, no bounce.

## Readability and quality checks

- Frames 3757 / 3757, 1920×1080, 30/1, h264 yuv420p, bt709 ✓
- Near-black runs: [[124.97, 125.2]] — the end fade only ✓
- Luma jumps > 18: 15 — all on deliberate cuts between the light (App) and dark (Developer) worlds
- Sharpness scan (Laplacian variance vs ±12-frame neighbourhood, `scripts/blur-scan.py`): 20 soft moments flagged — 7.0–7.27 s; 9.43–9.43 s; 29.97–30.17 s; 37.83–38.0 s; 49.07–49.07 s; 49.3–49.43 s; 53.53–53.53 s; 57.53–57.53 s; 64.77–64.77 s; 69.97–70.0 s; 72.37–72.43 s; 76.33–76.63 s; 78.73–78.73 s; 87.77–87.8 s; 89.33–89.67 s; 92.73–92.97 s; 105.13–105.27 s; 110.03–110.4 s; 118.23–118.57 s; 124.87–125.03 s. Each was reviewed as a still: what remains are scene dissolves/fades, wipes, cuts to sparse frames and the end fade — no camera smear on readable UI.
- Motion scan (frame-to-frame difference, 320×180 grey): peak 181.9 (single-frame cuts); sustained fast motion (≥ 3 frames over 15): [[41.93, 42.1, 41.4], [81.27, 81.37, 64.1]] — 41.9–42.1 s is the decision drawer sliding in right after a cut (UI motion, frames sharp); 81.3 s is the 0.2 s dissolve into the Console.
- No fake grain beyond the existing 1.5–2.5 % film grain on dark scenes, no bloom, no glassmorphism, no particles; the product UI stays the hero.
- Browser chrome, traffic lights and Console navigation are recreated from the product source; logos are the website's vendor marks; the NavisLabs mark is the approved asset.

## Known limits (not fixed in V7)

- 4K quality (text rasterization at 2×) is not yet verified — no 4K was rendered, as instructed.
- The evidence chips in S07 are small at 1080p (15.5 px fact text); readable on a laptop, tight on a phone.
