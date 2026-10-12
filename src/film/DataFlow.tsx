import { interpolate } from "remotion";
import { BEAT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { FILM, FONT } from "../config/navisBrand";
import { BrandIcon, BrandTile, integration } from "../ui/Integrations";
import {
  ACCOUNT_PLAN,
  COMMITMENT,
  CONTACT,
  CUSTOMER,
  DECISION,
  EMAIL,
  FLOW_SIGNALS,
  INTEGRATION_SEMANTICS,
  isUpcoming,
  LIVE_IDS,
  MOVED_ON,
  ORDER_FORM,
  RENEWAL_CALL_WHEN,
  USER,
} from "../ui/demoContent";
import { CLAMP, easeInOut, easeOut } from "../ui/kit";
import { FilmLabel, NavisMark } from "../scenes/shared";

// S04 — how NavisLabs works, as infrastructure (world space, light canvas):
//   live systems → SIGNALS → MEMORY → CONTEXT → INTELLIGENCE → DECISION →
//   EXECUTION → OUTCOME (building) → LEARNING (next)
// Deck p.5: "Signals → Memory → What's true now → What matters → Decide (a
// person approves) → Learn (BUILDING)". The outcome ledger is designed and
// learning is on the roadmap, so those two stages are drawn dashed and
// labelled. V6 launch state: all thirteen systems are connected (film-only
// configuration, src/data/navislabs_v8_launch_state.json); signals are drawn
// only from the systems the demo data holds a record for.

const r = (T: number, a: number, b: number, e: (x: number) => number = easeOut) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

const SYS_X = -470;
// The thirteen connected systems (launch state): two columns, seven rows.
const SYS_COL_X = [SYS_X - 330, SYS_X - 120];
// V8: live systems in the first column, upcoming systems (demo configuration) in the second.
const LIVE_COUNT = LIVE_IDS.filter((id) => !isUpcoming(id)).length;
const sysPos = (i: number) => ({ x: SYS_COL_X[i < LIVE_COUNT ? 0 : 1], y: -250 + (i < LIVE_COUNT ? i : i - LIVE_COUNT) * 66 });
const STAGE = { signals: -150, memory: 175, context: 480, intel: 790, decision: 1095, execution: 1385, outcome: 1655, learning: 1895 } as const;
const STAGE_Y = -330;
const chipY = (i: number) => -170 + i * 50;

const Stage: React.FC<{ readonly x: number; readonly label: string; readonly reveal: number; readonly status?: string }> = ({ x, label, reveal, status }) => (
  <div style={{ position: "absolute", left: x, top: STAGE_Y, translate: "-50% 0", opacity: reveal, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
    <FilmLabel size={13} tracking={0.26} color={reveal > 0.99 ? FILM.ink : FILM.textSubtle}>
      {label}
    </FilmLabel>
    {status ? <div style={{ fontFamily: FONT.mono, fontSize: 10.5, letterSpacing: "0.2em", textTransform: "uppercase", color: "#B7791F" }}>{status}</div> : null}
  </div>
);

const Card: React.FC<{ readonly x: number; readonly w: number; readonly reveal: number; readonly dashed?: boolean; readonly children: React.ReactNode }> = ({ x, w, reveal, dashed, children }) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: 0,
      width: w,
      translate: `-50% -50%`,
      opacity: reveal,
      scale: String(0.96 + 0.04 * reveal),
      borderRadius: 12,
      backgroundColor: dashed ? "rgba(255,255,255,0.4)" : "#FFFFFF",
      border: dashed ? "1.5px dashed rgba(28,25,20,0.25)" : "1px solid rgba(28,25,20,0.1)",
      boxShadow: dashed ? undefined : "0 16px 40px -20px rgba(20,19,15,0.3)",
      padding: "14px 16px",
      boxSizing: "border-box",
      fontFamily: FONT.app,
      color: "#111827",
    }}
  >
    {children}
  </div>
);

const Row: React.FC<{ readonly k: string; readonly v: string; readonly reveal?: number }> = ({ k, v, reveal = 1 }) => (
  <div style={{ display: "flex", gap: 8, alignItems: "baseline", fontSize: 13.5, lineHeight: 1.45, opacity: reveal }}>
    <span style={{ fontFamily: FONT.mono, fontSize: 11, color: FILM.textSubtle, whiteSpace: "nowrap", minWidth: 52 }}>{k}</span>
    <span>{v}</span>
  </div>
);

export const DataFlow: React.FC<{ readonly T: number }> = ({ T }) => {
  const live = LIVE_IDS.map((_, i) => r(T, BEAT.iconsIn + i * 0.05, BEAT.iconsIn + 0.3 + i * 0.05));
  const flight = (i: number) => r(T, BEAT.signalsOut + i * 0.22, BEAT.signalsOut + 0.7 + i * 0.22, easeInOut);
  const memory = r(T, BEAT.flowMemory, BEAT.flowMemory + 0.35);
  const memRows = [0, 1, 2, 3, 4, 5].map((i) => r(T, BEAT.flowMemory + 0.1 + i * 0.09, BEAT.flowMemory + 0.3 + i * 0.09));
  const context = r(T, BEAT.flowContext, BEAT.flowContext + 0.35);
  const intel = r(T, BEAT.flowIntel, BEAT.flowIntel + 0.35);
  const intelRows = [0, 1, 2, 3, 4].map((i) => r(T, BEAT.flowIntel + 0.1 + i * 0.1, BEAT.flowIntel + 0.3 + i * 0.1));
  const decision = r(T, BEAT.flowDecision, BEAT.flowDecision + 0.35);
  const execution = r(T, BEAT.flowExecution, BEAT.flowExecution + 0.35);
  const outcome = r(T, BEAT.flowOutcome, BEAT.flowOutcome + 0.35);
  const learning = r(T, BEAT.flowLearning, BEAT.flowLearning + 0.35);
  const loop = r(T, BEAT.flowOutcome + 0.2, BEAT.flowLearning + 0.5, easeInOut);
  const bracket = r(T, BEAT.signalsOut, BEAT.signalsOut + 0.5);
  // The spine between stages draws as each stage activates.
  const spineStops: readonly (readonly [number, number])[] = [
    [STAGE.signals, BEAT.signalsOut],
    [STAGE.memory, BEAT.flowMemory],
    [STAGE.context, BEAT.flowContext],
    [STAGE.intel, BEAT.flowIntel],
    [STAGE.decision, BEAT.flowDecision],
    [STAGE.execution, BEAT.flowExecution],
    [STAGE.outcome, BEAT.flowOutcome],
    [STAGE.learning, BEAT.flowLearning],
  ];
  const spineEnd: number = spineStops.reduce<number>((x, [sx, at]) => (T >= at ? sx : x), STAGE.signals);
  const C = CUSTOMER;

  return (
    <>
      {/* NavisLabs brackets the pipeline. */}
      <div style={{ position: "absolute", left: STAGE.signals - 110, top: STAGE_Y - 70, width: STAGE.learning - STAGE.signals + 220, height: 1, backgroundColor: "rgba(28,25,20,0.14)", opacity: bracket }} />
      <div style={{ position: "absolute", left: STAGE.signals - 110, top: STAGE_Y - 104, display: "flex", alignItems: "center", gap: 10, opacity: bracket }}>
        <NavisMark size={30} tone="light" />
        <span style={{ fontFamily: FONT.display, fontSize: 19, fontWeight: 600, color: FILM.ink }}>NavisLabs</span>
      </div>

      {/* The company's systems: live connectors, and upcoming ones shown as a labelled demo configuration. */}
      <div style={{ position: "absolute", left: SYS_COL_X[0], top: STAGE_Y, opacity: live[0] }}>
        <FilmLabel size={13} tracking={0.26} color={FILM.textSubtle}>
          {copy("liveLabel")}
        </FilmLabel>
      </div>
      <div style={{ position: "absolute", left: SYS_COL_X[1], top: STAGE_Y, opacity: live[LIVE_COUNT] ?? 0 }}>
        <FilmLabel size={13} tracking={0.26} color={FILM.textSubtle}>
          {copy("upcomingLabel")}
        </FilmLabel>
      </div>
      {LIVE_IDS.map((id, i) => (
        <div key={id} style={{ position: "absolute", left: sysPos(i).x, top: sysPos(i).y, translate: `${(1 - live[i]) * -14}px -50%`, opacity: live[i] * (isUpcoming(id) ? 0.78 : 1), display: "flex", alignItems: "center", gap: 10 }}>
          <BrandTile id={id} size={38} />
          <div>
            <div style={{ fontFamily: FONT.display, fontSize: 14.5, fontWeight: 500, color: FILM.ink, whiteSpace: "nowrap" }}>{integration(id).label}</div>
            <div style={{ fontFamily: FONT.mono, fontSize: 10.5, color: FILM.textSubtle, whiteSpace: "nowrap" }}>{INTEGRATION_SEMANTICS[id]}</div>
          </div>
        </div>
      ))}
      <svg width={2800} height={1400} viewBox="-900 -700 2800 1400" style={{ position: "absolute", left: -900, top: -700, overflow: "visible" }}>
        {/* spine */}
        <line x1={STAGE.signals} y1={0} x2={spineEnd} y2={0} stroke="rgba(25,118,254,0.55)" strokeWidth={1.4} />
        <line x1={spineEnd} y1={0} x2={STAGE.learning} y2={0} stroke="rgba(28,25,20,0.08)" strokeWidth={1.2} />
        {/* outcome returns to memory (building / next: dashed) */}
        <path d={`M ${STAGE.outcome} -70 C ${STAGE.outcome} -250, ${STAGE.memory} -250, ${STAGE.memory} -110`} fill="none" stroke="rgba(183,121,31,0.7)" strokeWidth={1.4} strokeDasharray="6 7" pathLength={1} style={{ strokeDashoffset: 0 }} opacity={loop} />
      </svg>

      {/* SIGNALS: one per live system, arriving at different times. */}
      {FLOW_SIGNALS.map((s, i) => {
        const p = flight(i);
        if (p <= 0) return null;
        const src = sysPos(Math.max(0, LIVE_IDS.indexOf(s.from)));
        const from = { x: src.x + 150, y: src.y };
        const to = { x: STAGE.signals - 95, y: chipY(i) };
        const x = from.x + (to.x - from.x) * p;
        const y = from.y + (to.y - from.y) * p;
        const settled = memory > 0 ? 1 - 0.5 * memory : 1;
        return (
          <div key={s.label} style={{ position: "absolute", left: x, top: y, translate: "0 -50%", opacity: Math.min(1, p * 4) * settled, display: "flex", alignItems: "center", gap: 7, padding: "6px 10px", borderRadius: 8, backgroundColor: "#FFFFFF", border: "1px solid rgba(28,25,20,0.1)", boxShadow: "0 4px 12px -6px rgba(20,19,15,0.3)", fontFamily: FONT.mono, fontSize: 12, letterSpacing: "0.04em", color: FILM.ink, whiteSpace: "nowrap" }}>
            <BrandIcon id={s.from} height={12} />
            {s.label}
          </div>
        );
      })}

      {/* MEMORY: the signals, organized and dated. */}
      <Card x={STAGE.memory} w={262} reveal={memory}>
        <div style={{ fontFamily: FONT.mono, fontSize: 10.5, letterSpacing: "0.16em", color: FILM.textSubtle, marginBottom: 6 }}>REMEMBERED</div>
        {/* Newest first; each row is dated when it happened (the call was moved on Oct 5 to an upcoming date). */}
        <Row k={EMAIL.date} v={`email · ${CONTACT.name}`} reveal={memRows[0]} />
        <Row k={MOVED_ON} v={`renewal call → ${RENEWAL_CALL_WHEN}`} reveal={memRows[1]} />
        <Row k={ORDER_FORM.date} v="order form" reveal={memRows[2]} />
        <Row k={ACCOUNT_PLAN.date} v="account owner" reveal={memRows[3]} />
        <Row k={DECISION.date} v="decision · annual terms" reveal={memRows[4]} />
        <Row k={COMMITMENT.date ?? ""} v={`commitment · ${COMMITMENT.due}`} reveal={memRows[5]} />
      </Card>

      {/* CONTEXT: resolved around one customer. */}
      <Card x={STAGE.context} w={268} reveal={context}>
        <div style={{ fontFamily: FONT.display, fontSize: 17, fontWeight: 600, letterSpacing: "0.02em" }}>{C.caps}</div>
        <div style={{ marginTop: 6 }}>
          <Row k="renewal" v={`${C.renewal_now} (was ${C.renewal_was})`} />
          <Row k="contact" v={CONTACT.name} />
          <Row k="owner" v={USER.name} />
          <Row k="terms" v="annual, current" />
          <Row k="owed" v={`revised terms · ${COMMITMENT.due}`} />
        </div>
      </Card>

      {/* INTELLIGENCE: what a person needs to know. */}
      <Card x={STAGE.intel} w={266} reveal={intel}>
        {[
          ["What changed", "renewal moved", FILM.ink],
          ["What matters", "terms unconfirmed", FILM.ink],
          ["At risk", "the renewal", "#EF4444"],
          ["Waiting", `${CONTACT.first}'s reply`, "#F59E0B"],
          ["Needs a decision", "confirm terms", FILM.ink],
        ].map(([k, v, c], i) => (
          <div key={k} style={{ display: "flex", alignItems: "baseline", gap: 8, fontSize: 13.5, lineHeight: 1.55, opacity: intelRows[i] }}>
            <span style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: c, translate: "0 -2px", flexShrink: 0 }} />
            <span style={{ fontWeight: 600 }}>{k}</span>
            <span style={{ color: FILM.textSubtle }}>{v}</span>
          </div>
        ))}
      </Card>

      {/* DECISION: narrowed to one, made by a person. */}
      <Card x={STAGE.decision} w={250} reveal={decision}>
        <div style={{ fontSize: 14.5, fontWeight: 600, lineHeight: 1.4 }}>
          Reply to {CONTACT.first}: confirm {C.renewal_now} on current terms
        </div>
        <div style={{ marginTop: 8, display: "inline-block", padding: "3px 9px", borderRadius: 999, border: "1px solid rgba(28,25,20,0.18)", fontFamily: FONT.mono, fontSize: 10.5, letterSpacing: "0.14em", textTransform: "uppercase", color: FILM.textSubtle }}>A person approves</div>
      </Card>

      {/* EXECUTION. */}
      <Card x={STAGE.execution} w={232} reveal={execution}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13.5 }}>
          <BrandIcon id="gmail" height={13} /> Reply sent · Gmail
        </div>
        <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 8, fontSize: 13.5 }}>
          <span style={{ fontFamily: FONT.mono, fontSize: 12, color: FILM.textSubtle }}>&gt;_</span> Workflow updated · agent
        </div>
      </Card>

      {/* OUTCOME (building) and LEARNING (next): dashed. */}
      <Card x={STAGE.outcome} w={196} reveal={outcome} dashed>
        <div style={{ fontSize: 14, fontWeight: 600, color: FILM.textMuted }}>Did it work?</div>
        <div style={{ marginTop: 4, fontSize: 12.5, color: FILM.textSubtle }}>Outcome recorded against the decision</div>
      </Card>
      <Card x={STAGE.learning} w={176} reveal={learning} dashed>
        <div style={{ fontSize: 14, fontWeight: 600, color: FILM.textMuted }}>What works</div>
        <div style={{ marginTop: 4, fontSize: 12.5, color: FILM.textSubtle }}>Learned across decisions</div>
      </Card>

      <Stage x={STAGE.signals} label="Signals" reveal={bracket} />
      <Stage x={STAGE.memory} label="Memory" reveal={memory} />
      <Stage x={STAGE.context} label="Context" reveal={context} />
      <Stage x={STAGE.intel} label="Intelligence" reveal={intel} />
      <Stage x={STAGE.decision} label="Decision" reveal={decision} />
      <Stage x={STAGE.execution} label="Execution" reveal={execution} />
      <Stage x={STAGE.outcome} label="Outcome" reveal={outcome} status="Building" />
      <Stage x={STAGE.learning} label="Learning" reveal={learning} status="Next" />
    </>
  );
};
