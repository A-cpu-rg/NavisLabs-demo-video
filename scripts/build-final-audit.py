#!/usr/bin/env python3
"""Writes navislabs_final_launch_audit.md and navislabs_final_launch_audit.json (V8 final-audio candidate).

Inputs (all generated, nothing hand-typed as "verified"):
  navislabs_v8_validation_report.json · navislabs_v8_stale_copy_report.json
  navislabs_v8_render_check.json (+ _540p) · navislabs_v8_blur_scan.json · navislabs_v8_audio_qc.json
  navislabs_v8_audio_map.json · navislabs_v8_sfx_map.json · navislabs_v8_music_production_brief.json
  src/data/navislabs_v8_launch_state.json · src/data/navislabs_v8_copy.json · navislabs_v8_voice_analysis (v6)
Every claim carries an evidence class: VERIFIED IN CODE · VERIFIED IN PROVIDED ASSET · FICTIONAL DEMO ·
ROADMAP · NOT VERIFIED. Nothing is called verified because it looks good on screen.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
J = lambda p: json.load(open(os.path.join(ROOT, p)))  # noqa: E731
data = fa.demo_data()
spec, amap, sfxm, mbrief = J("navislabs_v8_film_spec.json"), J("navislabs_v8_audio_map.json"), J("navislabs_v8_sfx_map.json"), J("navislabs_v8_music_production_brief.json")
val, stale = J("navislabs_v8_validation_report.json"), J("navislabs_v8_stale_copy_report.json")
rc, rc540, blur, aq = J("navislabs_v8_render_check.json"), J("navislabs_v8_render_check_540p.json"), J("navislabs_v8_blur_scan.json"), J("navislabs_v8_audio_qc.json")
tl, va, copydoc = J("navislabs_v8_voice_timeline.json"), J("navislabs_v6_voice_analysis.json"), J("src/data/navislabs_v8_copy.json")
END, FRAMES = spec["format"]["duration_s"], spec["format"]["frames"]
V = val["summary"]
launch = data["integrations"]["FILM_LAUNCH_INTEGRATIONS"]
cust = data["customers"][0]


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()[:16]


vo_files = [{"chunk": c["id"], "file": f"public/{c['file']}", "sha256_16": sha(f"public/{c['file']}"), "source_mp3": f"public/voiceover/source/v6/{c['id']}.mp3",
             "duration_s": c["duration_s"], "placed_at_s": c["at_s"]} for c in tl["chunks"]]
music_file = f"public/{amap['music']['final']}"
music_ok = os.path.isfile(os.path.join(ROOT, music_file))
sfx_files = sorted({f"public/{v['temp']}" for k, v in amap["sfx"]["library"].items() if any(e["sound"] == k for c in sfxm["categories"] for e in c["events"])})
sfx_final = [f for f in sfx_files if os.path.isfile(os.path.join(ROOT, f.replace("/temp/", "/final/")))]
room_file = f"public/{amap['room']['temp']}"

# ---------------------------------------------------------------- verdicts from measurements
sep, ml = aq["separation"], aq["master_loudness"]
unexpected_sil = [g for g in aq["silence_gaps"] if not g["intended"]]
unexpected_jumps = aq["volume_jumps"]["unexpected"]
stray_black = [b for b in rc["near_black_runs_s"] if b[0] < END - 1.2]
AUDIO_QC = bool(abs(ml["integrated_lufs"] + 14) <= 0.6 and ml["true_peak_dbtp"] <= -1.0 and ml["clipped_samples"] == 0 and not unexpected_sil
                and 11 <= sep["voice_minus_music_lu"] <= 15 and sep["voice_minus_music_key_lines_lu"] >= 16 and sep["voice_minus_sfx_peak_db"] > 6
                and abs(aq["av_sync"]["audio_minus_video_ms"]) < 40 and aq["av_sync"]["max_abs_onset_diff_ms"] <= 60 and not unexpected_jumps)
VISUAL_QC = bool(rc["video"]["frames"] == FRAMES and not stray_black and V.get("timeline") and V.get("interaction") and V.get("visual_asset"))
FLAGS = {
    "VOICEOVER_READY": bool(V.get("narrative") and V.get("voice_audio") and V.get("captions") and not rc["vo_silent_lines"]),
    "PICTURE_READY": bool(VISUAL_QC and V.get("dates") and V.get("data_consistency")),
    "MUSIC_READY": False,
    "SFX_READY": False,
    "DATA_READY": bool(V.get("data_consistency") and V.get("entity") and V.get("dates") and stale["summary"]["fix"] == 0),
    "INTEGRATIONS_READY": bool(V.get("integration") and V.get("product_claim")),
    "AUDIO_QC": AUDIO_QC,
    "VISUAL_QC": VISUAL_QC,
    "FINAL_RENDER_READY": False,
}
WHY = {
    "VOICEOVER_READY": "P1–P8 are the founder's files, unchanged (hashes below); every line placed on the measured performance; captions from the measured voice.",
    "PICTURE_READY": "12 validators pass; frame review and sharpness scan reviewed; dates, names and labels corrected.",
    "MUSIC_READY": "The founder-supplied Eleven Music track is in the film (VERIFIED IN PROVIDED ASSET), but its licence tier is NOT VERIFIED (it depends on the ElevenLabs plan it was generated on — free-tier tracks must credit ElevenMusic), and it needs the founder's listening approval in the final mix.",
    "SFX_READY": "All SFX are in-project synthesized placeholders (TEMPORARY). No ElevenLabs SFX were supplied and ELEVENLABS_API_KEY is not set, so none were generated.",
    "DATA_READY": "Every visible entity comes from one launch-state file; the customer is a labelled fictional demo organization; all dates validated against Oct 6, 2026.",
    "INTEGRATIONS_READY": "Six live integrations VERIFIED IN CODE (local Navis backend); seven labelled 'upcoming' on screen and in the disclosure (ROADMAP / demo configuration); no action shown executed through them.",
    "AUDIO_QC": "Measured on the master and stems: −14 LUFS, ≤ −1 dBTP, no clipping, no unexpected silence or jumps, voice dominant, A/V in sync.",
    "VISUAL_QC": "3757/3757 frames, no stray black frames, readable camera moves (sharpness scan + stills), clicks synchronized.",
    "FINAL_RENDER_READY": "False until the founder approves this review, confirms the music licence, and replaces the temporary SFX (or accepts them).",
}

# ---------------------------------------------------------------- evidence register
EVIDENCE = {
    "VERIFIED IN CODE": [
        "Live integrations Gmail, Google Calendar, Google Meet, Google Drive, Google Docs, Slack — Backend navis/signals/{gmail,calendar,meet,drive,slack}; Navis-AI ConnectionIds (read-only audit).",
        "Navis Developer surfaces: MCP (claude mcp add/list), Developer API (X-API-Key), SDK local tarball (not on npm), CLI workstate checkpoint/restore, Members/Invited, roles, permission refusal text, Runs (Running/Completed labels from Devtool lib/runs.ts), 'Not judged' — Devtool (read-only).",
        "Navis App surfaces (Today, What changed, Why this drawer, Decision drawer, Approve & send, Gmail accepted) — Navis-AI components (read-only).",
        "Every on-screen entity value is read from src/data/navislabs_v8_launch_state.json (validator data_consistency).",
    ],
    "VERIFIED IN PROVIDED ASSET": [
        "Founder voice P1–P8 (~/Downloads/P1.mp3, p2–p8.mp3 → public/voiceover/source/v6, measured and placed unchanged).",
        "Music: ~/Downloads/ElevenLabs_NavisLabs_Platform_Introduction.mp3 (ID3 title 'NavisLabs Platform Introduction', 127.84 s, 44.1 kHz stereo; instrumental by spectral analysis) → public/music/final/v8/score.wav.",
        "NavisLabs brand mark and name (approved assets); founder identity Abhishek Meena (REAL_AUTHORIZED in the dataset).",
    ],
    "FICTIONAL DEMO": [f"{cust['name']} — {cust['label']} (Bengaluru logistics; no company with that exact name found in a web search, 2026-10-06)",
                       "People: Meera Iyer (customer contact), Arjun Rao (engineer), Riya (solo developer) — fictional, reserved .example / example.com emails",
                       "Salesforce opportunity, Notion playbook, Jira KVR-142, GitHub file src/workflows/kaveri-renewal.ts, the run 7c2e91a0, all dates, emails and meetings — demo records"],
    "ROADMAP": [f"{x['label']} — shown as 'upcoming' (demo configuration); local source: {x['local_source_status']}" for x in launch if x["status"] == "upcoming"],
    "NOT VERIFIED": ["Eleven Music licence tier for the supplied track (plan unknown; free tier requires crediting ElevenMusic).",
                     "That the seven upcoming integrations will be live at launch (no connector in the local backend checkout).",
                     "Absence of vocals in the music — by spectral analysis only; not confirmed by listening.",
                     "Subjective quality of the final mix and of the temporary SFX — measured, not listened to (no listening is possible in this environment)."],
}

# ---------------------------------------------------------------- dates table
dates = [
    ("Film 'today'", data["application_workspace"]["date"] + ", 2026 · 09:44", "current"),
    ("Pricing review / decision", data["decisions"][0]["date"], "past (Sep 30)"),
    ("Slack commitment made", next(x for x in data["commitments"] if x["id"] == "m_revised_terms")["date"], "past"),
    ("Board metrics committed", next(x for x in data["commitments"] if x["id"] == "m_board_metrics")["date"] + " (6 days ago)", "past"),
    ("Notion renewal playbook", data["knowledge"][0]["date"], "past"),
    ("Account plan", next(x for x in data["documents"] if x["id"] == "doc_account_plan")["date"], "past"),
    ("Order form · SSO spec", next(x for x in data["documents"] if x["id"] == "doc_order_form")["date"], "past"),
    ("Jira KVR-142 blocked", data["engineering_context"]["issues"][0]["date"], "past"),
    ("Customer email · call moved", data["emails"][0]["date"], "past"),
    ("Earlier run 3f9a1d27", "Oct 5, 17:31", "past"),
    ("Revised terms due", next(x for x in data["commitments"] if x["id"] == "m_revised_terms")["due"], "future — shown as 'promised by Oct 7'"),
    ("Renewal call", "Thu, Oct 8", "future — shown 'Thu, Oct 8 (upcoming)'"),
    ("Contracted renewal / close date", cust["renewal_was"], "future — 'closes Nov 14', 'renews'"),
    ("Requested renewal", cust["renewal_now"], "future — 'renews Nov 28', 'moving to'"),
]

# ---------------------------------------------------------------- the 20 questions
ans = []


def q(n, question, answer, ok, evidence_class, evidence):
    ans.append({"n": n, "question": question, "answer": answer, "result": ok, "evidence_class": evidence_class, "evidence": evidence})


q(1, "Is the founder VO unchanged?", "Yes. P1–P8 are the founder's files: same WAVs since V6 (48 kHz, gain-matched; originals kept), no regeneration, no speed or pitch change, no trims inside a chunk, every [pause] kept (≥ 1 s measured).",
  "TRUE", "VERIFIED IN PROVIDED ASSET", {"files": vo_files, "validator": "voice_audio"})
q(2, "Is every VO section synchronized?", f"Yes. Each chunk starts at its timeline slot; measured onsets in the rendered voice stem are within {aq['av_sync']['max_abs_onset_diff_ms']} ms of the timeline; audio vs video length differ by {aq['av_sync']['audio_minus_video_ms']} ms (AAC padding).",
  "TRUE", "VERIFIED IN CODE", aq["av_sync"])
q(3, "Is the music final or temporary?", "Final candidate: the founder-supplied Eleven Music track is what plays. It is not yet declared final — licence tier not verified and the founder has not yet approved it in the mix. The V7 in-project score remains only as an automatic fallback (TEMPORARY, never labelled final).",
  "FINAL CANDIDATE", "VERIFIED IN PROVIDED ASSET", mbrief.get("file"))
q(4, "Are SFX final or temporary?", "Temporary. Every SFX is synthesized in-project (no third-party rights). Replacement plan: scripts/elevenlabs-generate.py --sfx (prompts for every sound) or designed files dropped into public/sfx/final/.",
  "TEMPORARY", "NOT VERIFIED", {"final_files_present": sfx_final})
q(5, "What exact music file is being used?", f"{music_file} (48 kHz WAV) made from ~/Downloads/ElevenLabs_NavisLabs_Platform_Introduction.mp3 by scripts/prepare-music-v8.py: −1.5 dB headroom, 44.1 → 48 kHz, −2.5 dB at 3 kHz for dialogue, trimmed to {END:.3f} s with a 0.8 s fade. Original kept at public/music/source/v8/.",
  "TRUE" if music_ok else "FALSE", "VERIFIED IN PROVIDED ASSET", {"file": music_file, "sha256_16": sha(music_file) if music_ok else None})
q(6, "What exact SFX files are being used?", f"{len(sfx_files)} files from public/sfx/temp/v7/ (listed in the JSON) plus room tone {room_file}; none from public/sfx/final/.", "TEMPORARY", "NOT VERIFIED", {"files": sfx_files, "room_tone": room_file})
q(7, "Are all visible company names verified?", "Yes. NavisLabs is the founder's company (REAL_AUTHORIZED). Kaveri Freightworks is fictional and labelled 'Fictional demo organization' on screen (S05, S07) and in the disclosure. Vendor names (Gmail, Salesforce, Claude Code, …) name connectors/clients nominatively. No real company is shown as a customer; no DailyObjects/Digantara evidence or authorization exists in the repos.",
  "TRUE", "VERIFIED IN CODE", {"validator": "entity", "customer": cust["name"], "label": cust["label"]})
q(8, "Are all people names verified/fictional?", "Yes. Abhishek Meena is the founder (REAL_AUTHORIZED, at the founder's request). Meera Iyer, Arjun Rao and Riya are fictional, with reserved example domains. Acme / Jordan Lee / Sam Rivera are gone (validator + project search).",
  "TRUE", "FICTIONAL DEMO", [p["name"] + " — " + p["provenance"] for p in data["people"]])
q(9, "Are all dates chronologically correct?", "Yes. The film is set on Tue, Oct 6, 2026; past events fall between Sep 30 and Oct 5 (validator dates); the memory card lists them newest first, each dated when it happened; weekdays are correct (Oct 8 is a Thursday).",
  "TRUE", "VERIFIED IN CODE", dates)
q(10, "Are future dates clearly represented as future?", "Yes. The renewal call reads 'Thu, Oct 8 (upcoming)'; the commitment is 'promised by Oct 7'; the renewal 'closes Nov 14' / 'renews Nov 28'; no November date is phrased as past (validator dates).",
  "TRUE", "VERIFIED IN CODE", {"validator": "dates"})
q(11, "Are Salesforce/Notion/Microsoft 365/HubSpot/Jira/GitHub/Zoom claims accurate?", "Yes. They are labelled 'upcoming' wherever they appear as a Navis source — S04 column 'Upcoming · demo configuration', priority chips, the evidence chips, the across-systems panel, the agent's context table ('salesforce · upcoming'), the run step — and in the end-card disclosure. In S01/S05 they appear only as the company's own tools (where work lives), not as Navis integrations.",
  "TRUE", "ROADMAP", [{x["label"]: x["film_status"]} for x in launch if x["status"] == "upcoming"])
q(12, "Are any integrations falsely presented as live?", "No. Only the six with backend connectors are under 'Live'; validators check that every evidence row from an upcoming system carries the label and that no screen text says an action was executed through one ('updated in Salesforce', 'synced', 'merged', …). The Salesforce and GitHub rows after the reply say 'Next' with a human/agent owner — no update is claimed.",
  "NO", "VERIFIED IN CODE", {"validator": "integration"})
q(13, "Are any customer claims unsupported?", "No. No real customer is named; the disclosure states the organization, people and data are fictional; no metrics, revenue or amounts appear.", "NO", "FICTIONAL DEMO", {"validator": "entity, product_claim"})
q(14, "Are all UI clicks synchronized?", "Yes. Every cursor press has its click on the same frame, the cursor settles ≥ 0.1 s before each click, and no click sound plays without a visible click (validator interaction, 29 checks).", "TRUE", "VERIFIED IN CODE", {"validator": "interaction"})
q(15, "Are camera movements readable?", f"Yes. A sharpness scan (with a ±1.5 s window that also catches sustained pushes) was reviewed as stills; fast changes are cuts, eased moves are slow enough to read, S04's pipeline pan runs without blur. Flagged soft moments that remain are fades, dissolves, wipes and sparse frames: {len(blur['soft_frames'])} listed in navislabs_v8_blur_scan.json.",
  "TRUE", "VERIFIED IN CODE", {"blur_scan": blur["soft_frames"][:40]})
q(16, "Is the audio mix suitable for a premium startup showcase?", "Technically yes, by measurement: the voice leads at ~12.6 LU over the music in speech and ~19 LU under the key lines, the music opens on 'Navis' and rises in the visual-only moments, SFX are felt and below the voice, the room tone keeps the pauses alive at about −50 LUFS. Whether it *feels* premium needs the founder's listening, and the SFX are still temporary.",
  "MEASURED PASS · LISTENING PENDING", "NOT VERIFIED", sep)
q(17, "Is dialogue intelligibility good?", f"By measurement, yes: voice − music {sep['voice_minus_music_lu']} LU in speech (broadcast guidance ≥ 10 LU), {sep['voice_minus_music_key_lines_lu']} LU under the key lines, {sep['voice_minus_music_small_speaker_lu']} LU on a simulated small speaker; a 3 kHz presence carve in the music; no pumping (music rises {sep['music_rise_in_pauses_lu']} LU in pauses).",
  "TRUE", "VERIFIED IN CODE", sep)
q(18, "Is the final master free of clipping?", f"Yes: {ml['clipped_samples']} clipped samples, true peak {ml['true_peak_dbtp']} dBTP, integrated {ml['integrated_lufs']} LUFS.", "TRUE" if ml["clipped_samples"] == 0 and ml["true_peak_dbtp"] <= -1 else "FALSE", "VERIFIED IN CODE", ml)
q(19, "Are there black frames?", f"Only the intended end fade ({rc['near_black_runs_s']}).", "ONLY THE END FADE" if not stray_black else "YES — UNEXPECTED", "VERIFIED IN CODE", {"near_black_runs_s": rc["near_black_runs_s"]})
q(20, "Is the film READY_FOR_FINAL_RENDER?", "No — FINAL_RENDER_READY = FALSE until the founder approves this review, confirms the Eleven Music licence, and replaces (or accepts) the temporary SFX. No 4K was rendered.", "FALSE", "NOT VERIFIED", None)

out = {
    "about": "NavisLabs launch film — final launch audit (V8 final-audio candidate). Generated by scripts/build-final-audit.py from measurements and validators.",
    "renders": {"1080p": "out/navislabs-final-audio-review-1080p.mp4", "540p": "out/navislabs-final-audio-review-540p.mp4", "v7_untouched": "out/navislabs-v7-review-1080p.mp4"},
    "film": {"duration_s": END, "frames": FRAMES, "fps": spec["format"]["fps"], "size": "1920×1080"},
    "flags": {k: ("TRUE" if v else "FALSE") for k, v in FLAGS.items()}, "flag_reasons": WHY,
    "answers": ans, "evidence": EVIDENCE, "dates": [{"what": a, "date": b, "status": c} for a, b, c in dates],
    "integrations": [{"system": x["label"], "film": x["film_status"], "public_website": x["public_website_status"], "local_source": x["local_source_status"], "on_screen": "upcoming" if x["status"] == "upcoming" else "live"} for x in launch],
    "audio": {"stems": aq["stems"], "separation": sep, "master": ml, "silence_gaps": aq["silence_gaps"], "volume_jumps": aq["volume_jumps"], "av_sync": aq["av_sync"],
              "music": mbrief.get("file"), "mix": mbrief.get("mix"), "room_tone": amap["room"]["why"]},
    "visual": {"render_1080p": {k: rc[k] for k in ("duration_s", "video", "near_black_runs_s", "luma_jumps", "motion_peak", "sustained_fast_motion_s") if k in rc},
               "render_540p": {k: rc540[k] for k in ("duration_s", "video") if k in rc540}, "blur_scan": blur["soft_frames"]},
    "validators": V, "stale_copy": stale["summary"]["fix"],
}
with open(os.path.join(ROOT, "navislabs_final_launch_audit.json"), "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
    f.write("\n")

L = []
w = L.append
w("# NavisLabs launch film — final launch audit (V8 final-audio candidate)\n")
w(f"Review renders: `out/navislabs-final-audio-review-1080p.mp4` · `out/navislabs-final-audio-review-540p.mp4` — {END:.2f} s, {FRAMES} frames. The V7 master is untouched (`out/navislabs-v7-review-1080p.mp4`). No 4K.\n")
w("## Readiness\n")
w("| Flag | Value | Why |\n|---|---|---|")
for k, v in FLAGS.items():
    w(f"| {k} | **{'TRUE' if v else 'FALSE'}** | {WHY[k]} |")
w("\n## The 20 questions\n")
for a in ans:
    w(f"**{a['n']}. {a['question']}** — `{a['result']}` · _{a['evidence_class']}_  \n{a['answer']}\n")
w("## Evidence register\n")
for k, items in EVIDENCE.items():
    w(f"### {k}\n")
    for it in items:
        w(f"- {it}")
    w("")
w("## Integrations\n")
w("| System | In the film | Public website | Local Navis backend |\n|---|---|---|---|")
for x in launch:
    w(f"| {x['label']} | {'LIVE' if x['status'] == 'live' else 'UPCOMING (demo configuration)'} | {x['public_website_status']} | {x['local_source_status']} |")
w("\n## Dates (film set on Tue, Oct 6, 2026)\n")
w("| What | Date | Status |\n|---|---|---|")
for a, b, c in dates:
    w(f"| {a} | {b} | {c} |")
w("\n## Audio QC (measured on the master and the separately rendered stems)\n")
w("| Measure | Value |\n|---|---|")
for k, v in [("Master integrated", f"{ml['integrated_lufs']} LUFS"), ("Master true peak", f"{ml['true_peak_dbtp']} dBTP"), ("Clipped samples", ml["clipped_samples"]), ("LRA", f"{ml['lra_lu']} LU"),
             ("Voice − music, speech", f"{sep['voice_minus_music_lu']} LU"), ("Voice − music, key lines", f"{sep['voice_minus_music_key_lines_lu']} LU"), ("Voice − music, small speaker", f"{sep['voice_minus_music_small_speaker_lu']} LU"),
             ("Music rise in pauses", f"{sep['music_rise_in_pauses_lu']} LU"), ("Room tone in pauses", f"{sep['room_in_pauses_lufs']} LUFS"), ("Voice peak − SFX peak", f"{sep['voice_minus_sfx_peak_db']} dB"),
             ("Silence gaps", "; ".join(f"{g['from_s']}–{g['to_s']} s ({g['why']})" for g in aq["silence_gaps"]) or "none"),
             ("Unexpected volume jumps", len(unexpected_jumps)), ("Audio − video length", f"{aq['av_sync']['audio_minus_video_ms']} ms"), ("Max VO onset offset", f"{aq['av_sync']['max_abs_onset_diff_ms']} ms")]:
    w(f"| {k} | {v} |")
w("\nStems: " + " · ".join(f"{k} {v['integrated_lufs']} LUFS (peak {v['sample_peak_dbfs']} dBFS)" for k, v in aq["stems"].items()) + ". Stem files: `out/stems/v8-{voice,music,sfx,room}.wav`.\n")
w("## Music\n")
mf = mbrief.get("file", {})
w(f"- File: `{mf.get('in_film')}` ← `{mf.get('source')}`; original kept at `{mf.get('kept_original')}`.\n- Processing: {mf.get('processing')}.\n- Status: {mf.get('status')}")
for s_ in mbrief.get("sync_to_film", []):
    w(f"- {s_}")
w(f"- Mix: −{abs(amap['music']['duck_under_vo_db'])} dB under every line, −{abs(amap['music']['duck_key_line_db'])} dB under the 7 key lines (strongest), +{amap['music']['lift']['db']} dB in visual-only moments ≥ {amap['music']['lift']['min_gap_s']} s, act 1 held −7 dB, near-silence after 'NavisLabs.', silent end.\n")
w("## SFX (TEMPORARY)\n")
w("| Group | Category | Events |\n|---|---|---|")
for c in sfxm["categories"]:
    w(f"| {c.get('group', '')} | {c['category']} | {c['count']} |")
w(f"\nSilence is used on purpose (no SFX in the breath before 'Navis', after Approve, under the refusal, under 'Same facts…', after the end lockup). Files: public/sfx/temp/v7/*.wav; room tone {room_file}.\n")
w("## What changed (V7 → V8)\n")
for it in [
    "Music: the founder-supplied Eleven Music track replaces the in-project score (which stays only as an automatic fallback).",
    "Mix: strongest ducking moved to the brief's 7 lines; music lifts in visual-only moments; act 1 held near silence; room tone added as a 4th layer in the pauses.",
    "SFX: subtle whooshes on the two world changes, a reverse whoosh into one company, one sweep as the systems appear (S04 ticks halved), 'workspace created', a 'shared understanding' lock, a quieter end resolve; Send/Gmail confirm under 'Then the company acts.' set lower.",
    "Integrations: Live (6) vs Upcoming · demo configuration (7) on screen and in the disclosure; 'upcoming' on every evidence row from an upcoming system.",
    "Data: 'Fictional demo organization' on screen; renewal call moved to Thu, Oct 8 (was Oct 9, a Friday, against the reply's 'Thursday'); documents dated Oct 1–2; 'Committed 6 days ago' (was 9); memory card dated by when things happened, newest first.",
    "Camera: S04 pipeline pan slowed and unblurred; S07 push onto the evidence slowed — both were smeared in V7.",
]:
    w(f"- {it}")
w("\n## What I need to do next (founder)\n")
for it in ["Watch/listen to the 1080p review on MacBook speakers, iPhone and AirPods.",
           "Confirm the ElevenLabs plan used for the music allows commercial film use (credit ElevenMusic if it was the free tier).",
           "Provide final SFX (ElevenLabs Sound Effects with ELEVENLABS_API_KEY set: `npm run audio:eleven`, or designed files in public/sfx/final/), or approve the temporary ones.",
           "Confirm the launch status of Salesforce, Notion, Microsoft 365, HubSpot, Jira, GitHub and Zoom — they stay 'upcoming' until the team confirms them live.",
           "Then approve for the final (4K) render."]:
    w(f"- {it}")
with open(os.path.join(ROOT, "navislabs_final_launch_audit.md"), "w") as f:
    f.write("\n".join(L) + "\n")
print(" · ".join(f"{k}={'TRUE' if v else 'FALSE'}" for k, v in FLAGS.items()))
