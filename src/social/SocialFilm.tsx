import { Audio } from "@remotion/media";
import { AbsoluteFill, Easing, Freeze, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";
import { FILM, FONT } from "../config/navisBrand";
import plan from "./navislabs_social_v1_plan.json";

// NavisLabs SOCIAL V1 — a 4:5 (1080×1350) social launch cut edited from the approved V7 film.
// Picture: the V7 master (via a 1.5× proxy) reframed shot by shot for 4:5; voice: the founder's
// own recordings cut at measured line boundaries; music: the founder-supplied Eleven Music track
// re-edited to the social arc; SFX only on visible actions; captions burned in for sound-off
// viewing. Everything is read from navislabs_social_v1_plan.json (scripts/build-social-v1.py).
// V7 and V8 are untouched: this composition only reads their outputs.

export const SOCIAL_FPS = plan.fps;
export const SOCIAL_FRAMES = plan.frames;
const F = (s: number) => Math.round(s * SOCIAL_FPS);
const PROXY = plan.picture.proxy_scale; // proxy pixels per V7 pixel
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const dbToGain = (db: number) => (db <= -90 ? 0 : 10 ** (db / 20));
const inOut = Easing.bezier(0.45, 0, 0.55, 1);

type Key = { src: number; cx: number; cy: number; s: number };
type Shot = (typeof plan.shots)[number];
type Panel = { label: string; label_y: number; y0: number; y1: number; cx: number; cy: number; s: number };

/** Reframe parameters at source time `t` (V7 seconds, or shot-local seconds for stills). */
const frameAt = (keys: readonly Key[], t: number) => {
  if (keys.length === 0) return null;
  if (t <= keys[0].src) return keys[0];
  for (let i = 1; i < keys.length; i++) {
    const a = keys[i - 1];
    const b = keys[i];
    if (t <= b.src) {
      const p = interpolate(t, [a.src, b.src], [0, 1], { ...CLAMP, easing: inOut });
      return { src: t, cx: a.cx + (b.cx - a.cx) * p, cy: a.cy + (b.cy - a.cy) * p, s: a.s + (b.s - a.s) * p };
    }
  }
  return keys[keys.length - 1];
};

/** The V7 picture (video, or a held frame of the same video) with V7 point (cx, cy) at output (ox, oy), scaled by s.
 *  Holds freeze the proxy itself, so a held frame decodes exactly like the frame before the cut. */
const Picture: React.FC<{ readonly shot: Shot; readonly cx: number; readonly cy: number; readonly s: number; readonly ox: number; readonly oy: number; readonly feather: boolean }> = ({ shot, cx, cy, s, ox, oy, feather }) => {
  const px = s / PROXY;
  const video = <OffthreadVideo src={staticFile(plan.picture.proxy)} trimBefore={F(shot.src_in)} muted style={{ width: 2880, height: 1620, display: "block" }} />;
  const media = shot.layout === "still" ? <Freeze frame={0}>{video}</Freeze> : video;
  const fadeX = "linear-gradient(to right, transparent 0%, black 5%, black 95%, transparent 100%)";
  const fadeY = "linear-gradient(to bottom, transparent 0%, black 7%, black 93%, transparent 100%)";
  return (
    <div style={{ position: "absolute", left: ox - cx * s, top: oy - cy * s, width: 2880, height: 1620, transform: `scale(${px})`, transformOrigin: "0 0" }}>
      <div style={feather ? { width: "100%", height: "100%", maskImage: fadeX, WebkitMaskImage: fadeX } : { width: "100%", height: "100%" }}>
        <div style={feather ? { width: "100%", height: "100%", maskImage: fadeY, WebkitMaskImage: fadeY } : { width: "100%", height: "100%" }}>{media}</div>
      </div>
    </div>
  );
};

const Label: React.FC<{ readonly children: React.ReactNode; readonly y: number; readonly opacity?: number }> = ({ children, y, opacity = 1 }) => (
  <div style={{ position: "absolute", left: 0, right: 0, top: y, textAlign: "center", fontFamily: FONT.mono, fontSize: 22, letterSpacing: "0.34em", color: FILM.onInkMuted, opacity }}>{children}</div>
);

const ShotView: React.FC<{ readonly shot: Shot }> = ({ shot }) => {
  const f = useCurrentFrame();
  const local = f / SOCIAL_FPS;
  if (shot.layout === "split" && "panels" in shot && shot.panels) {
    const src = shot.src_in + local;
    return (
      <AbsoluteFill style={{ backgroundColor: shot.bg }}>
        {(shot.panels as Panel[]).map((p, i) => {
          const h = p.y1 - p.y0;
          // The agent's view arrives with the V7 picture (it appears at V7 1.6 s).
          const show = i === 0 ? 1 : interpolate(src, [1.45, 1.75], [0, 1], CLAMP);
          return (
            <div key={p.label}>
              <Label y={p.label_y} opacity={show}>
                {p.label}
              </Label>
              <div style={{ position: "absolute", left: 0, top: p.y0, width: 1080, height: h, overflow: "hidden" }}>
                <Picture shot={shot} cx={p.cx} cy={p.cy} s={p.s} ox={540} oy={h / 2} feather={false} />
              </div>
            </div>
          );
        })}
        <div style={{ position: "absolute", left: 140, right: 140, top: 598, height: 1, backgroundColor: "rgba(237,235,230,0.12)" }} />
      </AbsoluteFill>
    );
  }
  const t = shot.layout === "still" ? local : shot.src_in + local;
  const k = frameAt(shot.keys as Key[], t) ?? { cx: 960, cy: 540, s: 1 };
  const clip = "clip_bottom" in shot ? (shot.clip_bottom as number) : null;
  // Edge masks: clip_bottom hides V7 below a fixed output line (short 16 px fade); top_fade softens the
  // V7 frame's top edge, top_cut (V7 px) first hides a strip at V7's top. Both follow the camera.
  const topFade = "top_fade" in shot ? (shot.top_fade as number) : 0;
  const topCut = "top_cut" in shot ? (shot.top_cut as number) : 0;
  const top = shot.oy - (k.cy - topCut) * k.s;
  const bottom = clip ?? 1350;
  const clipFade = "clip_fade" in shot ? (shot.clip_fade as number) : 16;
  const edgeMask =
    clip || topFade > 0
      ? `linear-gradient(to bottom, ${topFade > 0 ? `transparent ${top}px, black ${top + topFade}px` : "black 0px"}, black ${bottom - (clip ? clipFade : 0)}px, ${clip ? "transparent" : "black"} ${bottom}px)`
      : undefined;
  // A shot may fade its picture to its background as it ends (the thesis, with its type).
  const fadeOut = "fade_out" in shot ? (shot.fade_out as number) : 0;
  const op = fadeOut > 0 ? interpolate(local, [shot.dur - fadeOut, shot.dur], [1, 0], { ...CLAMP, easing: Easing.in(Easing.quad) }) : 1;
  // side_fade: the output frame's left/right edges fade to the background (neighbouring cards in a macro).
  const side = "side_fade" in shot ? (shot.side_fade as number) : 0;
  // clip_right: hide V7 right of a fixed output line (24 px fade) — e.g. integrations that are not live yet.
  const clipRight = "clip_right" in shot ? (shot.clip_right as number) : 0;
  const sideMask =
    side > 0
      ? `linear-gradient(to right, transparent 0px, black ${side}px, black ${1080 - side}px, transparent 1080px)`
      : clipRight > 0
        ? `linear-gradient(to right, black 0px, black ${clipRight - 24}px, transparent ${clipRight}px)`
        : undefined;
  const pic = (
    <AbsoluteFill style={{ opacity: op, maskImage: sideMask, WebkitMaskImage: sideMask }}>
      <Picture shot={shot} cx={k.cx} cy={k.cy} s={k.s} ox={540} oy={shot.oy} feather={"feather" in shot ? Boolean(shot.feather) : false} />
    </AbsoluteFill>
  );
  return (
    <AbsoluteFill style={{ backgroundColor: shot.bg }}>
      {edgeMask ? (
        <div style={{ position: "absolute", inset: 0, height: bottom, overflow: "hidden", maskImage: edgeMask, WebkitMaskImage: edgeMask }}>{pic}</div>
      ) : (
        pic
      )}
    </AbsoluteFill>
  );
};

/** SAME FACTS. SAME SOURCES. SAME FRESHNESS. → ONE UNDERSTANDING. TWO WAYS IN. — on the founder's words. */
const Thesis: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / SOCIAL_FPS;
  const words = plan.overlays.thesis_words;
  const g1 = words.find((w) => w.group === 1)!.at;
  const end = plan.overlays.thesis_end;
  const out0 = interpolate(t, [g1 - 0.25, g1], [1, 0], CLAMP);
  const outAll = interpolate(t, [end - 0.35, end], [1, 0], CLAMP);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", left: 0, right: 0, top: 800, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
        {words.map((w) => {
          const a = interpolate(t, [w.at - 0.05, w.at + 0.3], [0, 1], { ...CLAMP, easing: Easing.out(Easing.cubic) });
          const vis = (w.group === 0 ? out0 : 1) * outAll;
          if (a <= 0 || vis <= 0) return null;
          const big = w.group === 1;
          return (
            <div
              key={w.text}
              style={{
                opacity: a * vis,
                translate: `0 ${(1 - a) * 14}px`,
                fontFamily: FONT.display,
                fontSize: big ? 78 : 60,
                fontWeight: 600,
                letterSpacing: big ? "0.01em" : "0.06em",
                color: w.text.startsWith("TWO") ? "#FFFFFF" : FILM.onInk,
                lineHeight: 1.08,
                textAlign: "center",
                boxShadow: w.text.startsWith("TWO") ? `inset 0 -${4 * a}px 0 ${FILM.cobalt}` : undefined,
                paddingBottom: w.text.startsWith("TWO") ? 6 : 0,
              }}
            >
              {w.text}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Burned-in captions: restrained, high contrast, ≤ 2 lines, inside the 4:5 safe area. */
const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / SOCIAL_FPS;
  const c = plan.captions.find((x) => x.burn && t >= x.start - 0.05 && t < x.end);
  if (!c) return null;
  const a = Math.min(interpolate(t, [c.start - 0.05, c.start + 0.1], [0, 1], CLAMP), interpolate(t, [c.end - 0.12, c.end], [1, 0], CLAMP));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 132, display: "flex", justifyContent: "center", opacity: a }}>
      <div
        style={{
          maxWidth: 960,
          padding: "16px 30px 18px",
          borderRadius: 18,
          backgroundColor: "rgba(14,13,10,0.80)",
          boxShadow: "0 18px 40px -18px rgba(0,0,0,0.55)",
          fontFamily: FONT.display,
          fontSize: 44,
          fontWeight: 600,
          lineHeight: 1.22,
          letterSpacing: "-0.005em",
          color: "#F4F2EE",
          textAlign: "center",
        }}
      >
        {c.lines.map((l) => (
          <div key={l}>{l}</div>
        ))}
      </div>
    </div>
  );
};

const Disclosure: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / SOCIAL_FPS;
  const d = plan.overlays.disclosure;
  const a = interpolate(t, [d.from, d.from + 0.5], [0, 0.85], CLAMP);
  if (a <= 0) return null;
  return (
    <div style={{ position: "absolute", left: 90, right: 90, bottom: 120, opacity: a, fontFamily: FONT.display, fontSize: 21, lineHeight: 1.5, textAlign: "center", color: FILM.onInkMuted }}>{d.text}</div>
  );
};

// ------------------------------------------------------------------ audio
type Curve = { t: number[]; db: number[] };
const at = (c: Curve, t: number) => interpolate(t, c.t, c.db, CLAMP);
const M = plan.music;

const SocialAudio: React.FC<{ readonly stem: "mix" | "voice" | "music" | "sfx" }> = ({ stem }) => {
  const on = (g: string) => stem === "mix" || stem === g;
  return (
    <>
      {on("voice")
        ? plan.voice.map((v) => {
            const len = v.src_out - v.src_in;
            return (
              <Sequence key={v.id} name={`VO ${v.id}`} from={F(v.at)} durationInFrames={Math.max(1, F(v.at + len) - F(v.at))} layout="none">
                <Audio src={staticFile(v.file)} trimBefore={F(v.src_in)} volume={(fr) => interpolate(fr / SOCIAL_FPS, [0, 0.02, len - 0.04, len], [0, 1, 1, 0], CLAMP)} />
              </Sequence>
            );
          })
        : null}
      {on("music")
        ? M.segments.map((sg) => {
            const len = sg.end - sg.at;
            return (
              <Sequence key={sg.id} name={`Music ${sg.id}`} from={F(sg.at)} durationInFrames={Math.max(1, F(sg.end) - F(sg.at))} layout="none">
                <Audio
                  src={staticFile(M.file)}
                  trimBefore={F(sg.src)}
                  volume={(fr) => {
                    const lt = fr / SOCIAL_FPS;
                    const gt = sg.at + lt;
                    const fin = sg.fade_in > 0 ? Math.sin((Math.min(1, lt / sg.fade_in) * Math.PI) / 2) : 1;
                    const fout = sg.fade_out > 0 ? Math.cos((Math.max(0, (lt - (len - sg.fade_out)) / sg.fade_out) * Math.PI) / 2) : 1;
                    return dbToGain(M.gain_db + at(M.curves.duck, gt) + at(M.curves.shape, gt)) * fin * Math.max(0, fout);
                  }}
                />
              </Sequence>
            );
          })
        : null}
      {on("sfx")
        ? plan.sfx.map((e, i) => (
            <Sequence key={`${e.sfx}-${i}`} name={`SFX ${e.sfx}`} from={F(e.at)} durationInFrames={F(1.6)} layout="none">
              <Audio src={staticFile(e.file)} volume={dbToGain(e.gain_db)} />
            </Sequence>
          ))
        : null}
    </>
  );
};

export const SocialFilm: React.FC<{ readonly stem?: "mix" | "voice" | "music" | "sfx" }> = ({ stem = "mix" }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: FILM.ink }}>
      {plan.shots.map((s) => (
        <Sequence key={s.id} name={`${s.id} · V7 ${s.src_in.toFixed(2)}`} from={F(s.at)} durationInFrames={F(s.at + s.dur) - F(s.at)}>
          <ShotView shot={s} />
        </Sequence>
      ))}
      <Thesis />
      <Captions />
      <Disclosure />
      <SocialAudio stem={stem} />
    </AbsoluteFill>
  );
};
