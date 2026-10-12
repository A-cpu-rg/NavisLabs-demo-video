# NavisLabs launch film — V7 final product audit

Review cut: `out/navislabs-v7-review-1080p.mp4` and `out/navislabs-v7-review-540p.mp4` · **125.23 s (2:05.23) · 3757 frames** — the same 125 s structure; the founder's voice (P1–P8) is locked and is the master clock.  
**Validators:** all pass — narrative ✓ · brand ✓ · entity ✓ · product_claim ✓ · integration ✓ · interaction ✓ · timeline ✓ · voice_audio ✓ · visual_asset ✓ · data_consistency ✓ · captions ✓.  
**Stale-copy search:** 3577 hits, 0 to fix.

Companion audits: `navislabs_v7_audio_audit.md`, `navislabs_v7_visual_audit.md`, `navislabs_v7_customer_entity_audit.json`, `navislabs_v7_readiness_report.md`.

## The 18 questions

**1. Does the film feel like a premium San Francisco startup showcase?**  
Closer than V6, and on purpose: the problem opens restrained, the music opens on "Navis", the App section breathes on the human decision, the Developer section is rhythmic and readable, the thesis slows down and the name lands in near-silence. The remaining gap is the audio *production*: the score and SFX are synthesized in-project. A produced score (Eleven Music or a composer) and recorded/ElevenLabs SFX are the step that will make it feel fully premium. This judgement is from frames and measurements — no listening test was possible here.

**2. Is the music clearly audible on normal speakers?**  
Measured, yes: under speech the music now sits 12.6 LU below the voice (V6: 21.26), and with a 180 Hz high-pass that simulates laptop/phone speakers it is 14.26 LU below (V6: 25.78). The pulse carries harmonics (140 Hz knock, saturation) so it reads without sub-bass. A listening check on MacBook, iPhone and AirPods is still needed.

**3. Does music create emotion without fighting the founder?**  
The score follows the voice (opens on "Navis", breath on "A person decides.", return on "Then the company acts.", lift and resolution on the thesis lines, near-silence on "NavisLabs."); it ducks −6 dB under every line and −11 dB under the eight key lines, leaves 2–4 kHz open, and rises naturally in the pauses.

**4. Are SFX synchronized with visible interactions?**  
Yes — 113 events, each on a visible action at the same frame; no click without a visible click; no SFX inside the deliberate silences; nothing but keystrokes under a key line (validators interaction + voice_audio).

**5. Does the first Navis reveal feel like a real "wow" moment?**  
It is built as one: a breath, a reverse swell, then on the word "Navis" the score opens (+7 LU from act 1 to act 2 in the music stem), the PRODUCT REVEAL bloom, and the mark coming into focus with a slow push; the systems then flow into one chain with a progressive pull-back.

**6. Does the developer section feel technically impressive?**  
It shows real surfaces at speed and stays readable: VS Code + Claude Code, Members → Invited, the real `claude mcp add` / `claude mcp list` → ✓ Connected, Connect with MCP · API · SDK · CLI lighting on the words, the agent's context arriving fact by fact with SOURCE and FRESHNESS, the SDK and API, three credentials with the product's exact refusal, the diff, Runs and a run going Running → Completed.

**7. Does the App section feel human?**  
Yes: Today, what changed, why (every fact with source, time, freshness), the CRM conflict, Navis preparing the reply, the person editing one sentence, the cursor resting on Approve & send through "A person decides." with the music drawn back, then the company acting.

**8. Does the solo/team/company story make sense?**  
Yes: a solo developer signs up "For myself" and gets a personal workspace (no Navis App involved), a team works in the company's Members, the work state carries into the next session, and only then does the film widen to one company with the person and the agent on the same event.

**9. Are Navis App and Navis Developer clearly separate?**  
Yes: separate worlds (light App, dark Developer), separate interfaces recreated from separate sources, separate audiences on the end card. The shared understanding is the bridge (S17) — never one merged interface.

**10. Is every real company name authorized?**  
Yes. The only real organization shown as a user is NavisLabs itself (the founder's company). Vendor names (Gmail, Salesforce, Claude Code, …) are used nominatively to name connectors and clients. No real company is shown as a customer — research found no authorized NavisLabs customer.

**11. Is every fictional entity explicitly identified?**  
Yes: Kaveri Freightworks and its people are named as fictional in the end-card disclosure; every synthetic record is marked SYNTHETIC in the launch-state file; customer emails use reserved .example domains.

**12. Are all connector claims accurately represented?**  
In the film, the thirteen systems appear as the LAUNCH CONFIGURATION supplied by the founder/team, and the disclosure says "shown in the launch configuration". They are not claimed to be available to everyone today. The website lists 7 of them as Coming soon and the local product source has no connector for Salesforce, Notion, Microsoft 365, HubSpot, Jira, GitHub, Zoom — see the connector table below.

**13. Is Salesforce presented as meaningful context rather than a logo?**  
Yes: it is the CRM of record with a demo opportunity; the film shows the chain email → CRM → meeting → decision, the conflict (CRM still says the old close date), the corrected state, the next action ("Reply to Meera; then the CRM"), and after the reply the Salesforce row is the next step owned by a person; the agent's context cites it too.

**14. Are there any stale names?**  
No: Acme, Jordan Lee and Sam Rivera are gone from the render path, copy and data (validator entity ✓; project search 0 to fix). History remains only in archive/.

**15. Are there any fake customer claims?**  
No. The customer is fictional and disclosed; no real company appears as a customer; no metrics, revenue or amounts.

**16. Is every visible UI element internally consistent?**  
Yes, as far as the validators and frame review can tell: one data file feeds every scene; the run's context step, the agent's table and the hero now all say 6 facts with the same sources; the CRM close date is the customer's old renewal date; the GitHub file is the one the agent edits; run labels match the product.

**17. Does the end card feel premium?**  
It is quiet and exact: the mark and name in near-silence after "NavisLabs.", the tagline with a barely-there harmonic tail, the two products, navislabs.in, a readable disclosure, then silence.

**18. Does the film feel better than V6?**  
By every measure taken, yes (see the A/B table in the audio audit): the music is present and shaped instead of almost inaudible, the pauses no longer pump, the SFX are felt, the CRM story is real, the reveal and the run have their moments, and the smeared frame is gone. Whether it *feels* more exciting is the founder's call after watching — the synthesized audio is the main thing still holding it back.

## Connectors (film launch configuration)

> The launch film represents the planned launch-state connector set supplied by the founder/team. Public website status may lag this film configuration.

Shown as LAUNCH CONFIGURATION, not current general availability. Nothing in the product repositories or the website was modified, and the film does not claim the website was updated.

- **Gmail** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS SUPPORTED · LOCAL PRODUCT SOURCE: LIVE in the local checkout — Backend navis/signals/gmail; Navis-AI ConnectionId 'gmail' · IN FILM: evidence
- **Google Calendar** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS SUPPORTED · LOCAL PRODUCT SOURCE: LIVE — Backend navis/signals/calendar; ConnectionId 'calendar' (covers Meet) · IN FILM: evidence
- **Google Meet** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS SUPPORTED · LOCAL PRODUCT SOURCE: LIVE — Backend navis/signals/meet; reached through the Calendar grant · IN FILM: evidence
- **Google Drive** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS SUPPORTED · LOCAL PRODUCT SOURCE: LIVE — Backend navis/signals/drive; ConnectionId 'drive' (covers Docs) · IN FILM: evidence
- **Google Docs** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS SUPPORTED · LOCAL PRODUCT SOURCE: LIVE — Backend navis/signals/drive/docs.py; Docs arrive as Drive files · IN FILM: evidence
- **Slack** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS SUPPORTED · LOCAL PRODUCT SOURCE: LIVE — Backend navis/signals/slack; ConnectionId 'slack'; credential resolver shipped (5.4.1) · IN FILM: evidence
- **Salesforce** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS COMING SOON · LOCAL PRODUCT SOURCE: NOT IN THE LOCAL CHECKOUT — no backend or frontend reference · IN FILM: evidence (primary CRM)
- **Notion** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS COMING SOON · LOCAL PRODUCT SOURCE: NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — enum members only (IntegrationProvider, SignalSource); no credential resolver (tests/execution/test_integration_boundary.py); Navis-AI: 'coming soon, no backend handler' · IN FILM: evidence (company knowledge)
- **Microsoft 365** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS COMING SOON · LOCAL PRODUCT SOURCE: NOT IN THE LOCAL CHECKOUT — no connector · IN FILM: connected infrastructure — no record shown
- **HubSpot** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS COMING SOON · LOCAL PRODUCT SOURCE: NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — identity-resolution alias only (AliasProvider.HUBSPOT) · IN FILM: connected infrastructure — no record shown (Salesforce is the primary CRM example)
- **Jira** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS COMING SOON · LOCAL PRODUCT SOURCE: NOT IN THE LOCAL CHECKOUT — mentioned in comments only · IN FILM: evidence (engineering)
- **GitHub** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS COMING SOON · LOCAL PRODUCT SOURCE: NOT IN THE LOCAL CHECKOUT AS A CONNECTOR — identity-resolution alias only (AliasProvider.GITHUB) · IN FILM: evidence (code)
- **Zoom** — FILM STATUS: CONNECTED / LAUNCH CONFIGURATION · PUBLIC WEBSITE STATUS: CURRENTLY SHOWN AS COMING SOON · LOCAL PRODUCT SOURCE: NOT IN THE LOCAL CHECKOUT — mentioned in a comment only · IN FILM: connected infrastructure — no record shown (Meet carries the meeting example)

## Product separation and claims

- Navis App: human-facing organizational intelligence (S05–S09). Navis Developer: developer / AI-agent platform, private preview (S10–S16). The shared understanding is the conceptual bridge (S17).
- Developer claims stay honest: Claude Code is the only LIVE VERIFIED MCP client; the SDK is a local package, not on npm; the API base URL is a placeholder; credentials are placeholders; economics read "—"; the outcome is "Not judged"; the central policy engine is not shown as live.
- After the reply, Navis does not claim to update other systems: each row (Salesforce, GitHub, Jira) shows who owns the next step.

## Data

Every visible name, date, company, customer, CRM record, email, GitHub file, Jira issue, meeting, source, freshness, role and workspace comes from `src/data/navislabs_v7_launch_state.json` via `src/ui/demoContent.ts` (validator data_consistency: no entity value hard-coded in a component). Customer: Kaveri Freightworks (fictional). People: Abhishek Meena (real, authorized), Meera Iyer, Arjun Rao, Riya (fictional).

## Render

1080p: 66.1 MB, 125.248 s, -14.07 LUFS, -1.18 dBTP, 0 clipped samples.  
540p: 12.1 MB, 960×540, same mastered audio (-14.07 LUFS).  
**No 4K rendered.**

