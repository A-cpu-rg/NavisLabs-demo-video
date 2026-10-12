import { AbsoluteFill, interpolate } from "remotion";
import { BEAT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { DEV, FILM, FONT, type AnyIntegrationId } from "../config/navisBrand";
import type { CameraKeyframe } from "../config/types";
import { Camera } from "../components/Camera";
import { Grain } from "../components/World";
import { LIVE_IDS, OPENING_SIGNALS, TWO_TRUTHS } from "../ui/demoContent";
import { BrandIcon, BrandTile, integration } from "../ui/Integrations";
import { CLAMP, easeInOut } from "../ui/kit";
import { FilmLabel } from "./shared";

// S01 · 0–6.2 s · one continuous take.
//   V01 "Your people and agents see different truths."
//   V02 "The truth is scattered across the systems where work happens."
// 1) PEOPLE | AI AGENTS: the same customer seen two ways. The person's inbox
//    has the renewal on its new date; the agent's workflow file still has the
//    old one (the file the agent updates in S15).
// 2) The two views break apart: the truth sits across the company's connected
//    systems (V6 launch state: thirteen), a piece in each that holds one. All
//    values are demo data (src/ui/demoContent.ts).

const r = (T: number, a: number, b: number, e?: (x: number) => number) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

const COL = 470;

/** #RRGGBB → rgba() at an alpha. */
const tintA = (hex: string, alpha: number) => `rgba(${parseInt(hex.slice(1, 3), 16)},${parseInt(hex.slice(3, 5), 16)},${parseInt(hex.slice(5, 7), 16)},${alpha})`;
const CARD_W = 600;

/** Where each system sits once the truth is scattered: a loose 4 · 5 · 4 field. */
const ROWS: readonly (readonly AnyIntegrationId[])[] = [
  ["gmail", "salesforce", "calendar", "notion"],
  ["meet", "hubspot", "microsoft365", "jira", "drive"],
  ["docs", "zoom", "slack", "github"],
];
const ROW_Y = [-430, -50, 330];
const ROW_X = [[-780, -260, 260, 780], [-920, -460, 0, 460, 920], [-780, -260, 260, 780]];
// A little irregularity so it reads as scattered, not as a grid.
const JITTER: readonly (readonly [number, number])[] = [[-20, 10], [30, -14], [-12, 18], [24, 6], [16, -10], [-24, 12], [8, -18], [-30, 8], [12, 14], [-16, -6], [28, 10], [-10, -16], [20, 4]];
const SYSTEM_POS = Object.fromEntries(
  ROWS.flatMap((row, r_) => row.map((id, c) => [id, { x: ROW_X[r_][c], y: ROW_Y[r_] }] as const)).map(([id, p], k) => [id, { x: p.x + JITTER[k][0], y: p.y + JITTER[k][1] }]),
) as Record<AnyIntegrationId, { x: number; y: number }>;

const Value: React.FC<{ readonly label: string; readonly value: string; readonly tint: string; readonly on: number; readonly dark?: boolean }> = ({ label, value, tint, on, dark }) => (
  <div style={{ marginTop: 18, paddingTop: 16, borderTop: `1px solid ${dark ? "rgba(237,235,230,0.1)" : "rgba(20,19,15,0.08)"}`, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
    <span style={{ fontFamily: FONT.mono, fontSize: 13, letterSpacing: "0.14em", textTransform: "uppercase", color: dark ? FILM.onInkDim : FILM.textSubtle }}>{label}</span>
    <span
      style={{
        fontFamily: FONT.display,
        fontSize: 30,
        fontWeight: 600,
        letterSpacing: "-0.01em",
        color: dark ? FILM.onInk : FILM.ink,
        padding: "4px 12px",
        borderRadius: 8,
        backgroundColor: tintA(tint, 0.22 * on),
        boxShadow: `inset 0 0 0 1px ${tintA(tint, 0.7 * on)}`,
      }}
    >
      {value}
    </span>
  </div>
);

const PeopleCard: React.FC<{ readonly diff: number }> = ({ diff }) => {
  const p = TWO_TRUTHS.people;
  return (
    <div style={{ width: CARD_W, padding: "24px 28px", borderRadius: 16, backgroundColor: "#FFFFFF", boxShadow: "0 30px 70px -30px rgba(0,0,0,0.75)", boxSizing: "border-box" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <BrandIcon id={p.source} height={16} />
        <span style={{ fontFamily: FONT.mono, fontSize: 13, color: FILM.textSubtle }}>Gmail</span>
        <span style={{ marginLeft: "auto", fontFamily: FONT.mono, fontSize: 13, color: FILM.textSubtle }}>{p.from}</span>
      </div>
      <div style={{ marginTop: 16, fontFamily: FONT.display, fontSize: 24, fontWeight: 600, color: FILM.ink }}>{p.subject}</div>
      <div style={{ marginTop: 8, fontFamily: FONT.display, fontSize: 19, lineHeight: 1.4, color: FILM.textMuted }}>{p.text}</div>
      <Value label={p.label} value={p.value} tint={FILM.cobalt} on={diff} />
    </div>
  );
};

const AgentCard: React.FC<{ readonly diff: number }> = ({ diff }) => {
  const a = TWO_TRUTHS.agents;
  const [key, ...rest] = a.code.split(": ");
  return (
    <div style={{ width: CARD_W, padding: "24px 28px", borderRadius: 16, backgroundColor: FILM.inkRaised, border: "1px solid rgba(237,235,230,0.12)", boxShadow: "0 30px 70px -30px rgba(0,0,0,0.8)", boxSizing: "border-box", fontFamily: FONT.mono }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ fontSize: 13, letterSpacing: "0.16em", textTransform: "uppercase", color: FILM.onInkDim }}>{a.session}</span>
        <span style={{ marginLeft: "auto", fontSize: 13, color: FILM.onInkDim }}>{a.file}</span>
      </div>
      <div style={{ marginTop: 18, fontSize: 17, color: DEV.termMuted }}>Read({a.file})</div>
      <div style={{ marginTop: 10, fontSize: 21, color: DEV.termText }}>
        {key}: <span style={{ color: DEV.termAmber }}>{rest.join(": ")}</span>
      </div>
      <Value label={a.label} value={a.value} tint={DEV.termAmber} on={diff} dark />
    </div>
  );
};

const Fragment: React.FC<{ readonly i: number; readonly T: number; readonly push: number }> = ({ i, T, push }) => {
  const s = OPENING_SIGNALS[i];
  const at = BEAT[s.at];
  const a = r(T, at - 0.1, at + 0.3, easeInOut);
  if (a <= 0) return null;
  const tile = SYSTEM_POS[s.source];
  const x = tile.x * push;
  const y = tile.y * push + 128;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        translate: `-50% calc(0% + ${(1 - a) * 10}px)`,
        width: 250,
        opacity: a,
        padding: "14px 16px",
        borderRadius: 12,
        backgroundColor: FILM.inkRaised,
        border: "1px solid rgba(237,235,230,0.12)",
        boxShadow: "0 24px 50px -24px rgba(0,0,0,0.8)",
      }}
    >
      <FilmLabel size={11} tracking={0.22} color={FILM.onInkMuted}>
        {s.kind}
      </FilmLabel>
      <div style={{ marginTop: 6, fontFamily: FONT.display, fontSize: 17, lineHeight: 1.3, fontWeight: 500, color: FILM.onInk }}>{s.text}</div>
      <div style={{ marginTop: 8, fontFamily: FONT.mono, fontSize: 11, color: FILM.onInkDim }}>{s.when}</div>
    </div>
  );
};

export const MemoryFlow: React.FC<{ readonly T: number; readonly keyframes: readonly CameraKeyframe[] }> = ({ T, keyframes }) => {
  const fade = r(T, 0, 0.6);
  const labels = r(T, BEAT.truthLabels, BEAT.truthLabels + 0.4, easeInOut);
  const people = r(T, BEAT.truthPeople - 0.1, BEAT.truthPeople + 0.35, easeInOut);
  const agent = r(T, BEAT.truthAgent - 0.1, BEAT.truthAgent + 0.35, easeInOut);
  const diff = r(T, BEAT.truthDiff, BEAT.truthDiff + 0.3, easeInOut);
  // V02: the two views break apart.
  const out = r(T, BEAT.scatter - 0.1, BEAT.scatter + 0.35, easeInOut);
  const tilesIn = (i: number) => r(T, BEAT.scatter + 0.15 + i * 0.05, BEAT.scatter + 0.55 + i * 0.05, easeInOut);
  const push = 1 + 0.08 * r(T, BEAT.problem, BEAT.problem + 1.6, easeInOut);

  return (
    <AbsoluteFill style={{ backgroundColor: FILM.ink, opacity: fade }}>
      <Camera keyframes={keyframes}>
        {out < 1 ? (
          <div style={{ opacity: 1 - out }}>
            {/* PEOPLE | AI AGENTS */}
            <div style={{ position: "absolute", left: -0.5, top: -330, width: 1, height: 660 * labels, backgroundColor: "rgba(237,235,230,0.12)" }} />
            <div style={{ position: "absolute", left: -COL, top: -300, translate: "-50% -50%", opacity: labels }}>
              <FilmLabel size={18} tracking={0.3} color={FILM.onInk}>
                {copy("people")}
              </FilmLabel>
            </div>
            <div style={{ position: "absolute", left: COL, top: -300, translate: "-50% -50%", opacity: labels }}>
              <FilmLabel size={18} tracking={0.3} color={FILM.onInk}>
                {copy("agents")}
              </FilmLabel>
            </div>
            <div style={{ position: "absolute", left: -COL - 60 * out, top: 20, translate: `-50% calc(-50% + ${(1 - people) * 14}px)`, opacity: people, scale: String(1 - 0.04 * out) }}>
              <PeopleCard diff={diff} />
            </div>
            <div style={{ position: "absolute", left: COL + 60 * out, top: 20, translate: `-50% calc(-50% + ${(1 - agent) * 14}px)`, opacity: agent, scale: String(1 - 0.04 * out) }}>
              <AgentCard diff={diff} />
            </div>
          </div>
        ) : null}
        {/* The systems the truth lives in, a piece in each. */}
        {LIVE_IDS.map((id, i) => {
          const a = tilesIn(i);
          if (a <= 0) return null;
          const p = SYSTEM_POS[id];
          return (
            <div key={id} style={{ position: "absolute", left: p.x * push, top: p.y * push, translate: "-50% -50%", opacity: a, scale: String(0.85 + 0.15 * a), display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
              <BrandTile id={id} size={72} />
              <FilmLabel size={13} tracking={0.16} color={FILM.onInkMuted}>
                {integration(id).label}
              </FilmLabel>
            </div>
          );
        })}
        {OPENING_SIGNALS.map((_, i) => (
          <Fragment key={i} i={i} T={T} push={push} />
        ))}
      </Camera>
      <Grain opacity={0.025} />
    </AbsoluteFill>
  );
};
