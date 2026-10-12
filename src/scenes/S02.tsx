import { AbsoluteFill, interpolate } from "remotion";
import { BEAT, sec } from "../config/beats";
import { copy } from "../config/filmSpec";
import { FILM, FONT, type IntegrationId } from "../config/navisBrand";
import { Grain } from "../components/World";
import { BrandTile } from "../ui/Integrations";
import { CLAMP, caretOn, easeInOut, useSceneClock } from "../ui/kit";
import { HAND_COPIES, HAND_NOTE_TITLE } from "../ui/demoContent";
import { arcPoint, FilmLabel, UiCursor } from "./shared";

// S02 · 6.2–10.3 s · V03 "People rebuild it by hand. Agents start without it."
// Left, PEOPLE: a cursor copies the renewal's pieces out of four systems into
// a note, one at a time. Right, AI AGENTS: a new session with none of it. Then
// black, and a breath before NavisLabs.

const r = (T: number, a: number, b: number, e?: (x: number) => number) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

const SOURCES: readonly { id: IntegrationId; text: string; x: number }[] = HAND_COPIES.map((h, i) => ({ ...h, x: 120 + i * 210 }));
const COPIES = [
  { from: 0, at: BEAT.copy1 },
  { from: 2, at: BEAT.copy2 },
  { from: 3, at: BEAT.copy3 },
];
const NOTE = { x: 150, y: 560, w: 660, h: 300 };

export const S02: React.FC = () => {
  const { t, T } = useSceneClock("S02");
  const agents = r(T, BEAT.agentsStart - 0.2, BEAT.agentsStart + 0.5, easeInOut);
  const peopleDim = 1 - 0.45 * agents;
  const black = r(T, BEAT.blackout, BEAT.blackout + 0.3, easeInOut);
  const lineY = (k: number) => NOTE.y + 92 + k * 52;

  const cursor = (() => {
    const home = { x: 700, y: 900 };
    for (let k = COPIES.length - 1; k >= 0; k--) {
      const c = COPIES[k];
      const src = { x: SOURCES[c.from].x + 30, y: 330 };
      const dst = { x: NOTE.x + 60, y: lineY(k) };
      if (T >= c.at - 0.3) {
        const pick = r(T, c.at - 0.3, c.at, easeInOut);
        const carry = r(T, c.at, c.at + 0.45, easeInOut);
        const prev = k === 0 ? home : { x: NOTE.x + 60, y: lineY(k - 1) };
        return carry > 0 ? arcPoint(src, dst, carry, 0.1) : arcPoint(prev, src, pick, -0.1);
      }
    }
    return home;
  })();

  return (
    <AbsoluteFill style={{ backgroundColor: FILM.ink }}>
      {/* PEOPLE */}
      <div style={{ position: "absolute", left: 0, top: 0, width: 960, height: 1080, backgroundColor: FILM.canvas, overflow: "hidden", opacity: peopleDim }}>
        <div style={{ position: "absolute", left: 80, top: 80 }}>
          <FilmLabel size={20} tracking={0.3} color={FILM.ink}>
            {copy("people")}
          </FilmLabel>
        </div>
        {SOURCES.map((s, i) => (
          <div key={s.id} style={{ position: "absolute", left: s.x - 60, top: 200, width: 190, opacity: r(T, BEAT.peopleStart - 0.1 + i * 0.1, BEAT.peopleStart + 0.25 + i * 0.1) }}>
            <BrandTile id={s.id} size={56} />
            <div style={{ marginTop: 14, fontFamily: FONT.display, fontSize: 16, lineHeight: 1.35, color: FILM.ink, backgroundColor: "#fff", borderRadius: 8, padding: "8px 10px", boxShadow: "0 8px 20px -12px rgba(20,19,15,0.3)" }}>{s.text}</div>
          </div>
        ))}
        <div style={{ position: "absolute", left: NOTE.x, top: NOTE.y, width: NOTE.w, height: NOTE.h, borderRadius: 16, backgroundColor: "#fff", boxShadow: "0 30px 70px -30px rgba(20,19,15,0.35)", padding: "22px 26px" }}>
          <FilmLabel size={13} color={FILM.textSubtle}>
            {HAND_NOTE_TITLE}
          </FilmLabel>
        </div>
        {COPIES.map((c, k) => {
          if (T < c.at) return null;
          const carry = r(T, c.at, c.at + 0.45, easeInOut);
          const p = arcPoint({ x: SOURCES[c.from].x - 50, y: 300 }, { x: NOTE.x + 26, y: lineY(k) - 14 }, carry, 0.1);
          return (
            <div key={k} style={{ position: "absolute", left: p.x, top: p.y, fontFamily: FONT.display, fontSize: 19, color: FILM.ink, backgroundColor: carry < 1 ? "rgba(59,130,246,0.18)" : "transparent", borderRadius: 6, padding: "3px 6px", whiteSpace: "nowrap" }}>
              {SOURCES[c.from].text}
            </div>
          );
        })}
        {T < BEAT.agentsStart + 0.3 ? <UiCursor x={cursor.x} y={cursor.y} scale={1.05} opacity={1 - r(T, BEAT.agentsStart - 0.15, BEAT.agentsStart + 0.25)} clickFrames={COPIES.map((c) => sec(c.at))} frameOverride={sec(T)} /> : null}
      </div>
      <div style={{ position: "absolute", left: 959, top: 0, width: 2, height: 1080, backgroundColor: "rgba(237,235,230,0.08)" }} />
      {/* AGENTS */}
      <div style={{ position: "absolute", left: 960, top: 0, width: 960, height: 1080, opacity: 0.35 + 0.65 * agents }}>
        <div style={{ position: "absolute", left: 80, top: 80 }}>
          <FilmLabel size={20} tracking={0.3} color={FILM.onInk}>
            {copy("agents")}
          </FilmLabel>
        </div>
        <div style={{ position: "absolute", left: 80, top: 300, width: 800, borderRadius: 16, backgroundColor: FILM.inkRaised, border: "1px solid rgba(237,235,230,0.1)", padding: "30px 34px", fontFamily: FONT.mono, fontSize: 22, lineHeight: 1.8, color: FILM.onInk, opacity: agents, translate: `0 ${(1 - agents) * 20}px` }}>
          <div style={{ color: FILM.onInkDim, fontSize: 14, letterSpacing: "0.2em" }}>NEW AGENT SESSION</div>
          {["renewal date", "decisions", "commitments", "owner"].map((k) => (
            <div key={k} style={{ color: FILM.onInkMuted }}>
              {k}: <span style={{ color: FILM.onInkDim }}>—</span>
            </div>
          ))}
          <div style={{ marginTop: 12 }}>
            &gt; <span style={{ display: "inline-block", width: 12, height: 26, translate: "0 5px", backgroundColor: caretOn(t, false) ? FILM.onInk : "transparent" }} />
          </div>
        </div>
      </div>
      <Grain opacity={0.02} />
      <AbsoluteFill style={{ backgroundColor: FILM.ink, opacity: black }} />
    </AbsoluteFill>
  );
};
