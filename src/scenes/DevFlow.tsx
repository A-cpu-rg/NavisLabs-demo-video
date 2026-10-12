import { AbsoluteFill, interpolate } from "remotion";
import { BEAT, TYPING, typingEnd, sec } from "../config/beats";
import { copy } from "../config/filmSpec";
import { DEMO, DEV, FONT } from "../config/navisBrand";
import type { CameraKeyframe } from "../config/types";
import { Camera } from "../components/Camera";
import { CodeEditor, RENEWALS_AFTER, RENEWALS_BEFORE } from "../film/CodeEditor";
import { ProductTag } from "../film/ProductReveal";
import { AgentConversation, AgentText, PromptInput, ShellLine, ToolCall, UserTurn } from "../ui/developer/AgentConversation";
import { ContextRequest } from "../ui/developer/Context";
import { AGENT_LINES, APP_WORKSPACE, CUSTOMER, RESULT_ROWS, WORKFLOW } from "../ui/demoContent";
import { DeveloperShell } from "../ui/developer/DeveloperShell";
import { CLAMP, caretOn, easeOut, typedCount } from "../ui/kit";

// S10, S12 and S15 share one take in Abhishek's environment: VS Code on the
// NavisLabs repository, Claude Code running in a terminal editor group (the
// prompt is this Mac's real user and host). Claude Code is the client Navis
// Developer lists as LIVE VERIFIED over MCP (Devtool/docs/mcp/CLIENTS.md);
// Cursor, Codex and VS Code's own MCP client are CONFIG VERIFIED only and are
// not shown as integrations. The agent gets the task, asks Navis Developer for
// company context (navis_get_relevant_context), and uses what comes back.

const r = (T: number, a: number, b: number, e: (x: number) => number = easeOut) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

export const VSCODE = { w: 1640, h: 940 } as const;
const FILE = WORKFLOW.file.split("/").pop() ?? WORKFLOW.file;
const TASK_TEXT = TYPING.agentTask.text;

/** The MCP tool result rows come from the demo data (RESULT_ROWS). */
// Columns are sized to their longest cell so no source ever runs into FRESHNESS.
const FACT_W = Math.max(...RESULT_ROWS.map((row) => row.fact.length)) + 2;
const SOURCE_W = Math.max("SOURCE · DATE".length, ...RESULT_ROWS.map((row) => row.source.length)) + 2;

const Col: React.FC<{ readonly w: number; readonly hl?: number; readonly color?: string; readonly children: React.ReactNode }> = ({ w, hl = 0, color = DEV.termText, children }) => (
  <span style={{ display: "inline-block", width: `${w}ch`, color, backgroundColor: hl > 0 ? `rgba(111,168,255,${0.16 * hl})` : undefined, boxShadow: hl > 0 ? `0 0 0 3px rgba(111,168,255,${0.16 * hl})` : undefined, whiteSpace: "pre" }}>{children}</span>
);

const ContextTable: React.FC<{ readonly rows: readonly number[]; readonly source: number; readonly fresh: number; readonly header: number }> = ({ rows, source, fresh, header }) => (
  <div style={{ fontFamily: FONT.mono }}>
    <div style={{ opacity: header, color: DEV.termText }}>
      {CUSTOMER.caps} <span style={{ color: DEV.termMuted }}>· {RESULT_ROWS.length} facts · as_of {APP_WORKSPACE.date_iso} {APP_WORKSPACE.now}</span>
    </div>
    <div style={{ opacity: header, color: DEV.termDim, marginTop: 2 }}>
      <Col w={FACT_W} color={DEV.termDim}>FACT</Col>
      <Col w={SOURCE_W} color={DEV.termDim} hl={source}>SOURCE · DATE</Col>
      <Col w={12} color={DEV.termDim} hl={fresh}>FRESHNESS</Col>
    </div>
    {RESULT_ROWS.map((row, i) => (
      <div key={row.fact} style={{ opacity: rows[i] ?? 0 }}>
        <Col w={FACT_W}>{row.fact}</Col>
        <Col w={SOURCE_W} hl={source} color={DEV.termBlue}>{row.source}</Col>
        <Col w={12} hl={fresh} color={DEV.termGreen}>{row.fresh}</Col>
      </div>
    ))}
    <div style={{ opacity: rows[RESULT_ROWS.length - 1] ?? 0, color: DEV.termDim }}>… +31 lines (ctrl+r to expand)</div>
  </div>
);

export const DevFlow: React.FC<{ readonly T: number; readonly keyframes: readonly CameraKeyframe[] }> = ({ T, keyframes }) => {
  const task = TYPING.agentTask;
  const typed = typedCount(task.text, sec(T), sec(task.start), task.cps);
  const submitted = T >= BEAT.agentEnter;
  const typingNow = T >= task.start && T < typingEnd(task);
  const read = r(T, BEAT.agentRead, BEAT.agentRead + 0.2);
  const needs = r(T, BEAT.agentNeeds, BEAT.agentNeeds + 0.25);
  const call = r(T, BEAT.contextCall, BEAT.contextCall + 0.2);
  const answered = T >= BEAT.contextResult;
  const tableRows = RESULT_ROWS.map((_, i) => r(T, BEAT.contextResult + 0.1 + i * 0.12, BEAT.contextResult + 0.25 + i * 0.12));
  const tableHeader = r(T, BEAT.contextResult, BEAT.contextResult + 0.15);
  const source = r(T, BEAT.contextSource, BEAT.contextSource + 0.2) * (1 - r(T, BEAT.contextFresh - 0.1, BEAT.contextFresh + 0.1));
  const fresh = r(T, BEAT.contextFresh, BEAT.contextFresh + 0.2) * (1 - r(T, BEAT.agentReason - 0.1, BEAT.agentReason + 0.1));
  const reason = r(T, BEAT.agentReason, BEAT.agentReason + 0.25);
  const update = r(T, BEAT.agentUses, BEAT.agentUses + 0.25);
  const diff = r(T, BEAT.agentUses + 0.1, BEAT.agentUses + 0.5);
  const done = r(T, BEAT.agentDone, BEAT.agentDone + 0.3);
  // The product name sits above the window only while it is framed small.
  const caption = r(T, BEAT.devCaption + 0.05, BEAT.devCaption + 0.3) * (1 - r(T, task.start - 0.3, task.start - 0.05));

  return (
    <AbsoluteFill>
      <DeveloperShell lift={0.5}>
        <Camera keyframes={keyframes}>
          <CodeEditor
            width={VSCODE.w}
            height={VSCODE.h}
            title={`${FILE} — ${DEMO.repo}`}
            file={FILE}
            lines={T >= BEAT.agentUses ? RENEWALS_AFTER : RENEWALS_BEFORE}
            diff={diff}
            codeDim={0}
            terminalLabel="claude"
            splitAt={0.45}
            terminal={
              <AgentConversation>
                <ShellLine user={`${DEMO.macUser}@${DEMO.macHost}`} repo={DEMO.repo} command="claude" />
                <div style={{ height: 6 }} />
                {submitted ? <UserTurn text={TASK_TEXT} /> : null}
                {submitted ? (
                  <ToolCall name="Read" args={AGENT_LINES.read} reveal={{ opacity: read }}>
                    <span style={{ color: DEV.termMuted }}>Read 8 lines</span>
                  </ToolCall>
                ) : null}
                {needs > 0 ? (
                  <AgentText reveal={{ opacity: needs }}>
                    {AGENT_LINES.needs}
                  </AgentText>
                ) : null}
                {call > 0 ? (
                  <ContextRequest task={TASK_TEXT.replace(/\.$/, "")} status={answered ? "ok" : "running"} reveal={{ opacity: call }}>
                    {answered ? <ContextTable rows={tableRows} source={source} fresh={fresh} header={tableHeader} /> : <span style={{ color: DEV.termDim }}>Running…</span>}
                  </ContextRequest>
                ) : null}
                {reason > 0 ? (
                  <AgentText reveal={{ opacity: reason }}>
                    {AGENT_LINES.reason[0]}
                    <span style={{ color: DEV.termMuted }}>{AGENT_LINES.reason[1]}</span>
                    {AGENT_LINES.reason[2]}
                    <span style={{ color: DEV.termMuted }}>{AGENT_LINES.reason[3]}</span>
                    {AGENT_LINES.reason[4]}
                  </AgentText>
                ) : null}
                {update > 0 ? (
                  <ToolCall name="Update" args={AGENT_LINES.read} reveal={{ opacity: update }}>
                    <span style={{ color: DEV.termMuted }}>
                      Updated {AGENT_LINES.read} with <span style={{ color: DEV.termGreen }}>4 additions</span> and <span style={{ color: DEV.termRed }}>2 removals</span>
                    </span>
                  </ToolCall>
                ) : null}
                {done > 0 ? (
                  <AgentText reveal={{ opacity: done }}>
                    {AGENT_LINES.done}
                  </AgentText>
                ) : null}
                <PromptInput text={submitted ? "" : task.text.slice(0, typed)} caret={caretOn(sec(T), typingNow)} highlight={typingNow ? 1 : 0} />
              </AgentConversation>
            }
          />
        </Camera>
        <ProductTag name={copy("product.developer")} audience={copy("product.developer.audience")} badge={copy("product.developer.status")} reveal={caption} tone="dark" />
      </DeveloperShell>
    </AbsoluteFill>
  );
};
