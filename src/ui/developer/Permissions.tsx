import { DEV, FILM, FONT } from "../../config/navisBrand";

// Per-key scope on the MCP server.
//   PermissionPanel -> Devtool/services/mcp-server/src/authorization: every
//     tool call is authorized against the calling key's organization and
//     permissions (a key only ever reads its own organization).
//   AccessDenied    -> authorization/authorize.ts, the exact refusal text.

export const REFUSAL =
  'navis_get_relevant_context requires the "view_memory" permission, which this credential does not hold. Do not retry — the answer will not change. Ask an organization admin to issue a key carrying it.';

type Status = "authorized" | "own-scope" | "restricted" | "denied";

const STATUS: Record<Status, { label: string; color: string }> = {
  authorized: { label: "AUTHORIZED", color: DEV.termGreen },
  "own-scope": { label: "AUTHORIZED · OWN SCOPE", color: DEV.termGreen },
  restricted: { label: "RESTRICTED", color: DEV.termAmber },
  denied: { label: "DENIED", color: DEV.termRed },
};

export const PermissionPanel: React.FC<{
  readonly org: string;
  readonly keyName: string;
  readonly permissions: string;
  readonly status: Status;
  /** 0..1 how far the call has resolved (shows status and result). */
  readonly resolved: number;
  readonly lines: readonly string[];
  readonly width?: number;
  readonly height?: number;
  readonly focus?: number;
}> = ({ org, keyName, permissions, status, resolved, lines, width = 520, height = 420, focus = 0 }) => {
  const s = STATUS[status];
  return (
    <div
      style={{
        width,
        height,
        borderRadius: 16,
        backgroundColor: FILM.inkRaised,
        border: `1px solid rgba(237,235,230,${0.09 + 0.14 * focus})`,
        boxShadow: "0 30px 80px -30px rgba(0,0,0,0.7)",
        padding: "22px 24px",
        fontFamily: FONT.mono,
        color: DEV.termText,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{ fontSize: 12, letterSpacing: "0.16em", color: FILM.onInkMuted }}>{org.toUpperCase()}</div>
      <div style={{ fontFamily: FONT.display, fontSize: 24, fontWeight: 600, marginTop: 6, color: FILM.onInk }}>{keyName}</div>
      <div style={{ fontSize: 13, color: DEV.termDim, marginTop: 6 }}>permissions: {permissions}</div>
      <div style={{ marginTop: 18, fontSize: 14, color: DEV.termMuted }}>
        <span style={{ color: DEV.termGreen }}>⏺</span> navis_get_relevant_context
      </div>
      <div
        style={{
          marginTop: 16,
          opacity: resolved,
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
          padding: "6px 12px",
          borderRadius: 999,
          border: `1px solid ${s.color}55`,
          color: s.color,
          fontSize: 12,
          letterSpacing: "0.14em",
        }}
      >
        <span style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: s.color }} />
        {s.label}
      </div>
      <div style={{ marginTop: 14, opacity: resolved, display: "flex", flexDirection: "column", gap: 8 }}>
        {lines.map((l) => (
          <div key={l} style={{ fontSize: 13.5, lineHeight: 1.45, color: status === "denied" ? DEV.termMuted : DEV.termText }}>
            {l}
          </div>
        ))}
      </div>
    </div>
  );
};

/** The refusal, full frame: an MCP tool error as the agent receives it. */
export const AccessDenied: React.FC<{ readonly reveal: number; readonly keyLine: string }> = ({ reveal, keyLine }) => (
  <div style={{ width: 1360, fontFamily: FONT.mono, color: DEV.termText, opacity: reveal }}>
    <div style={{ fontSize: 15, color: DEV.termDim, letterSpacing: "0.14em" }}>{keyLine}</div>
    <div style={{ display: "flex", gap: 16, marginTop: 22, fontSize: 22 }}>
      <span style={{ color: DEV.termRed }}>⏺</span>
      <span>
        <span style={{ fontWeight: 600 }}>navis - navis_get_relevant_context</span>
        <span style={{ color: DEV.termMuted }}> (MCP)</span>
      </span>
    </div>
    <div style={{ display: "flex", gap: 16, marginTop: 10 }}>
      <span style={{ color: DEV.termDim, fontSize: 22, paddingLeft: 30 }}>⎿</span>
      <div style={{ fontSize: 30, lineHeight: 1.45, color: FILM.onInk }}>
        <span style={{ color: DEV.termRed }}>Error: </span>
        {REFUSAL}
      </div>
    </div>
  </div>
);
