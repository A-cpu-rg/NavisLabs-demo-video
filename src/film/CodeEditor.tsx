import { FONT } from "../config/navisBrand";
import { TrafficLights } from "../components/TrafficLights";
import { CONTACT, CUSTOMER, DECISION, EMAIL, WORKFLOW } from "../ui/demoContent";

// Abhishek's editor: a VS Code window (Dark Modern colours, Dark+ syntax
// colours) on the NavisLabs repository — explorer, an editor group with the
// file the agent is changing, and a second editor group holding the terminal
// where Claude Code runs. Editor chrome only; no vendor logo. The code is
// demo content.

export type CodeLine = { readonly text: string; readonly change?: "add" | "remove" };

const FN = `${CUSTOMER.short.toLowerCase()}Renewal`;

export const RENEWALS_BEFORE: readonly CodeLine[] = [
  { text: 'import { workflow } from "../lib/workflow";' },
  { text: "" },
  { text: `export const ${FN} = workflow({` },
  { text: `  account: "${CUSTOMER.slug}",` },
  { text: `  renewsOn: "${CUSTOMER.renewal_was_iso}",` },
  { text: '  terms: "usage",' },
  { text: "  remindOwner: { daysBefore: 14 }," },
  { text: "});" },
];

export const RENEWALS_AFTER: readonly CodeLine[] = [
  { text: 'import { workflow } from "../lib/workflow";' },
  { text: "" },
  { text: `export const ${FN} = workflow({` },
  { text: `  account: "${CUSTOMER.slug}",` },
  { text: `  renewsOn: "${CUSTOMER.renewal_was_iso}",`, change: "remove" },
  { text: `  // Moved by ${CONTACT.name} (Gmail, ${EMAIL.date})`, change: "add" },
  { text: `  renewsOn: "${CUSTOMER.renewal_now_iso}",`, change: "add" },
  { text: '  terms: "usage",', change: "remove" },
  { text: `  // ${DECISION.short} (${DECISION.made_in.toLowerCase()}, ${DECISION.date})`, change: "add" },
  { text: '  terms: "annual-current",', change: "add" },
  { text: "  remindOwner: { daysBefore: 14 }," },
  { text: "});" },
];

const C = {
  bg: "#1F1F1F",
  chrome: "#181818",
  border: "#2B2B2B",
  text: "#CCCCCC",
  dim: "#9D9D9D",
  lineNo: "#6E7681",
  accent: "#0078D4",
  keyword: "#569CD6",
  control: "#C586C0",
  fn: "#DCDCAA",
  str: "#CE9178",
  vari: "#9CDCFE",
  type: "#4EC9B0",
  comment: "#6A9955",
  num: "#B5CEA8",
};

const KEYWORDS = new Set(["const", "function", "async", "let", "true", "false", "null"]);
const CONTROL = new Set(["import", "from", "export", "await", "return", "if", "else"]);

/** A tiny TypeScript colouring: comments, strings, keywords, calls, types. */
const colour = (line: string): React.ReactNode[] => {
  const trimmed = line.trimStart();
  if (trimmed.startsWith("//")) return [<span key="c" style={{ color: C.comment }}>{line}</span>];
  const out: React.ReactNode[] = [];
  const re = /("[^"]*"|\b[A-Za-z_]\w*\b|-?\d+|[^\w"]+)/g;
  let m: RegExpExecArray | null;
  let i = 0;
  while ((m = re.exec(line))) {
    const tok = m[0];
    const next = line.slice(m.index + tok.length);
    let color = C.text;
    if (tok.startsWith('"')) color = C.str;
    else if (/^-?\d+$/.test(tok)) color = C.num;
    else if (KEYWORDS.has(tok)) color = C.keyword;
    else if (CONTROL.has(tok)) color = C.control;
    else if (/^[A-Z]/.test(tok) && /^\w/.test(tok)) color = C.type;
    else if (/^\w/.test(tok) && next.startsWith("(")) color = C.fn;
    else if (/^\w/.test(tok)) color = C.vari;
    out.push(<span key={i++} style={{ color }}>{tok}</span>);
  }
  return out;
};

const Tree: React.FC<{ readonly active: string }> = ({ active }) => {
  const rows: { name: string; depth: number; folder?: boolean; open?: boolean }[] = [
    { name: "NAVISLABS", depth: 0, folder: true, open: true },
    { name: "src", depth: 1, folder: true, open: true },
    { name: "billing", depth: 2, folder: true },
    { name: "lib", depth: 2, folder: true },
    { name: "workflows", depth: 2, folder: true, open: true },
    { name: WORKFLOW.file.split("/").pop() ?? WORKFLOW.file, depth: 3 },
    { name: "onboarding.ts", depth: 3 },
    { name: "package.json", depth: 1 },
    { name: "README.md", depth: 1 },
  ];
  return (
    <div style={{ fontSize: 13, color: C.text }}>
      {rows.map((r) => (
        <div
          key={r.name}
          style={{
            height: 22,
            display: "flex",
            alignItems: "center",
            paddingLeft: 8 + r.depth * 12,
            gap: 6,
            backgroundColor: r.name === active ? "rgba(255,255,255,0.08)" : "transparent",
            fontWeight: r.depth === 0 ? 700 : 400,
            fontSize: r.depth === 0 ? 11 : 13,
            letterSpacing: r.depth === 0 ? "0.04em" : 0,
          }}
        >
          <span style={{ width: 10, color: C.dim, fontSize: 10 }}>{r.folder ? (r.open ? "⌄" : "›") : ""}</span>
          <span style={{ color: r.folder ? C.text : r.name.endsWith(".ts") ? "#4D9BE6" : C.dim, fontSize: 11, width: 14, fontFamily: FONT.mono }}>{r.folder ? "" : r.name.endsWith(".ts") ? "TS" : "{}"}</span>
          <span>{r.name}</span>
        </div>
      ))}
    </div>
  );
};

const ActivityIcon: React.FC<{ readonly d: string; readonly active?: boolean }> = ({ d, active }) => (
  <div style={{ width: 48, height: 48, display: "flex", alignItems: "center", justifyContent: "center", borderLeft: `2px solid ${active ? "#FFFFFF" : "transparent"}` }}>
    <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke={active ? "#FFFFFF" : "#868686"} strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
      <path d={d} />
    </svg>
  </div>
);

const Tab: React.FC<{ readonly label: string; readonly active: boolean; readonly icon: "ts" | "term" }> = ({ label, active, icon }) => (
  <div
    style={{
      height: 35,
      display: "flex",
      alignItems: "center",
      gap: 8,
      padding: "0 14px",
      fontSize: 13,
      color: active ? "#FFFFFF" : C.dim,
      backgroundColor: active ? C.bg : C.chrome,
      borderTop: `1px solid ${active ? C.accent : "transparent"}`,
      borderRight: `1px solid ${C.border}`,
    }}
  >
    {icon === "ts" ? <span style={{ color: "#4D9BE6", fontFamily: FONT.mono, fontSize: 11 }}>TS</span> : <span style={{ color: C.dim, fontFamily: FONT.mono, fontSize: 12 }}>&gt;_</span>}
    {label}
  </div>
);

export const CodeEditor: React.FC<{
  readonly width: number;
  readonly height: number;
  readonly title: string;
  readonly file: string;
  readonly lines: readonly CodeLine[];
  readonly diff?: number;
  readonly codeDim?: number;
  readonly terminalLabel: string;
  readonly terminal: React.ReactNode;
  readonly splitAt?: number;
  readonly cursorLine?: number;
}> = ({ width, height, title, file, lines, diff = 0, codeDim = 0, terminalLabel, terminal, splitAt = 0.48 }) => {
  const sidebar = 250;
  const activity = 48;
  const editorW = width - sidebar - activity;
  const codeW = Math.round(editorW * splitAt);
  return (
    <div
      style={{
        position: "absolute",
        left: -width / 2,
        top: -height / 2,
        width,
        height,
        borderRadius: 12,
        overflow: "hidden",
        backgroundColor: C.bg,
        boxShadow: "0 0 0 1px rgba(255,255,255,0.08), 0 60px 140px -30px rgba(0,0,0,0.75)",
        fontFamily: '-apple-system, "SF Pro Text", system-ui, sans-serif',
      }}
    >
      <div style={{ height: 36, display: "flex", alignItems: "center", padding: "0 14px", backgroundColor: C.chrome, borderBottom: `1px solid ${C.border}`, position: "relative" }}>
        <TrafficLights />
        <div style={{ position: "absolute", left: 0, right: 0, textAlign: "center", fontSize: 13, color: C.dim }}>{title}</div>
      </div>
      <div style={{ position: "absolute", top: 36, bottom: 22, left: 0, width: activity, backgroundColor: C.chrome, borderRight: `1px solid ${C.border}` }}>
        <ActivityIcon active d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z M14 3v6h6" />
        <ActivityIcon d="M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14z M21 21l-5-5" />
        <ActivityIcon d="M6 3v12 M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M18 9a9 9 0 0 1-9 9" />
        <ActivityIcon d="M5 3l14 9-14 9z" />
        <ActivityIcon d="M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z" />
      </div>
      <div style={{ position: "absolute", top: 36, bottom: 22, left: activity, width: sidebar, backgroundColor: C.chrome, borderRight: `1px solid ${C.border}` }}>
        <div style={{ height: 35, display: "flex", alignItems: "center", padding: "0 20px", fontSize: 11, letterSpacing: "0.06em", color: C.dim }}>EXPLORER</div>
        <Tree active={file} />
      </div>
      {/* Editor group 1: the code. */}
      <div style={{ position: "absolute", top: 36, bottom: 22, left: activity + sidebar, width: codeW, borderRight: `1px solid ${C.border}` }}>
        <div style={{ display: "flex", backgroundColor: C.chrome, borderBottom: `1px solid ${C.border}` }}>
          <Tab label={file} active icon="ts" />
        </div>
        <div style={{ height: 24, display: "flex", alignItems: "center", padding: "0 16px", fontSize: 12, color: C.dim }}>src › workflows › {file}</div>
        <div style={{ fontFamily: FONT.mono, fontSize: 14.5, lineHeight: "24px", paddingTop: 6, position: "relative" }}>
          {lines.map((l, i) => {
            const bg = l.change === "add" ? `rgba(46,160,67,${0.2 * diff})` : l.change === "remove" ? `rgba(248,81,73,${0.2 * diff})` : "transparent";
            return (
              <div key={i} style={{ display: "flex", backgroundColor: bg, whiteSpace: "pre", opacity: l.change === "remove" ? 1 - 0.4 * diff : 1 }}>
                <span style={{ width: 48, textAlign: "right", paddingRight: 18, color: C.lineNo, flexShrink: 0 }}>{i + 1}</span>
                <span style={{ width: 14, color: l.change === "add" ? "#3FB950" : l.change === "remove" ? "#F85149" : "transparent", opacity: diff }}>{l.change === "add" ? "+" : l.change === "remove" ? "−" : ""}</span>
                <span style={{ textDecoration: l.change === "remove" && diff > 0.5 ? "line-through" : "none" }}>{colour(l.text)}</span>
              </div>
            );
          })}
          {codeDim > 0 ? <div style={{ position: "absolute", inset: 0, backgroundColor: C.bg, opacity: codeDim * 0.75 }} /> : null}
        </div>
      </div>
      {/* Editor group 2: the terminal where Claude Code runs. */}
      <div style={{ position: "absolute", top: 36, bottom: 22, left: activity + sidebar + codeW, right: 0, backgroundColor: "#181818" }}>
        <div style={{ display: "flex", backgroundColor: C.chrome, borderBottom: `1px solid ${C.border}` }}>
          <Tab label={terminalLabel} active icon="term" />
        </div>
        <div style={{ position: "absolute", top: 36, left: 0, right: 0, bottom: 0, padding: "16px 22px", fontFamily: FONT.mono, fontSize: 14.5, lineHeight: 1.6, color: "#E4E4E4", overflow: "hidden" }}>{terminal}</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 22, backgroundColor: C.chrome, borderTop: `1px solid ${C.border}`, display: "flex", alignItems: "center", gap: 18, padding: "0 12px", fontSize: 12, color: C.dim }}>
        <span>⎇ main</span>
        <span>⊗ 0  ⚠ 0</span>
        <span style={{ marginLeft: "auto" }}>Ln 5, Col 3</span>
        <span>UTF-8</span>
        <span>TypeScript</span>
      </div>
    </div>
  );
};
