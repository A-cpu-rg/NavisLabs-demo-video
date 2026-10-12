import { interpolate } from "remotion";
import { BEAT } from "../config/beats";
import { FILM, FONT } from "../config/navisBrand";
import { BrandTile } from "../ui/Integrations";
import { copy } from "../config/filmSpec";
import { CUSTOMER_STATE, APP_WORKSPACE, CUSTOMER, isUpcoming, SYSTEM_FACTS } from "../ui/demoContent";
import { CLAMP, easeInOut, easeOut } from "../ui/kit";
import { FilmLabel } from "../scenes/shared";

// S07, after the "Why Navis surfaced this" drawer: the evidence opened out.
// Each connected system that holds a demo record contributes a different fact
// about the customer (SYSTEM_FACTS, demo data), read as a chain: the customer's
// email → the CRM opportunity → the meeting → the decision → documents,
// commitment, engineering. Navis resolves them into one customer state — and
// the CRM disagrees with the email: the opportunity still closes on the old
// date. The CRM alone does not hold the whole truth. Screen space.

const r = (T: number, a: number, b: number, e: (x: number) => number = easeOut) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

const CARD = { x: 960, y: 566, w: 540 };
const HALF = Math.ceil(SYSTEM_FACTS.length / 2);
const LEFT = SYSTEM_FACTS.slice(0, HALF);
const RIGHT = SYSTEM_FACTS.slice(HALF);
// Rows spaced to the card's height, centred on it.
const ROW_GAP = 112;
const rowY = (i: number, n: number) => CARD.y + (i - (n - 1) / 2) * ROW_GAP;
const leftY = (i: number) => rowY(i, LEFT.length);
const rightY = (i: number) => rowY(i, RIGHT.length);
const CHIP_W = 410;

const AMBER = "#B45309";

const Chip: React.FC<{ readonly f: (typeof SYSTEM_FACTS)[number]; readonly reveal: number; readonly side: -1 | 1; readonly conflict?: number }> = ({ f, reveal, side, conflict = 0 }) => (
  <div
    style={{
      width: CHIP_W,
      opacity: reveal,
      translate: `${(1 - reveal) * 18 * side}px 0`,
      outline: conflict > 0 ? `${1.5 * conflict}px solid rgba(217,119,6,${0.85 * conflict})` : undefined,
      display: "flex",
      alignItems: "center",
      gap: 14,
      padding: "11px 14px",
      borderRadius: 12,
      backgroundColor: "#FFFFFF",
      boxShadow: "0 1px 2px rgba(15,23,42,0.05), inset 0 0 0 1px rgba(0,0,0,0.06)",
      boxSizing: "border-box",
    }}
  >
    <BrandTile id={f.id} size={38} />
    <div style={{ minWidth: 0, flex: 1 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontFamily: FONT.mono, fontSize: 11, letterSpacing: "0.14em", textTransform: "uppercase", color: FILM.textSubtle }}>
        <span>{f.role}</span>
        {f.conflict && conflict > 0 ? (
          <span style={{ letterSpacing: "0.06em", color: AMBER, opacity: conflict }}>{f.conflict}</span>
        ) : (
          <span style={{ letterSpacing: "0.04em" }}>{f.when}</span>
        )}
      </div>
      <div style={{ marginTop: 4, fontFamily: FONT.app, fontSize: 15.5, fontWeight: 500, color: "#111827", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{f.fact}</div>
    </div>
  </div>
);

export const EvidenceExploded: React.FC<{ readonly T: number }> = ({ T }) => {
  const t0 = BEAT.explodeIn;
  const chip = (i: number) => r(T, t0 + i * 0.04, t0 + 0.3 + i * 0.04);
  const lines = r(T, t0 + 0.25, t0 + 0.75, easeInOut);
  const card = r(T, t0 + 0.4, t0 + 0.7);
  const rows = CUSTOMER_STATE.map((_, i) => r(T, BEAT.resolveIn + i * 0.1, BEAT.resolveIn + 0.25 + i * 0.1));
  // The conflict lands as the Opportunity row resolves: the CRM still has the old date.
  const oppRow = CUSTOMER_STATE.findIndex((s) => s.was);
  const conflict = r(T, BEAT.resolveIn + oppRow * 0.1 + 0.15, BEAT.resolveIn + oppRow * 0.1 + 0.45);
  const crmIdx = LEFT.findIndex((f) => f.conflict);
  const mailIdx = LEFT.findIndex((f) => f.id === "gmail");
  const leftEdge = CARD.x - CARD.w / 2;
  const rightEdge = CARD.x + CARD.w / 2;
  return (
    <>
      <div style={{ position: "absolute", left: 0, right: 0, top: 104, display: "flex", justifyContent: "center", opacity: chip(0) }}>
        <FilmLabel size={14} tracking={0.28} color={FILM.textSubtle}>
          Evidence · {SYSTEM_FACTS.filter((f) => !isUpcoming(f.id)).length} live + {SYSTEM_FACTS.filter((f) => isUpcoming(f.id)).length} upcoming systems · one customer state
        </FilmLabel>
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0 }}>
        {LEFT.map((f, i) => {
          const x1 = 90 + CHIP_W;
          const y1 = leftY(i);
          const y2 = CARD.y - 75 + i * 50;
          return <line key={f.id} x1={x1} y1={y1} x2={x1 + (leftEdge - x1) * lines} y2={y1 + (y2 - y1) * lines} stroke="rgba(25,118,254,0.4)" strokeWidth={1.1} />;
        })}
        {RIGHT.map((f, i) => {
          const x1 = 1830 - CHIP_W;
          const y1 = rightY(i);
          const y2 = CARD.y - 75 + i * 50;
          return <line key={f.id} x1={x1} y1={y1} x2={x1 + (rightEdge - x1) * lines} y2={y1 + (y2 - y1) * lines} stroke="rgba(25,118,254,0.4)" strokeWidth={1.1} />;
        })}
      </svg>
      {crmIdx >= 0 && mailIdx >= 0 ? (
        <svg width={1920} height={1080} style={{ position: "absolute", left: 0, top: 0, opacity: conflict }}>
          <path d={`M 84 ${leftY(mailIdx)} C 58 ${leftY(mailIdx)}, 58 ${leftY(crmIdx)}, 84 ${leftY(crmIdx)}`} fill="none" stroke={AMBER} strokeWidth={1.6} strokeDasharray="4 4" />
        </svg>
      ) : null}
      {LEFT.map((f, i) => (
        <div key={f.id} style={{ position: "absolute", left: 90, top: leftY(i), translate: "0 -50%" }}>
          <Chip f={f} reveal={chip(i)} side={-1} conflict={f.conflict ? conflict : 0} />
        </div>
      ))}
      {RIGHT.map((f, i) => (
        <div key={f.id} style={{ position: "absolute", left: 1830 - CHIP_W, top: rightY(i), translate: "0 -50%" }}>
          <Chip f={f} reveal={chip(HALF + i)} side={1} />
        </div>
      ))}
      <div
        style={{
          position: "absolute",
          left: leftEdge,
          top: CARD.y,
          width: CARD.w,
          translate: "0 -50%",
          opacity: card,
          scale: String(0.97 + 0.03 * card),
          borderRadius: 18,
          backgroundColor: "#FFFFFF",
          boxShadow: "0 30px 70px -30px rgba(20,19,15,0.35), inset 0 0 0 1px rgba(0,0,0,0.07)",
          padding: "22px 26px",
          boxSizing: "border-box",
        }}
      >
        <div style={{ fontFamily: FONT.display, fontSize: 26, fontWeight: 600, letterSpacing: "0.02em", color: FILM.ink, whiteSpace: "nowrap" }}>{CUSTOMER.caps}</div>
        <div style={{ marginTop: 4, fontFamily: FONT.mono, fontSize: 12, color: FILM.textSubtle }}>
          {copy("fictionalOrg")} · customer state · as of {APP_WORKSPACE.now}
        </div>
        <div style={{ marginTop: 14, display: "flex", flexDirection: "column" }}>
          {CUSTOMER_STATE.map((s, i) => (
            <div
              key={s.entity}
              style={{
                opacity: 0.25 + 0.75 * rows[i],
                display: "grid",
                gridTemplateColumns: "130px 1fr",
                alignItems: "baseline",
                padding: "9px 10px",
                margin: "0 -10px",
                borderRadius: 8,
                backgroundColor: s.was ? `rgba(217,119,6,${0.1 * conflict})` : undefined,
                borderTop: i ? "1px solid rgba(0,0,0,0.06)" : "none",
              }}
            >
              <span style={{ fontFamily: FONT.mono, fontSize: 11.5, letterSpacing: "0.16em", textTransform: "uppercase", color: s.was && conflict > 0.5 ? AMBER : rows[i] > 0.5 ? FILM.cobalt : FILM.textSubtle }}>{s.entity}</span>
              {s.was && s.now ? (
                <span style={{ fontFamily: FONT.app, fontSize: 17, fontWeight: 500, color: "#111827" }}>
                  Closes{" "}
                  <span style={{ textDecoration: conflict > 0.5 ? "line-through" : "none", textDecorationColor: AMBER, color: conflict > 0.5 ? FILM.textSubtle : "#111827" }}>{s.was}</span>
                  <span style={{ color: AMBER, opacity: conflict }}> → {s.now}</span>
                  <span style={{ marginLeft: 10, fontFamily: FONT.mono, fontSize: 11, letterSpacing: "0.12em", color: AMBER, opacity: conflict }}>CRM NOT UPDATED</span>
                </span>
              ) : (
                <span style={{ fontFamily: FONT.app, fontSize: 17, fontWeight: 500, color: "#111827" }}>{s.value}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
};
