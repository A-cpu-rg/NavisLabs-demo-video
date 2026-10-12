#!/usr/bin/env python3
"""Optional: generate the V7 score and SFX with ElevenLabs (Eleven Music + Sound Effects).

  ELEVENLABS_API_KEY=… python3 scripts/elevenlabs-generate.py --sfx            # 22 SFX → public/sfx/final/v7/<name>.wav
  ELEVENLABS_API_KEY=… python3 scripts/elevenlabs-generate.py --music          # one score → public/music/final/v7/score.wav
  python3 scripts/elevenlabs-generate.py --dry-run --sfx --music               # print the prompts / plan, call nothing

The key is read from the environment only — never printed, logged, written to disk or put in JSON.
Never commit .env. Files land in the FINAL slots, which the film prefers over the in-project
synthesized TEMP files (no code change); delete a final file to fall back to the temp one.

APIs (checked 2026-10-06, elevenlabs.io/docs):
  Sound Effects  POST /v1/sound-generation?output_format=pcm_48000   {text, duration_seconds 0.5–30, prompt_influence 0–1}
  Eleven Music   POST /v1/music?output_format=pcm_48000              {model_id music_v2_5, composition_plan{chunks[]}, force_instrumental}
Terms: Eleven Music commercial use needs a paid plan, and the Starter plan excludes films, advertising and
broadcast — a launch film needs Creator or above. Check the account's plan before using a generated score.
"""
import json
import os
import subprocess
import sys
import urllib.request
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.elevenlabs.io/v1"
AUDIO = json.load(open(os.path.join(ROOT, "navislabs_v8_audio_map.json")))
args = set(sys.argv[1:])
DRY = "--dry-run" in args

SFX_PROMPTS = {
    "key1": ("single soft laptop keyboard keystroke, scissor switch, close mic, dry small room, one-shot", 0.5),
    "key2": ("single soft laptop keystroke, slightly lower, close mic, dry, one-shot", 0.5),
    "key3": ("single light laptop keystroke, crisp, close mic, dry, one-shot", 0.5),
    "key4": ("single laptop keystroke, muted, close mic, dry, one-shot", 0.5),
    "enter": ("laptop Enter key press, firm, short, close mic, dry small room, one-shot", 0.5),
    "save": ("two tiny soft UI ticks then a quiet low confirmation tone, minimal, premium, one-shot", 0.6),
    "click": ("MacBook trackpad click, press and release, very close, dry, subtle, one-shot", 0.5),
    "data": ("tiny glassy digital tick, data arriving, very short, soft, premium UI, one-shot", 0.5),
    "source": ("soft UI chip appearing, gentle short upward pop with a little air, minimal, premium, one-shot", 0.5),
    "connect": ("two soft rising bell tones, connection established, warm, minimal, premium software, one-shot", 1.0),
    "surface": ("one tiny soft tick-tone, an interface element lighting up, subtle, one-shot", 0.5),
    "api": ("three quick tiny digital glints settling into one soft tone, API response, minimal, one-shot", 0.6),
    "retrieve": ("short stream of fine digital ticks rising into a soft tone, information being gathered, subtle, one-shot", 0.8),
    "deny": ("serious low tonal shift, two soft low notes a semitone apart, dark, restrained, not an error buzzer, not a game sound", 1.0),
    "approve": ("crisp UI button press followed by a small warm positive two-note confirmation, premium, subtle", 0.7),
    "sent": ("short soft airy upward movement, message sent, gentle, not a whoosh, minimal", 0.5),
    "gmail": ("gentle two-tone notification chime, D and A, satisfying but subtle, premium, soft attack", 1.0),
    "run": ("soft low pulse with a short rising tone, a process starting, minimal, premium", 0.6),
    "complete": ("resolving three-note soft chime D F# A, task complete, warm, premium, subtle", 1.2),
    "reveal": ("low warm bloom with a soft high harmonic shimmer, a brand mark appearing, cinematic but restrained, no boom, no braam", 2.5),
    "air": ("soft filtered air movement, a scene transition, low and short, very subtle, not a swoosh", 0.8),
    "end": ("deep soft tonal bloom with a long gentle tail, a final logo, restrained, elegant, no boom", 3.0),
}


def key():
    k = os.environ.get("ELEVENLABS_API_KEY", "")
    if not k and not DRY:
        sys.exit("ELEVENLABS_API_KEY is not set in the environment. Nothing was generated.")
    return k


def post(path, body, out_format="pcm_48000"):
    req = urllib.request.Request(f"{API}{path}?output_format={out_format}", data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key(), "Content-Type": "application/json", "Accept": "audio/*"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def write_pcm(path, pcm, channels=1):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm)


if "--sfx" in args:
    for name, (prompt, dur) in SFX_PROMPTS.items():
        assert name in AUDIO["sfx"]["library"], name
        dest = os.path.join(ROOT, "public", AUDIO["sfx"]["library"][name]["final"])
        if DRY:
            print(f"SFX {name:9s} {dur:>4}s  {prompt}")
            continue
        pcm = post("/sound-generation", {"text": prompt, "duration_seconds": max(0.5, dur), "prompt_influence": 0.6})
        write_pcm(dest, pcm)
        print("wrote", os.path.relpath(dest, ROOT))

if "--music" in args:
    # Eleven Music v2.5 (model_id music_v2_5): the composition plan is a list of chunks whose
    # durations are enforced. One chunk per film section, on the founder's measured voice.
    secs = AUDIO["music"]["sections"]
    plan = {"chunks": [{
        "text": f"[{sx['id']} · {sx['role']}] {{instrumental}} {sx['brief'][:300]}",
        "duration_ms": int(round((sx["to_s"] - sx["from_s"]) * 1000)),
        "positive_styles": ["premium cinematic technology score", "warm analog synth texture", "clear memorable motif", "restrained percussion",
                            "evolving harmonic bed", "instrumental", "leaves room for a spoken voice"] if i == 0 else [sx["role"], "instrumental", "leaves room for a spoken voice"],
        "negative_styles": ["EDM", "cyberpunk", "trailer braams", "booms", "cheesy piano", "corporate stock music", "vocals"],
        "context_adherence": "high" if i else "medium",
    } for i, sx in enumerate(secs)]}
    if DRY:
        print(json.dumps(plan, indent=1))
    else:
        pcm = post("/music", {"composition_plan": plan, "force_instrumental": True, "model_id": "music_v2_5"})
        # Never overwrite the film's current score automatically: write a candidate and prepare it on purpose.
        cand = os.path.join(ROOT, "public", "music", "source", "v8", "eleven-music-v2_5-candidate.wav")
        write_pcm(cand, pcm, channels=2)
        print("wrote", os.path.relpath(cand, ROOT), "— listen, confirm the plan allows commercial use, then: python3 scripts/prepare-music-v8.py", cand)

if not ({"--sfx", "--music"} & args):
    print(__doc__)
