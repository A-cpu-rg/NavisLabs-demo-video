import { APP, DEMO, FILM, FONT } from "../../config/navisBrand";
import { CUSTOMER_SIGNALS, CONTACT, CUSTOMER, PRIORITIES, type Signal } from "../demoContent";
import { BrandIcon } from "../Integrations";
import { Icon } from "../kit";

// WhyThisDrawer -> Navis-AI/src/components/navis/WhyThisDrawer.tsx
// ("Why Navis surfaced this"): overlay bg-black/50, bottom sheet max-h-[88vh]
// rounded-t-2xl, content max-w-2xl px-6 py-7; kind label + 19px headline + X;
// Blocks (10px .2em gray-400 labels): "What's happening", "Who this is
// about", "Why it matters" (the 'situation' sentence and a COUNT of connected
// conclusions — confidence is never rendered as a percentage), "What supports
// this" (label/value rows, grid 140px 1fr, divide-y), "What you can do".
//
// TraceNote is NOT product UI: it is the film's annotation beside each
// evidence row (the system it came from, when, and how fresh the connector
// is), drawn as a dark card so it never reads as part of the app.

export const WHY_SHEET = 0.88;
const ROW_H = 54;

const Block: React.FC<{ readonly label: string; readonly reveal: number; readonly children: React.ReactNode }> = ({ label, reveal, children }) => (
  <section style={{ marginTop: 22, opacity: reveal, translate: `0 ${(1 - reveal) * 8}px` }}>
    <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.2em", textTransform: "uppercase", color: APP.gray400 }}>{label}</div>
    <div style={{ marginTop: 8 }}>{children}</div>
  </section>
);

export const TraceNote: React.FC<{ readonly signal: Signal; readonly reveal: number; readonly freshness: number }> = ({ signal, reveal, freshness }) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      top: 4,
      height: ROW_H - 8,
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: "0 16px 0 12px",
      borderRadius: 12,
      backgroundColor: FILM.ink,
      color: FILM.onInk,
      boxShadow: "0 14px 30px -14px rgba(20,19,15,0.55)",
      opacity: reveal,
      translate: `${(1 - reveal) * -14}px 0`,
      whiteSpace: "nowrap",
      fontFamily: FONT.mono,
    }}
  >
    <div style={{ width: 30, height: 30, borderRadius: 8, backgroundColor: "#fff", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <BrandIcon id={signal.source} height={signal.source === "slack" ? 13 : 16} />
    </div>
    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <div style={{ fontSize: 12, color: FILM.onInk }}>{signal.sourceLabel}</div>
      <div style={{ fontSize: 10.5, color: FILM.onInkMuted, letterSpacing: "0.04em" }}>
        {signal.when}
        <span style={{ opacity: freshness }}>
          {"  ·  "}
          <span style={{ color: "#7FB28E" }}>●</span> {signal.synced}
        </span>
      </div>
    </div>
  </div>
);

export const WhyThisDrawer: React.FC<{
  readonly open: number;
  readonly windowHeight: number;
  /** Reveal 0..1 per block: happening, who, matters, evidence rows[4], connected, canDo. */
  readonly blocks: { happening: number; who: number; matters: number; rows: readonly number[]; connected: number; canDo: number };
  readonly freshness: number;
  /** Highlight 0..1 per evidence row (the one being read). */
  readonly focus?: readonly number[];
  readonly showTrace?: number;
}> = ({ open, windowHeight, blocks, freshness, focus = [], showTrace = 1 }) => {
  if (open <= 0) return null;
  const sheetH = Math.round(windowHeight * WHY_SHEET);
  const priority = PRIORITIES[0];
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", inset: 0, backgroundColor: `rgba(0,0,0,${0.5 * open})` }} />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: sheetH,
          translate: `0 ${(1 - open) * sheetH}px`,
          backgroundColor: "#fff",
          borderRadius: "16px 16px 0 0",
          overflow: "hidden",
        }}
      >
        <div style={{ width: 672, margin: "0 auto", padding: "28px 24px", position: "relative" }}>
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
            <div>
              <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray500 }}>{priority.tag}</div>
              <div style={{ marginTop: 6, fontSize: 19, fontWeight: 600, lineHeight: 1.3, letterSpacing: "-0.01em", color: "#000" }}>{priority.title}</div>
            </div>
            <Icon.X size={16} color={APP.gray400} />
          </div>
          <Block label="What's happening" reveal={blocks.happening}>
            <div style={{ fontSize: 14, lineHeight: 1.6, color: APP.gray700 }}>{priority.detail}</div>
          </Block>
          <Block label="Who this is about" reveal={blocks.who}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 13.5, fontWeight: 500, color: "#000" }}>
              {DEMO.customer}
              <Icon.ArrowUpRight size={13} color={APP.gray400} />
            </div>
          </Block>
          <Block label="Why it matters" reveal={blocks.matters}>
            <div style={{ fontSize: 12.5, lineHeight: 1.5, color: APP.gray500, opacity: blocks.connected }}>
              This isn’t an isolated finding — Navis connected it to other conclusions about the same counterparty.
            </div>
            <div style={{ marginTop: 6, fontSize: 14, lineHeight: 1.6, color: APP.gray700 }}>
              {CUSTOMER.name} renews on {CUSTOMER.renewal_now}, and a promise made to them is still open.
            </div>
            <div style={{ marginTop: 4, fontSize: 12, color: APP.gray400, opacity: blocks.connected }}>2 connected conclusions</div>
          </Block>
          <Block label="What supports this" reveal={blocks.rows[0] ?? 0}>
            <div style={{ display: "flex", flexDirection: "column" }}>
              {CUSTOMER_SIGNALS.map((s, i) => (
                <div
                  key={s.field}
                  style={{
                    position: "relative",
                    height: ROW_H,
                    display: "grid",
                    gridTemplateColumns: "140px 1fr",
                    columnGap: 12,
                    alignItems: "center",
                    borderTop: i === 0 ? "none" : "1px solid rgba(0,0,0,0.05)",
                    opacity: blocks.rows[i] ?? 0,
                    backgroundColor: `rgba(17,24,39,${0.035 * (focus[i] ?? 0)})`,
                    margin: "0 -10px",
                    padding: "0 10px",
                    borderRadius: 6,
                  }}
                >
                  <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.16em", textTransform: "uppercase", color: APP.gray400 }}>{s.label}</div>
                  <div style={{ fontSize: 13.5, lineHeight: 1.55, color: APP.gray700 }}>{s.value}</div>
                  {/* Film annotation, outside the content column. */}
                  <div style={{ position: "absolute", left: 672 + 20, top: 0, height: ROW_H, opacity: showTrace }}>
                    {i === 0 ? (
                      <div style={{ position: "absolute", left: 2, top: -24, fontFamily: FONT.mono, fontSize: 11, letterSpacing: "0.26em", color: FILM.ink, opacity: blocks.rows[0] ?? 0, whiteSpace: "nowrap" }}>
                        TRACE · SIGNALS USED
                      </div>
                    ) : null}
                    <div style={{ position: "absolute", left: -18, top: ROW_H / 2, width: 14, height: 1.5, backgroundColor: FILM.cobalt, opacity: blocks.rows[i] ?? 0 }} />
                    <TraceNote signal={s} reveal={blocks.rows[i] ?? 0} freshness={freshness} />
                  </div>
                </div>
              ))}
            </div>
          </Block>
          <Block label="What you can do" reveal={blocks.canDo}>
            <div style={{ fontSize: 13.5, lineHeight: 1.55, color: APP.gray700 }}>Reply to {CONTACT.first} with the revised terms.</div>
            <div style={{ marginTop: 4, fontSize: 12.5, lineHeight: 1.5, color: APP.gray500 }}>
              Navis can prepare this for you — you review and approve before anything is sent.
            </div>
          </Block>
        </div>
      </div>
    </div>
  );
};
