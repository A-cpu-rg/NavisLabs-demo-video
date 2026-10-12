import { DEMO, DEV, FILM, FONT } from "../../config/navisBrand";
import { ShellLine } from "./AgentConversation";
import { AGENT_TASK, APP_WORKSPACE, EMAIL, EVENT_FACT } from "../demoContent";

const TASK_JSON = `'${JSON.stringify({ task: AGENT_TASK.replace(/\.$/, "") })}'`;

// The SDK and the Developer API as an engineer meets them: a terminal.
//   SdkPane -> Devtool/apps/dashboard/src/features/connect/data/surfaces.ts:
//     @navis/sdk 0.1.0 is not published; installToday is the local tarball,
//     and the example is the SDK's own (me(), context()).
//   ApiPane -> POST /developer/context (the route behind the MCP tool) with
//     the real header, X-API-Key (packages/api-client/src/credentials.ts);
//     the answer keeps the real field names (items, sources, freshness).
// Values are demo data. No credential appears: only $NAVIS_API_KEY.

const K = { key: "#9CDCFE", str: "#CE9178", kw: "#C586C0", fn: "#DCDCAA", com: "#6A9955", type: "#4EC9B0" };
const c = (color: string, text: string) => <span style={{ color }}>{text}</span>;
const USER = `${DEMO.macUser}@${DEMO.macHost}`;

const Pane: React.FC<{ readonly title: string; readonly badge?: string; readonly width: number; readonly reveal: number; readonly children: React.ReactNode }> = ({ title, badge, width, reveal, children }) => (
  <div style={{ width, opacity: reveal, translate: `0 ${(1 - reveal) * 14}px`, borderRadius: 12, backgroundColor: DEV.termRaised, boxShadow: "0 0 0 1px rgba(237,235,230,0.09), 0 30px 80px -30px rgba(0,0,0,0.7)", overflow: "hidden" }}>
    <div style={{ height: 36, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 16px", backgroundColor: "#1F1E1A", borderBottom: "1px solid rgba(237,235,230,0.06)" }}>
      <div style={{ display: "flex", gap: 7 }}>
        {["#FF5F57", "#FEBC2E", "#28C840"].map((col) => (
          <span key={col} style={{ width: 11, height: 11, borderRadius: 6, backgroundColor: col }} />
        ))}
      </div>
      <div style={{ fontFamily: FONT.mono, fontSize: 12.5, color: DEV.termDim }}>{title}</div>
      {badge ? <div style={{ padding: "2px 9px", borderRadius: 999, border: "1px solid rgba(237,235,230,0.18)", fontFamily: FONT.mono, fontSize: 10.5, letterSpacing: "0.14em", textTransform: "uppercase", color: FILM.onInkMuted }}>{badge}</div> : <span />}
    </div>
    <div style={{ padding: "16px 20px", fontFamily: FONT.mono, fontSize: 14.5, lineHeight: 1.65, color: DEV.termText, whiteSpace: "pre" }}>{children}</div>
  </div>
);

export const SdkPane: React.FC<{ readonly reveal: number; readonly typed: string; readonly installed: number; readonly code: readonly number[] }> = ({ reveal, typed, installed, code }) => {
  const L = (i: number, node: React.ReactNode) => <div style={{ opacity: code[i] ?? 0 }}>{node}</div>;
  return (
    <Pane title="SDK · TypeScript" badge="Private preview" width={800} reveal={reveal}>
      <ShellLine user={USER} repo={DEMO.repo} command={typed} />
      <div style={{ opacity: installed, color: DEV.termMuted }}>added 1 package, and audited 2 packages in 1s</div>
      <div style={{ opacity: installed, color: DEV.termDim }}># @navis/sdk 0.1.0 · local package · not on npm yet</div>
      <div style={{ height: 12 }} />
      {L(0, <span style={{ color: DEV.termDim }}>context.ts</span>)}
      {L(0, <>{c(K.kw, "import")} {"{ "}{c(K.type, "Navis")}{" }"} {c(K.kw, "from")} {c(K.str, "'@navis/sdk'")};</>)}
      {L(1, <>{c(K.kw, "const")} {c(K.key, "navis")} = {c(K.kw, "new")} {c(K.type, "Navis")}({"{ "}{c(K.key, "apiKey")}: process.env.{c(K.key, "NAVIS_API_KEY")}{" }"});</>)}
      {L(2, <>{c(K.kw, "const")} {c(K.key, "me")} = {c(K.kw, "await")} navis.{c(K.fn, "me")}();      {c(K.com, "// who this key is")}</>)}
      {L(3, <>{c(K.kw, "const")} {c(K.key, "context")} = {c(K.kw, "await")} navis.{c(K.fn, "context")}();</>)}
    </Pane>
  );
};

export const ApiPane: React.FC<{ readonly reveal: number; readonly response: number; readonly emphasis: number }> = ({ reveal, response, emphasis }) => {
  const hl = (node: React.ReactNode) => <span style={{ backgroundColor: `rgba(111,168,255,${0.18 * emphasis})`, borderRadius: 3 }}>{node}</span>;
  return (
    <Pane title="Developer API" badge="Private preview" width={860} reveal={reveal}>
      <div>
        <span style={{ color: DEV.termGreen }}>NavisLabs</span> <span style={{ color: DEV.termDim }}>%</span> curl -s {c(K.str, '"$NAVIS_BASE_URL/developer/context"')} \
      </div>
      <div>{"    "}-H {c(K.str, '"X-API-Key: $NAVIS_API_KEY"')} \</div>
      <div>{"    "}--json {c(K.str, TASK_JSON)}</div>
      <div style={{ opacity: response }}>
        <div>{"{"}</div>
        <div>{"  "}{c(K.key, '"items"')}: [{"{ "}{c(K.key, '"text"')}: {c(K.str, JSON.stringify(EVENT_FACT))},</div>
        <div>{"             "}{hl(<>{c(K.key, '"source"')}: {c(K.str, '"gmail"')}</>)}, {c(K.key, '"occurred_at"')}: {c(K.str, JSON.stringify(EMAIL.date_iso))}{" }"}, …],</div>
        <div>{"  "}{c(K.key, '"sources"')}: {"{ "}{c(K.key, '"detail"')}: [{"{ "}{c(K.key, '"source"')}: {c(K.str, '"gmail"')}, {c(K.key, '"auth_state"')}: {c(K.str, '"ok"')}{" }"}, …]{" }"},</div>
        <div>{"  "}{hl(<>{c(K.key, '"freshness"')}: {"{ "}{c(K.key, '"as_of"')}: {c(K.str, JSON.stringify(`${APP_WORKSPACE.date_iso}T${APP_WORKSPACE.now}Z`))}{" }"}</>)}</div>
        <div>{"}"}</div>
      </div>
    </Pane>
  );
};
