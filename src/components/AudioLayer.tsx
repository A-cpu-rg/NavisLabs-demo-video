import { Audio } from "@remotion/media";
import { AbsoluteFill, interpolate, Sequence, useCurrentFrame } from "remotion";
import { audioMap, resolveSlot, scheduledLines, sfxSlot } from "../config/audioMap";
import { FPS, SFX_EVENTS, sec } from "../config/beats";
import { FONT } from "../config/navisBrand";
import { endFrame, FILM_SCENES, startFrame } from "../config/timeline";

// Voice, music and SFX from navislabs_v8_audio_map.json. Each slot plays its
// FINAL file when present, else its TEMP file, else nothing.

const dbToGain = (db: number) => (db <= -90 ? 0 : 10 ** (db / 20));
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const music = audioMap.music;

// V7: the music is mixed as real volume curves, not one static gain. The builder
// (scripts/build-film-data-v8.py) turns the measured speech windows into a
// keyframed duck curve (−6 dB under a line, −11 dB under a key line, 0.15 s
// attack, 0.6 s release — so the score rises naturally in every pause) and a
// keyframed curve of controlled dips (the breath before Navis, "A person
// decides.", Approve, the refusal, after "NavisLabs.", the silent end). Each
// stem takes its share of the duck (the bed and textures stay more present).
type Keys = { readonly frames: number[]; readonly db: number[] };
const toKeys = (k: { t: number[]; db: number[] } | undefined): Keys | null => (k ? { frames: k.t.map((t) => t * FPS), db: k.db } : null);
const DUCK = toKeys(music.curves?.duck);
const DIPS = toKeys(music.curves?.dips);
const at = (k: Keys | null, f: number) => (k ? interpolate(f, k.frames, k.db, CLAMP) : 0);

// Fallback for maps without curves: duck on the measured speech windows.
const voWindows = (audioMap.speech ?? scheduledLines.map((l) => ({ from_s: l.start_s, to_s: l.end_s ?? l.ceiling_s, key: false }))).map((w) => ({ from: sec(w.from_s), to: sec(w.to_s), key: w.key }));
const KEY_DUCK_DB = music.duck_key_line_db ?? music.duck_under_vo_db;
const legacyDuck = (f: number) => {
  const attack = music.duck_attack_s * FPS;
  const release = music.duck_release_s * FPS;
  let duck = 0;
  for (const w of voWindows) {
    const k = interpolate(f, [w.from - attack, w.from, w.to, w.to + release], [0, 1, 1, 0], CLAMP);
    duck = Math.min(duck, k * (w.key ? KEY_DUCK_DB : music.duck_under_vo_db));
  }
  return duck;
};

const musicVolume = (gainDb: number, duckShare: number) => (f: number) => {
  const duck = DUCK ? at(DUCK, f) : legacyDuck(f);
  return dbToGain(music.gain_db + gainDb + duck * duckShare + at(DIPS, f));
};

const layers = audioMap.layers;

const ROOM = audioMap.room;
const ROOM_KEYS = toKeys(ROOM?.curve);
const roomVolume = (f: number) => dbToGain((ROOM?.gain_db ?? -96) + at(ROOM_KEYS, f));

export const AudioLayer: React.FC<{ readonly stem?: "mix" | "voice" | "music" | "sfx" | "room" }> = ({ stem = "mix" }) => {
  const on = (g: "voice" | "music" | "sfx" | "room") => stem === "mix" || stem === g;
  const room = on("room") && ROOM ? resolveSlot(ROOM) : null;
  // A final, mixed score (e.g. from Eleven Music) replaces the stems; otherwise the stems play.
  const score = on("music") ? resolveSlot(music) : null;
  const stems = on("music") && score?.tier !== "final" ? (music.stems ?? []).map((s) => ({ s, r: resolveSlot(s) })) : [];
  return (
    <>
      {room ? (
        <Sequence name={`Room tone (${room.tier})`} layout="none">
          <Audio src={room.src} volume={roomVolume} />
        </Sequence>
      ) : null}
      {score?.tier === "final" ? (
        <Sequence name="Music (final score)" layout="none">
          <Audio src={score.src} volume={musicVolume(layers.music.gain_db, 1)} />
        </Sequence>
      ) : null}
      {stems.map(({ s, r }) =>
        r ? (
          <Sequence key={s.id} name={`Music · ${s.id} (${r.tier})`} layout="none">
            <Audio src={r.src} volume={musicVolume(layers.music.gain_db + s.gain_db, s.duck)} />
          </Sequence>
        ) : null,
      )}
      {(on("voice") ? scheduledLines : []).map((l) => {
        const r = resolveSlot(l);
        if (!r) return null;
        const from = sec(l.start_s);
        return (
          <Sequence key={l.id} name={`VO ${l.id} (${r.tier})`} from={from} durationInFrames={sec(l.ceiling_s) - from} layout="none">
            <Audio src={r.src} />
          </Sequence>
        );
      })}
      {(on("sfx") ? SFX_EVENTS : []).map((e, i) => {
        const slot = sfxSlot(e.sfx);
        const r = resolveSlot(slot);
        if (!r) return null;
        // Layers: product transitions and UI sounds are mixed as separate groups.
        const layerDb = e.category === "TRANSITION" ? layers.transitions.gain_db : layers.ui_sfx.gain_db;
        return (
          <Sequence key={`${e.sfx}-${i}`} name={`SFX ${e.category}`} from={sec(e.at)} durationInFrames={sec(1.5)} layout="none">
            <Audio src={r.src} volume={dbToGain((slot.gain_db ?? 0) + (e.gainDb ?? 0) + layerDb)} />
          </Sequence>
        );
      })}
    </>
  );
};

// ---------------------------------------------------------------- dev HUD

const Tag: React.FC<{ readonly children: React.ReactNode; readonly strong?: boolean }> = ({ children, strong }) => (
  <div
    style={{
      padding: "5px 10px",
      borderRadius: 6,
      backgroundColor: "rgba(20,19,15,0.72)",
      color: strong ? "#EDEBE6" : "rgba(237,235,230,0.62)",
      fontFamily: FONT.mono,
      fontSize: 12,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      whiteSpace: "nowrap",
      maxWidth: 1100,
      overflow: "hidden",
      textOverflow: "ellipsis",
    }}
  >
    {children}
  </div>
);

/** Development HUD: scene, time, and which audio tier is playing. */
export const DevHud: React.FC = () => {
  const f = useCurrentFrame();
  const scene = FILM_SCENES.find((s) => f >= startFrame(s) && f < endFrame(s)) ?? FILM_SCENES[FILM_SCENES.length - 1];
  const vo = scheduledLines.find((l) => f >= sec(l.start_s) && f < sec(l.ceiling_s));
  const voTier = vo ? (resolveSlot(vo)?.tier ?? "missing") : null;
  const musicTier = resolveSlot(music)?.tier ?? "missing";
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: 20, bottom: 16, display: "flex", gap: 6, flexWrap: "wrap", maxWidth: 1600 }}>
        <Tag strong>
          {scene.id} · {(f / FPS).toFixed(2)} s · f{f}
        </Tag>
        {vo ? <Tag>VO {vo.id} · {voTier}</Tag> : null}
        <Tag>Music · {musicTier}</Tag>
      </div>
    </AbsoluteFill>
  );
};
