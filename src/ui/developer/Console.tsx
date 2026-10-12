import { DEMO, DEV, FONT } from "../../config/navisBrand";
import { TrafficLights } from "../../components/TrafficLights";
import { AGENT, RUN, RUNS as DEMO_RUNS } from "../demoContent";

// The Navis Developer Console (Devtool/apps/dashboard), rebuilt from source:
//   navigation   -> src/lib/navigation.ts (groups and labels, in order)
//   shell        -> components/layout/SidebarFrame.tsx ("Navis Developer",
//                   bg-surface sidebar, border-line), globals.css tokens
//   Connect      -> features/connect/ConnectIndex.tsx (title, description,
//                   "Access surfaces") + data/surfaces.ts (surfaces, the
//                   MCP command, SDK installToday, CLI commands)
//   Run          -> features/runs/RunDetailPanel.tsx ("Run", "One attempt at
//                   a task.", "What happened", "Timeline" columns, step types
//                   Context/Tool/Model/Outcome, "Outcome") + run-story.ts.
// Rows, ids and timings are demo data. No cost, token or latency figure is
// invented: those cells read "—", as the console does for "not recorded".

const T = {
  canvas: "#f7f6f3",
  surface: "#ffffff",
  muted: "#f0eeea",
  line: "#e5e2dc",
  ink: DEV.ink,
  inkMuted: DEV.inkMuted,
  subtle: DEV.subtle,
  accent: "#2e2a24",
  positive: DEV.positive,
  positiveSoft: "#eef2ef",
  caution: "#7a5a1e",
  cautionSoft: "#f6f1e6",
};

const NAV: readonly { group: string | null; items: readonly string[] }[] = [
  { group: "Workspace", items: ["Overview"] },
  { group: "Build", items: ["Agents", "Context", "Policies"] },
  { group: "Connect", items: ["API", "SDKs", "API keys", "MCP"] },
  { group: "Observe", items: ["Runs", "Outcomes", "Economics", "Learning"] },
  { group: "Data", items: ["Memory", "State"] },
  { group: "Administration", items: ["Organization", "Members"] },
  { group: null, items: ["Developer Docs"] },
];

export const CONSOLE = { w: 1440, h: 900, titlebar: 40, sidebar: 236 } as const;

export const ConsoleShell: React.FC<{ readonly active: string; readonly children: React.ReactNode; readonly scroll?: number }> = ({ active, children, scroll = 0 }) => (
  <div
    style={{
      position: "absolute",
      left: -CONSOLE.w / 2,
      top: -(CONSOLE.h + CONSOLE.titlebar) / 2,
      width: CONSOLE.w,
      height: CONSOLE.h + CONSOLE.titlebar,
      borderRadius: 14,
      overflow: "hidden",
      backgroundColor: T.canvas,
      fontFamily: FONT.display,
      color: T.ink,
      boxShadow: "0 0 0 1px rgba(20,19,15,0.1), 0 60px 140px -30px rgba(0,0,0,0.6)",
    }}
  >
    <div style={{ height: CONSOLE.titlebar, display: "flex", alignItems: "center", padding: "0 16px", backgroundColor: "#efede8", borderBottom: `1px solid ${T.line}`, position: "relative" }}>
      <TrafficLights />
      <div style={{ position: "absolute", left: "50%", translate: "-50% 0", width: 420, height: 24, borderRadius: 7, backgroundColor: "rgba(20,19,15,0.06)" }} />
    </div>
    <div style={{ position: "absolute", top: CONSOLE.titlebar, left: 0, bottom: 0, width: CONSOLE.sidebar, backgroundColor: T.surface, borderRight: `1px solid ${T.line}`, padding: "16px 12px" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 6, padding: "0 4px" }}>
        <span style={{ fontSize: 14, fontWeight: 600, letterSpacing: "-0.01em" }}>Navis</span>
        <span style={{ fontSize: 12, color: T.subtle }}>Developer</span>
      </div>
      <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8, border: `1px solid ${T.line}`, borderRadius: 6, padding: "6px 8px", fontSize: 12.5 }}>
        <span style={{ width: 18, height: 18, borderRadius: 4, backgroundColor: T.muted, fontSize: 10, fontWeight: 600, display: "flex", alignItems: "center", justifyContent: "center", color: T.inkMuted }}>N</span>
        {DEMO.org}
      </div>
      <div style={{ marginTop: 10 }}>
        {NAV.map((g) => (
          <div key={g.group ?? "trail"} style={{ marginTop: 10 }}>
            {g.group ? <div style={{ padding: "0 6px", fontSize: 10.5, fontWeight: 500, color: T.subtle, letterSpacing: "0.02em" }}>{g.group}</div> : null}
            {g.items.map((it) => (
              <div
                key={it}
                style={{
                  marginTop: 2,
                  padding: "5px 8px",
                  borderRadius: 6,
                  fontSize: 13,
                  color: it === active ? T.ink : T.inkMuted,
                  fontWeight: it === active ? 500 : 400,
                  backgroundColor: it === active ? T.muted : "transparent",
                }}
              >
                {it}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
    <div style={{ position: "absolute", top: CONSOLE.titlebar, left: CONSOLE.sidebar, right: 0, bottom: 0, overflow: "hidden" }}>
      <div style={{ padding: "34px 44px", translate: `0 ${-scroll}px` }}>{children}</div>
    </div>
  </div>
);

export const PageHeader: React.FC<{ readonly title: string; readonly description: string; readonly badge?: string }> = ({ title, description, badge }) => (
  <div style={{ borderBottom: `1px solid ${T.line}`, paddingBottom: 18, display: "flex", justifyContent: "space-between", gap: 20 }}>
    <div>
      <div style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-0.01em" }}>{title}</div>
      <div style={{ marginTop: 6, maxWidth: 760, fontSize: 14, lineHeight: 1.6, color: T.inkMuted }}>{description}</div>
    </div>
    {badge ? (
      <div style={{ alignSelf: "flex-start", border: `1px solid ${T.line}`, backgroundColor: T.cautionSoft, color: T.caution, borderRadius: 4, padding: "3px 8px", fontSize: 12, fontWeight: 500, whiteSpace: "nowrap" }}>{badge}</div>
    ) : null}
  </div>
);

const Code: React.FC<{ readonly children: React.ReactNode; readonly highlight?: number }> = ({ children, highlight = 0 }) => (
  <div
    style={{
      marginTop: 12,
      borderRadius: 8,
      backgroundColor: "#1f1e1a",
      color: "#EDEBE6",
      fontFamily: FONT.mono,
      fontSize: 12.5,
      lineHeight: 1.6,
      padding: "10px 12px",
      whiteSpace: "pre-wrap",
      wordBreak: "break-all",
      boxShadow: highlight > 0 ? `0 0 0 ${2 * highlight}px #1976FE` : undefined,
    }}
  >
    {children}
  </div>
);

export const SURFACES = [
  {
    name: "MCP",
    summary: "Agents that already speak MCP reach Navis through it without any Navis-specific code.",
    code: "claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> -- node <repo>/services/mcp-server/dist/stdio.js",
  },
  {
    name: "Developer API",
    summary: "The contract everything else is built on — reached with one API key, scoped to one organization.",
    code: "POST /developer/context",
  },
  {
    name: "SDK",
    summary: "Typed TypeScript and Python clients over the Developer API. Not published to a registry yet.",
    code: "npm install ./navis-sdk-0.1.0.tgz",
  },
  {
    name: "CLI",
    summary: "Work continuity for coding sessions, from the terminal.",
    code: "navis workstate checkpoint",
  },
] as const;

/** Connect: the four interfaces onto the same intelligence. */
export const ConnectPage: React.FC<{ readonly reveal: readonly number[]; readonly highlight?: number; readonly focus?: readonly number[] }> = ({ reveal, highlight = 0, focus = [] }) => (
  <div>
    <PageHeader
      title="Connect"
      description="Connect your AI agents and applications to Navis. MCP, the Developer API, the SDK and the CLI are four interfaces onto the same organizational intelligence, reached with the same credential and bounded by the same permissions."
      badge="Private preview"
    />
    <div style={{ marginTop: 22, fontSize: 13, fontWeight: 600 }}>Access surfaces</div>
    <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
      {SURFACES.map((s, i) => (
        <div key={s.name} style={{ borderRadius: 10, border: `1px solid ${T.line}`, backgroundColor: T.surface, padding: "16px 18px", opacity: reveal[i] ?? 0, translate: `0 ${(1 - (reveal[i] ?? 0)) * 12}px`, boxShadow: (focus[i] ?? 0) > 0 ? `0 0 0 ${1.5 * (focus[i] ?? 0)}px ${T.ink}, 0 8px 24px -12px rgba(20,19,15,${0.35 * (focus[i] ?? 0)})` : undefined }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ fontSize: 15, fontWeight: 600 }}>{s.name}</div>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, color: T.ink }}>
              <span style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: T.positive }} />
              Available
            </span>
          </div>
          <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.55, color: T.inkMuted }}>{s.summary}</div>
          <Code highlight={i === 0 ? highlight : 0}>{s.code}</Code>
        </div>
      ))}
    </div>
  </div>
);

export type RunRow = { task: string; agent: string; status: string; started: string; duration: string; run: string };
export const RUNS: readonly RunRow[] = DEMO_RUNS.map((r) => ({ task: r.task, agent: AGENT.name, status: r.status, started: r.started, duration: r.duration, run: r.id }));

const TH: React.FC<{ readonly children: React.ReactNode; readonly w?: number }> = ({ children, w }) => (
  <th style={{ textAlign: "left", padding: "9px 14px", fontSize: 12, fontWeight: 500, color: T.subtle, width: w }}>{children}</th>
);
const TD: React.FC<{ readonly children: React.ReactNode; readonly mono?: boolean; readonly muted?: boolean }> = ({ children, mono, muted }) => (
  <td style={{ padding: "11px 14px", fontSize: 13.5, color: muted ? T.inkMuted : T.ink, fontFamily: mono ? FONT.mono : undefined }}>{children}</td>
);
const Status: React.FC<{ readonly label: string }> = ({ label }) => (
  <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
    {/* lib/runs.ts: running and completed both use the accent tone — a completed run is not
        a judged-good run, so it is deliberately not green. Running pulses. */}
    <span style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: label === "Running" || label === "Completed" ? T.accent : T.subtle }} />
    {label}
  </span>
);

export const RunsPage: React.FC<{ readonly highlight: number; readonly arrive?: number; readonly running?: boolean }> = ({ highlight, arrive = 1, running = false }) => (
  <div>
    <PageHeader title="Runs" description="What your agents did. A task is what was asked; a run is one attempt at it, with the steps, context and outcome the agent reported." />
    <div style={{ marginTop: 22, borderRadius: 8, border: `1px solid ${T.line}`, backgroundColor: T.surface, overflow: "hidden" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead style={{ backgroundColor: "rgba(240,238,234,0.6)", borderBottom: `1px solid ${T.line}` }}>
          <tr>
            <TH>Task</TH>
            <TH w={160}>Agent</TH>
            <TH w={130}>Status</TH>
            <TH w={150}>Started</TH>
            <TH w={110}>Duration</TH>
          </tr>
        </thead>
        <tbody>
          {RUNS.map((r, i) => (
            <tr key={r.run} style={{ borderTop: i ? `1px solid ${T.line}` : "none", backgroundColor: i === 0 ? `rgba(240,238,234,${0.8 * highlight})` : "transparent", opacity: i === 0 ? arrive : 1, translate: i === 0 ? `0 ${(1 - arrive) * -10}px` : undefined }}>
              <td style={{ padding: "11px 14px" }}>
                <div style={{ fontSize: 13.5, textDecoration: "underline", textUnderlineOffset: 4, textDecorationColor: "rgba(20,19,15,0.25)" }}>{r.task}</div>
                <div style={{ marginTop: 3, fontSize: 12, color: T.subtle, fontFamily: FONT.mono }}>run {r.run}</div>
              </td>
              <TD muted>{r.agent}</TD>
              <TD>
                <Status label={i === 0 && running ? "Running" : r.status} />
              </TD>
              <TD mono muted>
                {r.started}
              </TD>
              <TD mono muted>
                {i === 0 && running ? "—" : r.duration}
              </TD>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const STEPS = RUN.steps ?? [];

const Section: React.FC<{ readonly title: string; readonly description?: string; readonly children: React.ReactNode; readonly reveal?: number }> = ({ title, description, children, reveal = 1 }) => (
  <div style={{ marginTop: 24, opacity: reveal }}>
    <div style={{ fontSize: 14, fontWeight: 600 }}>{title}</div>
    {description ? <div style={{ marginTop: 3, fontSize: 12.5, color: T.subtle }}>{description}</div> : null}
    <div style={{ marginTop: 10 }}>{children}</div>
  </div>
);

const Field: React.FC<{ readonly label: string; readonly children: React.ReactNode }> = ({ label, children }) => (
  <div>
    <div style={{ fontSize: 12, color: T.subtle }}>{label}</div>
    <div style={{ marginTop: 3, fontSize: 13.5, color: T.ink }}>{children}</div>
  </div>
);

export const RunDetailPage: React.FC<{ readonly rows: readonly number[]; readonly outcome: number; readonly complete?: boolean }> = ({ rows, outcome, complete = true }) => (
  <div>
    <PageHeader title="Run" description="One attempt at a task." />
    <Section title="What happened">
      <div style={{ fontSize: 14, lineHeight: 1.6, color: T.inkMuted, maxWidth: 860 }}>
        {AGENT.name} reported {STEPS.length} steps during this attempt. What it reported is summarised below; anything it did not report is marked as not reported rather than assumed.
      </div>
    </Section>
    <Section title="Execution">
      <div style={{ display: "grid", gridTemplateColumns: "2.2fr 1fr 1fr 1fr 1fr", gap: 18, borderRadius: 8, border: `1px solid ${T.line}`, backgroundColor: T.surface, padding: "12px 16px" }}>
        <Field label="Task">{RUNS[0].task}</Field>
        <Field label="Agent">{RUNS[0].agent}</Field>
        <Field label="Status">
          <Status label={complete ? RUNS[0].status : "Running"} />
        </Field>
        <Field label="Started">{RUNS[0].started}</Field>
        <Field label="Duration">{complete ? RUNS[0].duration : "—"}</Field>
      </div>
    </Section>
    <Section title="Timeline" description="What was reported inside this attempt, in order — the rows every figure above is summed from.">
      <div style={{ borderRadius: 8, border: `1px solid ${T.line}`, backgroundColor: T.surface, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ backgroundColor: "rgba(240,238,234,0.6)", borderBottom: `1px solid ${T.line}` }}>
            <tr>
              <TH w={40}>#</TH>
              <TH w={100}>Type</TH>
              <TH>What</TH>
              <TH w={120}>Status</TH>
              <TH w={80}>Model</TH>
              <TH w={80}>Tokens</TH>
              <TH w={70}>Cost</TH>
              <TH w={80}>Latency</TH>
            </tr>
          </thead>
          <tbody>
            {STEPS.map((s, i) =>
              (rows[i] ?? 0) <= 0 ? null : (
              <tr key={i} style={{ borderTop: i ? `1px solid ${T.line}` : "none", opacity: rows[i], backgroundColor: s.type === "Context" ? `rgba(25,118,254,${0.06 * rows[i]})` : "transparent" }}>
                <TD mono muted>
                  {i + 1}
                </TD>
                <TD>{s.type}</TD>
                <td style={{ padding: "11px 14px", fontSize: 13.5, color: T.inkMuted }}>
                  <span style={{ fontFamily: FONT.mono, fontSize: 12, color: T.subtle, marginRight: 10 }}>{s.at}</span>
                  {s.what}
                </td>
                <TD>
                  <Status label={!complete && i === STEPS.length - 1 ? "Running" : !complete && (rows[i + 1] ?? 0) <= 0 ? "Running" : "Completed"} />
                </TD>
                <TD muted>—</TD>
                <TD muted>—</TD>
                <TD muted>—</TD>
                <TD muted>—</TD>
              </tr>
              ),
            )}
          </tbody>
        </table>
      </div>
    </Section>
    <Section title="Outcome" description="Whether the result was any good — not whether the run finished." reveal={outcome}>
      <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 13.5 }}>
        <span style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: T.subtle }} />
        Not judged
      </span>
    </Section>
  </div>
);

// ------------------------------------------------------------ Settings › Members
// features/settings/MembersPanel.tsx + InviteMemberForm.tsx (Developer roles
// from lib/format.ts DEVELOPER_ROLE_LABELS). People are demo data.
const DEV_ROLE_LABEL: Record<string, string> = { owner: "Developer owner", admin: "Developer admin", developer: "Developer", viewer: "Developer viewer" };

export type TeamMember = { readonly name: string; readonly email: string; readonly applicationRole: string; readonly developerRole: string; readonly state: string };

const Field2: React.FC<{ readonly label: string; readonly value: string; readonly w: number; readonly select?: boolean }> = ({ label, value, w, select }) => (
  <div style={{ width: w }}>
    <div style={{ fontSize: 12, fontWeight: 500, color: T.inkMuted }}>{label}</div>
    <div style={{ marginTop: 6, height: 34, borderRadius: 6, border: `1px solid ${T.line}`, backgroundColor: T.surface, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 10px", fontSize: 13, color: T.ink, boxSizing: "border-box" }}>
      <span>{value}</span>
      {select ? <span style={{ color: T.subtle, fontSize: 11 }}>▾</span> : null}
    </div>
  </div>
);

export const MembersPage: React.FC<{ readonly team: readonly TeamMember[]; readonly arrive: number; readonly press: number; readonly pending: boolean }> = ({ team, arrive, press, pending }) => {
  const invitee = team.find((m) => m.state === "Invited");
  return (
    <div>
      <PageHeader title="Settings" description="Your organization, the people in it, and how this console is configured. API keys moved to Connect — a credential is how something gets in, not an administrative setting." />
      <div style={{ marginTop: 22, fontSize: 13, fontWeight: 600 }}>Members</div>
      <div style={{ marginTop: 10, borderRadius: 8, border: `1px solid ${T.line}`, backgroundColor: T.surface, overflow: "hidden" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ backgroundColor: "rgba(240,238,234,0.6)", borderBottom: `1px solid ${T.line}` }}>
            <tr>
              <TH>Member</TH>
              <TH w={200}>Application role</TH>
              <TH w={200}>Developer access</TH>
              <TH w={130}>Status</TH>
            </tr>
          </thead>
          <tbody>
            {team.map((m) => {
              const isNew = m.state === "Invited";
              if (isNew && arrive <= 0) return null;
              return (
                <tr key={m.email} style={{ borderTop: `1px solid ${T.line}`, opacity: isNew ? arrive : 1, backgroundColor: isNew ? `rgba(240,238,234,${0.7 * arrive})` : "transparent" }}>
                  <td style={{ padding: "11px 14px" }}>
                    <div style={{ fontSize: 13.5 }}>{m.name}</div>
                    <div style={{ marginTop: 2, fontSize: 12, color: T.subtle }}>{m.email}</div>
                  </td>
                  <td style={{ padding: "11px 14px" }}>
                    <span style={{ border: `1px solid ${T.line}`, borderRadius: 4, padding: "2px 8px", fontSize: 12 }}>{m.applicationRole}</span>
                  </td>
                  <td style={{ padding: "11px 14px" }}>
                    <span style={{ border: `1px solid ${T.line}`, borderRadius: 4, padding: "2px 8px", fontSize: 12 }}>{DEV_ROLE_LABEL[m.developerRole] ?? m.developerRole}</span>
                  </td>
                  <td style={{ padding: "11px 14px" }}>
                    {isNew ? <span style={{ backgroundColor: T.cautionSoft, color: T.caution, border: `1px solid ${T.line}`, borderRadius: 4, padding: "2px 8px", fontSize: 12 }}>Invited</span> : <span style={{ fontSize: 13, color: T.inkMuted }}>Active</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {invitee ? (
        <div style={{ marginTop: 16, borderRadius: 8, border: `1px solid ${T.line}`, backgroundColor: T.surface, padding: 16 }}>
          <div style={{ fontSize: 13.5, fontWeight: 500 }}>Add a member</div>
          <div style={{ marginTop: 4, fontSize: 12, lineHeight: 1.5, color: T.subtle }}>
            They get access immediately and appear below as <strong>Invited</strong> until they sign in for the first time. Navis does not send an email — tell them yourself.
          </div>
          <div style={{ marginTop: 12, display: "flex", alignItems: "flex-end", gap: 12 }}>
            <Field2 label="Email" value={invitee.email} w={360} />
            <Field2 label="Application role" value={invitee.applicationRole} w={180} select />
            <Field2 label="Developer access" value={DEV_ROLE_LABEL[invitee.developerRole] ?? invitee.developerRole} w={180} select />
            <div style={{ height: 34, padding: "0 14px", borderRadius: 6, backgroundColor: T.accent, color: "#fff", fontSize: 13, fontWeight: 500, display: "flex", alignItems: "center", scale: String(1 - 0.04 * press) }}>{pending ? "Adding…" : "Add member"}</div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

// ------------------------------------------------------------ Sign up + Personal workspace
// features/auth/SignUpForm.tsx (the workspace choice) and
// features/settings/OrganizationPanel.tsx + lib/format.ts (Personal workspace).
const Choice: React.FC<{ readonly title: string; readonly description: string; readonly selected: number; readonly hover: number }> = ({ title, description, selected, hover }) => (
  <div style={{ flex: 1, borderRadius: 8, border: `1px solid ${selected > 0.5 ? T.ink : hover > 0.5 ? T.inkMuted : T.line}`, backgroundColor: T.surface, padding: "14px 16px", boxShadow: selected > 0 ? `0 0 0 ${selected}px ${T.ink}` : undefined }}>
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <span style={{ width: 14, height: 14, borderRadius: 7, border: `1.5px solid ${selected > 0.5 ? T.ink : T.subtle}`, display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
        <span style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: T.ink, opacity: selected }} />
      </span>
      <span style={{ fontSize: 14, fontWeight: 600 }}>{title}</span>
    </div>
    <div style={{ marginTop: 6, fontSize: 12.5, lineHeight: 1.5, color: T.inkMuted }}>{description}</div>
  </div>
);

export const SignUpChoice: React.FC<{ readonly selectedPersonal: number; readonly hoverPersonal: number; readonly name: string; readonly email: string }> = ({ selectedPersonal, hoverPersonal, name, email }) => (
  <div style={{ width: 620, borderRadius: 14, backgroundColor: T.surface, border: `1px solid ${T.line}`, padding: "26px 28px", fontFamily: FONT.display, color: T.ink, boxShadow: "0 40px 100px -40px rgba(0,0,0,0.5)" }}>
    <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
      <span style={{ fontSize: 15, fontWeight: 600 }}>Navis</span>
      <span style={{ fontSize: 13, color: T.subtle }}>Developer</span>
    </div>
    <div style={{ marginTop: 14, fontSize: 21, fontWeight: 600, letterSpacing: "-0.02em" }}>Create your Navis Developer account</div>
    <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.5, color: T.inkMuted }}>Connect your agents to durable, permission-aware context across sessions and tools.</div>
    <div style={{ marginTop: 16, display: "flex", gap: 12 }}>
      <Choice title="For my organization" description="Build with your team. Invite developers and manage shared agents, access and resources." selected={1 - selectedPersonal} hover={0} />
      <Choice title="For myself" description="Build and experiment on your own. Your workspace is private to you." selected={selectedPersonal} hover={hoverPersonal} />
    </div>
    <div style={{ marginTop: 16, display: "flex", gap: 12 }}>
      <Field2 label="Full name" value={name} w={270} />
      <Field2 label="Email" value={email} w={282} />
    </div>
  </div>
);

export const PersonalWorkspacePanel: React.FC<{ readonly name: string; readonly slug: string; readonly reveal: number }> = ({ name, slug, reveal }) => (
  <div style={{ opacity: reveal }}>
    <PageHeader title="Settings" description="Your organization, the people in it, and how this console is configured." />
    <div style={{ marginTop: 20, borderRadius: 8, border: `1px solid ${T.line}`, backgroundColor: T.surface, padding: "16px 18px" }}>
      <div style={{ fontSize: 14, fontWeight: 600 }}>Organization</div>
      <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "180px 1fr", rowGap: 10, fontSize: 13 }}>
        <span style={{ color: T.subtle }}>Name</span>
        <span>{name}</span>
        <span style={{ color: T.subtle }}>Slug</span>
        <span style={{ fontFamily: FONT.mono, fontSize: 12.5 }}>{slug}</span>
        <span style={{ color: T.subtle }}>Workspace</span>
        <span><span style={{ border: `1px solid ${T.line}`, borderRadius: 4, padding: "2px 8px", fontSize: 12 }}>Personal</span></span>
        <span style={{ color: T.subtle }}>Workspace ownership</span>
        <span><span style={{ border: `1px solid ${T.line}`, borderRadius: 4, padding: "2px 8px", fontSize: 12 }}>Owner</span></span>
        <span style={{ color: T.subtle }}>Developer access</span>
        <span><span style={{ border: `1px solid ${T.line}`, borderRadius: 4, padding: "2px 8px", fontSize: 12 }}>Developer owner</span></span>
      </div>
      <div style={{ marginTop: 12, fontSize: 12, lineHeight: 1.6, color: T.subtle }}>
        You own this workspace and administer it yourself. A personal workspace holds one member, so there are no company roles to assign. To work with colleagues, create a company workspace.
      </div>
    </div>
  </div>
);
