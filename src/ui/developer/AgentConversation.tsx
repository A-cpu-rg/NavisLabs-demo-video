import { DEV, FONT } from "../../config/navisBrand";

// The agent session as Claude Code prints it in a terminal: the developer's
// prompt, "⏺" tool calls with "⎿" results, and the agent's replies. These are
// the agent's surface, not a Navis screen; Navis Developer appears only where
// the real product does (the `navis` CLI, the SessionStart restoration block,
// and the navis_get_relevant_context MCP tool).

export type Reveal = { readonly opacity?: number; readonly y?: number };

const reveal = (r?: Reveal): React.CSSProperties => ({
  opacity: r?.opacity ?? 1,
  translate: `0 ${r?.y ?? 0}px`,
});

/** zsh prompt line: `user@host NavisLabs % claude` (or a bare `repo %`). */
export const ShellLine: React.FC<{ readonly repo: string; readonly command: string; readonly user?: string; readonly reveal?: Reveal }> = ({ repo, command, user, reveal: r }) => (
  <div style={{ ...reveal(r), color: DEV.termMuted }}>
    {user ? <span style={{ color: DEV.termMuted }}>{user} </span> : null}
    <span style={{ color: DEV.termGreen }}>{repo}</span> <span style={{ color: DEV.termDim }}>%</span>{" "}
    <span style={{ color: DEV.termText }}>{command}</span>
  </div>
);

/** A submitted prompt, as it stays in the scrollback. */
export const UserTurn: React.FC<{ readonly text: string; readonly reveal?: Reveal }> = ({ text, reveal: r }) => (
  <div style={{ ...reveal(r), display: "flex", gap: 12, color: DEV.termMuted, margin: "6px 0 10px" }}>
    <span style={{ color: DEV.termDim }}>&gt;</span>
    <span style={{ color: "#D6D3CC" }}>{text}</span>
  </div>
);

/** The live input box with a caret while the developer types. */
export const PromptInput: React.FC<{
  readonly text: string;
  readonly caret: boolean;
  readonly placeholder?: string;
  readonly reveal?: Reveal;
  readonly highlight?: number;
}> = ({ text, caret, placeholder, reveal: r, highlight = 0 }) => (
  <div
    style={{
      ...reveal(r),
      marginTop: 14,
      border: `1px solid rgba(237,235,230,${0.16 + highlight * 0.2})`,
      borderRadius: 10,
      padding: "10px 14px",
      display: "flex",
      gap: 12,
      minHeight: 24,
    }}
  >
    <span style={{ color: DEV.termMuted }}>&gt;</span>
    <span style={{ color: text ? DEV.termText : DEV.termDim, whiteSpace: "pre-wrap" }}>
      {text || (caret ? "" : placeholder)}
      <span
        style={{
          display: "inline-block",
          width: 9,
          height: 19,
          marginLeft: 1,
          translate: "0 4px",
          backgroundColor: caret ? DEV.termText : "transparent",
        }}
      />
    </span>
  </div>
);

/** `⏺ Tool(args)` with `⎿` result lines underneath. */
export const ToolCall: React.FC<{
  readonly name: string;
  readonly args: React.ReactNode;
  readonly status?: "running" | "ok" | "error";
  readonly children?: React.ReactNode;
  readonly reveal?: Reveal;
}> = ({ name, args, status = "ok", children, reveal: r }) => (
  <div style={{ ...reveal(r), margin: "8px 0" }}>
    <div style={{ display: "flex", gap: 12 }}>
      <span style={{ color: status === "error" ? DEV.termRed : status === "running" ? DEV.termDim : DEV.termGreen }}>⏺</span>
      <span>
        <span style={{ fontWeight: 600, color: DEV.termText }}>{name}</span>
        <span style={{ color: DEV.termMuted }}>(</span>
        <span style={{ color: DEV.termMuted }}>{args}</span>
        <span style={{ color: DEV.termMuted }}>)</span>
      </span>
    </div>
    {children ? (
      <div style={{ display: "flex", gap: 12, marginTop: 2 }}>
        <span style={{ color: DEV.termDim, paddingLeft: 22 }}>⎿</span>
        <div style={{ flex: 1, minWidth: 0 }}>{children}</div>
      </div>
    ) : null}
  </div>
);

/** `⏺ text` — the agent speaking. */
export const AgentText: React.FC<{ readonly children: React.ReactNode; readonly reveal?: Reveal }> = ({ children, reveal: r }) => (
  <div style={{ ...reveal(r), display: "flex", gap: 12, margin: "8px 0" }}>
    <span style={{ color: DEV.termText }}>⏺</span>
    <span style={{ color: DEV.termText, fontFamily: FONT.mono }}>{children}</span>
  </div>
);

/** Vertical stack of conversation blocks, scrolled by `scroll` px. */
export const AgentConversation: React.FC<{ readonly children: React.ReactNode; readonly scroll?: number }> = ({ children, scroll = 0 }) => (
  <div style={{ translate: `0 ${-scroll}px` }}>{children}</div>
);
