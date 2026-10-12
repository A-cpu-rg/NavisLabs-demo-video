import { interpolate } from "remotion";
import { BEAT, SIGNAL_FLIGHT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { FILM, FONT, FUTURE_CONNECTED, LIVE_CURRENT, type AnyIntegrationId } from "../config/navisBrand";
import { BrandIcon, BrandTile } from "../ui/Integrations";
import { FLOW_SIGNALS } from "../ui/demoContent";
import { CLAMP, easeInOut, easeOut } from "../ui/kit";
import { arcPoint, FilmLabel, NavisMark } from "../scenes/shared";

// How NavisLabs works, as data flow (S04):
//   CONNECTED SYSTEMS → SIGNALS → NAVISLABS → UNDERSTANDING → INTELLIGENCE
// Thirteen systems: the six connected today (LIVE_CURRENT) and the seven on
// the roadmap (FUTURE_CONNECTED), drawn alike because this scene shows the
// intended complete product — hence the "Product vision · connected systems
// shown" note. Nine kinds of signal leave their systems at different times,
// NavisLabs resolves them into the organization's entities, and out come the
// questions the Navis App answers. An information system, not a brain:
// no particles, no glow. Screen space, light canvas.

const SYSTEMS: readonly AnyIntegrationId[] = [...LIVE_CURRENT.map((m) => m.id), ...FUTURE_CONNECTED.map((m) => m.id)];
const tilePos = (i: number) => (i < 7 ? { x: 168, y: 250 + i * 96 } : { x: 268, y: 298 + (i - 7) * 96 });
const HUB = { x: 880, y: 540 };
const ENTITY_X = 1205;
const ENTITIES = ["People", "Customers", "Projects", "Decisions", "Commitments", "Meetings"] as const;
const entityY = (i: number) => HUB.y + (i - 2.5) * 80;
const INTEL_X = 1500;
const INTEL = ["What changed", "What matters", "What's at risk", "What's waiting", "What needs a decision"] as const;
const intelY = (i: number) => HUB.y + (i - 2) * 86;

const r = (T: number, a: number, b: number, e: (x: number) => number = easeOut) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

const Stage: React.FC<{ readonly x: number; readonly label: string; readonly reveal: number }> = ({ x, label, reveal }) => (
  <div style={{ position: "absolute", left: x, top: 150, translate: "-50% 0", opacity: reveal }}>
    <FilmLabel size={14} tracking={0.28} color={FILM.textSubtle}>
      {label}
    </FilmLabel>
  </div>
);

export const SignalFlow: React.FC<{ readonly T: number }> = ({ T }) => {
  const sys = r(T, BEAT.iconsIn - 0.1, BEAT.iconsIn + 0.3);
  const hub = r(T, BEAT.iconsIn + 0.1, BEAT.iconsIn + 0.45);
  const stageSig = r(T, BEAT.signalsOut, BEAT.signalsOut + 0.3);
  const stageUnd = r(T, BEAT.understanding, BEAT.understanding + 0.3);
  const stageInt = r(T, BEAT.intelIn - 0.1, BEAT.intelIn + 0.2);
  // The hub reacts to each arrival with a small, quick ring.
  const arrivals = FLOW_SIGNALS.map((_, i) => BEAT.signalsOut + i * 0.21 + SIGNAL_FLIGHT);
  const ring = Math.max(0, ...arrivals.map((a) => r(T, a - 0.02, a + 0.06) * (1 - r(T, a + 0.06, a + 0.4))));

  return (
    <>
      <Stage x={218} label="Connected systems" reveal={sys} />
      <Stage x={560} label={copy("signals")} reveal={stageSig} />
      <Stage x={HUB.x} label="NavisLabs" reveal={hub} />
      <Stage x={ENTITY_X} label={copy("understandingStage")} reveal={stageUnd} />
      <Stage x={INTEL_X + 110} label={copy("intelligence")} reveal={stageInt} />

      {/* Thin connectors: systems → hub (faint), hub → entities, entities → intelligence. */}
      <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
        {SYSTEMS.map((id, i) => {
          const p = tilePos(i);
          const a = r(T, BEAT.iconsIn + 0.15 + i * 0.03, BEAT.iconsIn + 0.6 + i * 0.03);
          return <line key={id} x1={p.x + 34} y1={p.y} x2={p.x + 34 + (HUB.x - 90 - p.x - 34) * a} y2={p.y + (HUB.y - p.y) * a} stroke="rgba(28,25,20,0.08)" strokeWidth={1} />;
        })}
        {ENTITIES.map((e, i) => {
          const a = r(T, BEAT.entitiesIn + i * 0.08, BEAT.entitiesIn + 0.3 + i * 0.08, easeInOut);
          return <line key={e} x1={HUB.x + 92} y1={HUB.y} x2={HUB.x + 92 + (ENTITY_X - 78 - HUB.x - 92) * a} y2={HUB.y + (entityY(i) - HUB.y) * a} stroke="rgba(25,118,254,0.45)" strokeWidth={1.2} />;
        })}
        {INTEL.map((q, i) => {
          const a = r(T, BEAT.intelIn + i * 0.1, BEAT.intelIn + 0.3 + i * 0.1, easeInOut);
          return <line key={q} x1={ENTITY_X + 92} y1={HUB.y} x2={ENTITY_X + 92 + (INTEL_X - 26 - ENTITY_X - 92) * a} y2={HUB.y + (intelY(i) - HUB.y) * a} stroke="rgba(28,25,20,0.16)" strokeWidth={1} />;
        })}
      </svg>

      {SYSTEMS.map((id, i) => {
        const p = tilePos(i);
        const a = r(T, BEAT.iconsIn + i * 0.035, BEAT.iconsIn + 0.3 + i * 0.035);
        return (
          <div key={id} style={{ position: "absolute", left: p.x, top: p.y, translate: "-50% -50%", opacity: a, scale: String(0.9 + 0.1 * a) }}>
            <BrandTile id={id} size={64} />
          </div>
        );
      })}

      {FLOW_SIGNALS.map((s, i) => {
        const start = BEAT.signalsOut + i * 0.21;
        const p = r(T, start, start + SIGNAL_FLIGHT, easeInOut);
        if (p <= 0 || p >= 1) return null;
        const from = tilePos(SYSTEMS.indexOf(s.from));
        const pos = arcPoint({ x: from.x + 60, y: from.y }, { x: HUB.x - 70, y: HUB.y }, p, (i - 4) * -0.03);
        const fade = Math.min(1, p * 6) * (1 - Math.max(0, (p - 0.82) / 0.18));
        return (
          <div
            key={s.label}
            style={{
              position: "absolute",
              left: pos.x,
              top: pos.y,
              translate: "-50% -50%",
              opacity: fade,
              scale: String(1 - 0.18 * p),
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "7px 12px 7px 9px",
              borderRadius: 9,
              backgroundColor: "#FFFFFF",
              border: "1px solid rgba(28,25,20,0.1)",
              boxShadow: "0 6px 16px -8px rgba(20,19,15,0.3)",
              fontFamily: FONT.mono,
              fontSize: 13.5,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: FILM.ink,
              whiteSpace: "nowrap",
            }}
          >
            <BrandIcon id={s.from} height={13} />
            {s.label}
          </div>
        );
      })}

      {/* NavisLabs: the mark and the wordmark, no container. */}
      <div style={{ position: "absolute", left: HUB.x, top: HUB.y, translate: "-50% -50%", opacity: hub, display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
        <div style={{ position: "relative" }}>
          <div style={{ position: "absolute", left: "50%", top: "50%", width: 128, height: 128, translate: "-50% -50%", borderRadius: 64, border: `1px solid rgba(25,118,254,${0.35 * ring})`, scale: String(0.9 + 0.2 * ring) }} />
          <NavisMark size={92} tone="light" />
        </div>
        <div style={{ fontFamily: FONT.display, fontSize: 26, fontWeight: 600, letterSpacing: "0.01em", color: FILM.ink }}>NavisLabs</div>
        <div style={{ opacity: stageUnd }}>
          <FilmLabel size={12} tracking={0.22} color={FILM.textSubtle}>
            {copy("layer")}
          </FilmLabel>
        </div>
      </div>

      {ENTITIES.map((e, i) => {
        const a = r(T, BEAT.entitiesIn + 0.15 + i * 0.08, BEAT.entitiesIn + 0.45 + i * 0.08);
        return (
          <div
            key={e}
            style={{
              position: "absolute",
              left: ENTITY_X,
              top: entityY(i),
              translate: `-50% -50%`,
              opacity: a,
              scale: String(0.94 + 0.06 * a),
              width: 176,
              textAlign: "center",
              padding: "9px 0",
              borderRadius: 999,
              border: "1px solid rgba(28,25,20,0.14)",
              backgroundColor: "#FFFFFF",
              fontFamily: FONT.display,
              fontSize: 19,
              fontWeight: 500,
              color: FILM.ink,
            }}
          >
            {e}
          </div>
        );
      })}

      {INTEL.map((q, i) => {
        const a = r(T, BEAT.intelIn + 0.12 + i * 0.1, BEAT.intelIn + 0.42 + i * 0.1);
        return (
          <div key={q} style={{ position: "absolute", left: INTEL_X, top: intelY(i), translate: `${(1 - a) * 12}px -50%`, opacity: a, display: "flex", alignItems: "center", gap: 14 }}>
            <span style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: i === 2 ? "#EF4444" : i === 3 ? "#F59E0B" : FILM.ink }} />
            <span style={{ fontFamily: FONT.display, fontSize: 24, fontWeight: 600, letterSpacing: "-0.01em", color: FILM.ink, whiteSpace: "nowrap" }}>{q}</span>
          </div>
        );
      })}

      <div style={{ position: "absolute", left: 64, bottom: 40, opacity: 0.85 * sys, fontFamily: FONT.display, fontSize: 13, color: FILM.textSubtle }}>{copy("visionNote")}</div>
    </>
  );
};
