import { DEV, FILM, FONT } from "../../config/navisBrand";
import { APP_WORKSPACE, CUSTOMER, EMAIL, type ContextFact } from "../demoContent";
import { BrandIcon } from "../Integrations";
import { type Reveal, ToolCall } from "./AgentConversation";

// Company context through Navis Developer's MCP server.
//   ContextRequest -> Devtool/services/mcp-server/src/tools/register.ts:
//     tool `navis_get_relevant_context`, input `task`.
//   ContextResult / SourceCard / FreshnessBadge -> the same tool's result:
//     items[] (GroundedFact: kind, text, source, occurred_at, lineage,
//     subject — packages/types developer.d.ts), sources.detail[] (source,
//     label, connected, auth_state 'ok' | 'reconsent_required',
//     last_success_at) and freshness (as_of, newest_fact_at).
// Navis calls no generative model to answer this tool.

export const ContextRequest: React.FC<{
  readonly task: string;
  readonly status: "running" | "ok" | "error";
  readonly children?: React.ReactNode;
  readonly reveal?: Reveal;
}> = ({ task, status, children, reveal }) => (
  <ToolCall
    name="navis - navis_get_relevant_context (MCP)"
    args={
      <>
        task: <span style={{ color: "#D6D3CC" }}>&quot;{task}&quot;</span>
      </>
    }
    status={status}
    reveal={reveal}
  >
    {children}
  </ToolCall>
);

const Label: React.FC<{ readonly children: React.ReactNode; readonly color?: string }> = ({ children, color = FILM.onInkDim }) => (
  <div style={{ fontFamily: FONT.mono, fontSize: 11, letterSpacing: "0.16em", textTransform: "uppercase", color }}>{children}</div>
);

export const FreshnessBadge: React.FC<{ readonly asOf: string; readonly newestFactAt: string; readonly opacity?: number }> = ({ asOf, newestFactAt, opacity = 1 }) => (
  <div
    style={{
      opacity,
      display: "inline-flex",
      alignSelf: "flex-start",
      alignItems: "center",
      gap: 10,
      padding: "6px 12px",
      borderRadius: 999,
      border: "1px solid rgba(237,235,230,0.16)",
      fontFamily: FONT.mono,
      fontSize: 12,
      color: DEV.termMuted,
      whiteSpace: "nowrap",
    }}
  >
    <span style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: DEV.termGreen }} />
    <span>
      as_of <span style={{ color: DEV.termText }}>{asOf}</span>
    </span>
    <span style={{ color: DEV.termDim }}>·</span>
    <span>
      newest_fact_at <span style={{ color: DEV.termText }}>{newestFactAt}</span>
    </span>
  </div>
);

/** One returned fact, as the agent receives it: what, from where, how fresh. */
export const ContextFactCard: React.FC<{
  readonly fact: ContextFact;
  readonly reveal: number;
  readonly source01: number;
  readonly fresh01: number;
  readonly emphasis?: number;
  readonly width?: number;
}> = ({ fact, reveal, source01, fresh01, emphasis = 0, width = 780 }) => (
  <div
    style={{
      width,
      opacity: reveal,
      translate: `${(1 - reveal) * -24}px 0`,
      display: "grid",
      gridTemplateColumns: "1fr 290px",
      columnGap: 22,
      alignItems: "center",
      backgroundColor: FILM.inkRaised,
      border: `1px solid rgba(237,235,230,${0.09 + emphasis * 0.18})`,
      borderRadius: 14,
      padding: "14px 18px",
      boxShadow: "0 24px 60px -24px rgba(0,0,0,0.7)",
    }}
  >
    <div>
      <div style={{ display: "flex", gap: 10, alignItems: "baseline" }}>
        <Label color={FILM.onInkMuted}>{fact.label}</Label>
        <span style={{ fontFamily: FONT.mono, fontSize: 11, color: DEV.termDim }}>kind: {fact.kind}</span>
      </div>
      <div style={{ marginTop: 6, fontFamily: FONT.display, fontSize: 19, lineHeight: 1.35, fontWeight: 500, color: FILM.onInk }}>{fact.text}</div>
    </div>
    <div style={{ borderLeft: "1px solid rgba(237,235,230,0.08)", paddingLeft: 18, display: "flex", flexDirection: "column", gap: 7 }}>
      <div style={{ opacity: source01, display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 26, height: 26, borderRadius: 7, backgroundColor: "#fff", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
          <BrandIcon id={fact.source} height={fact.source === "slack" ? 12 : 14} />
        </div>
        <div style={{ fontFamily: FONT.mono, fontSize: 12, color: DEV.termText, whiteSpace: "nowrap" }}>{fact.sourceLabel}</div>
      </div>
      <div style={{ opacity: fresh01, fontFamily: FONT.mono, fontSize: 11.5, color: DEV.termMuted, whiteSpace: "nowrap" }}>
        occurred_at {fact.occurredAt}
        <br />
        <span style={{ color: DEV.termGreen }}>auth_state ok</span> · last_success_at {fact.lastSuccessAt}
      </div>
    </div>
  </div>
);

/** The returned bundle about one customer. */
export const CustomerContextPanel: React.FC<{
  readonly facts: readonly ContextFact[];
  readonly reveal: readonly number[];
  readonly source01: number;
  readonly fresh01: number;
  readonly header: number;
  readonly emphasis?: readonly number[];
}> = ({ facts, reveal, source01, fresh01, header, emphasis = [] }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
    <div style={{ opacity: header, display: "flex", alignItems: "baseline", justifyContent: "space-between", width: 780 }}>
      <div style={{ fontFamily: FONT.display, fontSize: 30, fontWeight: 600, letterSpacing: "0.04em", color: FILM.onInk }}>{CUSTOMER.caps}</div>
      <FreshnessBadge asOf={`${APP_WORKSPACE.date_iso} ${APP_WORKSPACE.now}`} newestFactAt={EMAIL.date_iso} opacity={fresh01} />
    </div>
    <Label color={FILM.onInkDim}>
      navis_get_relevant_context · {facts.length} items · Source · Freshness
    </Label>
    {facts.map((f, i) => (
      <ContextFactCard key={f.label} fact={f} reveal={reveal[i] ?? 0} source01={source01} fresh01={fresh01} emphasis={emphasis[i] ?? 0} />
    ))}
  </div>
);
