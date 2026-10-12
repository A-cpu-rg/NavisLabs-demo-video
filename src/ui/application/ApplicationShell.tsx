import { APP, FONT } from "../../config/navisBrand";
import { TrafficLights } from "../../components/TrafficLights";
import { Icon } from "../kit";

// The Navis App frame: a browser window (blank address pill — no
// URL is claimed) holding the real desktop layout.
//   Sidebar -> Navis-AI/src/components/layout/Sidebar.tsx (w-[280px], brand
//     tile "N" + NAVIS_BRAND_NAME/TAGLINE from lib/navigation.ts, groups
//     Intelligence/Organization/Work/Observe, active row bg-black text-white,
//     WaitingIndicator amber chip, "Connections" strip "n/n active").

export const APP_WINDOW = { width: 1440, height: 900, titlebar: 44, sidebar: 280 } as const;

type NavRow = { id: string; label: string; icon: keyof typeof Icon; meta?: string };
const GROUPS: readonly { label: string; rows: readonly NavRow[] }[] = [
  {
    label: "Intelligence",
    rows: [
      { id: "today", label: "Today", icon: "Sparkles" },
      { id: "ask", label: "Ask Navis", icon: "Messages", meta: "ask about your organization" },
    ],
  },
  {
    label: "Organization",
    rows: [
      { id: "people", label: "People", icon: "Users" },
      { id: "projects", label: "Projects", icon: "Layers" },
      { id: "customers", label: "Customers", icon: "Building" },
    ],
  },
  {
    label: "Work",
    rows: [
      { id: "decisions", label: "Decisions", icon: "History" },
      { id: "governance", label: "Governance", icon: "Shield" },
      { id: "actions", label: "Actions", icon: "Scroll" },
    ],
  },
  { label: "Observe", rows: [{ id: "whats-changed", label: "What's Changed", icon: "Activity", meta: "since your last visit" }] },
];

export const Sidebar: React.FC<{ readonly waiting: number; readonly user: string; readonly email: string }> = ({ waiting, user, email }) => (
  <div
    style={{
      position: "absolute",
      left: 0,
      top: 0,
      bottom: 0,
      width: APP_WINDOW.sidebar,
      backgroundColor: "#FFFFFF",
      borderRight: `1px solid ${APP.gray100}`,
      display: "flex",
      flexDirection: "column",
      fontFamily: FONT.app,
    }}
  >
    <div style={{ padding: 16, borderBottom: `1px solid ${APP.gray100}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{ width: 36, height: 36, borderRadius: 12, backgroundColor: "#000", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, fontWeight: 600 }}>N</div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#000", lineHeight: 1.2 }}>Navis</div>
          <div style={{ fontSize: 10.5, color: APP.gray500, lineHeight: 1.2 }}>Organizational Intelligence</div>
        </div>
      </div>
      {waiting > 0 ? (
        <div
          style={{
            marginTop: 12,
            display: "flex",
            alignItems: "center",
            gap: 8,
            borderRadius: 12,
            backgroundColor: APP.amber50,
            boxShadow: `inset 0 0 0 1px ${APP.amber200}`,
            padding: "8px 12px",
            fontSize: 12,
            color: APP.amber800,
          }}
        >
          <Icon.Users size={12} />
          {waiting} teammate{waiting === 1 ? "" : "s"} waiting on you
        </div>
      ) : null}
    </div>
    <div style={{ flex: 1, padding: 12 }}>
      {GROUPS.map((g, gi) => (
        <div key={g.label} style={{ marginTop: gi === 0 ? 0 : 16 }}>
          <div style={{ padding: "0 10px", fontSize: 9.5, fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray400 }}>{g.label}</div>
          <div style={{ marginTop: 4, display: "flex", flexDirection: "column", gap: 2 }}>
            {g.rows.map((row) => {
              const active = row.id === "today";
              const Glyph = Icon[row.icon];
              return (
                <div
                  key={row.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    borderRadius: 12,
                    padding: "8px 10px",
                    fontSize: 14,
                    backgroundColor: active ? "#000" : "transparent",
                    color: active ? "#fff" : APP.gray700,
                    boxShadow: active ? "0 1px 2px rgba(0,0,0,0.15)" : undefined,
                  }}
                >
                  <Glyph size={15} color={active ? "#fff" : APP.gray500} />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 500, lineHeight: 1.2 }}>{row.label}</div>
                    {row.meta ? <div style={{ fontSize: 10.5, color: active ? "rgba(255,255,255,0.7)" : APP.gray400, marginTop: 2 }}>{row.meta}</div> : null}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
    <div style={{ borderTop: `1px solid ${APP.gray100}`, padding: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 10px" }}>
        <div style={{ display: "flex", gap: 6 }}>
          {[0, 1, 2].map((i) => (
            <div key={i} style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: "#10B981", boxShadow: "0 0 0 3px rgba(16,185,129,0.15)" }} />
          ))}
        </div>
        <div>
          <div style={{ fontSize: 10.5, fontWeight: 500, color: APP.gray700 }}>Connections</div>
          <div style={{ fontFamily: FONT.mono, fontSize: 9.5, color: APP.gray400 }}>3/3 active</div>
        </div>
      </div>
    </div>
    <div style={{ borderTop: `1px solid ${APP.gray100}`, padding: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: 6 }}>
        <div style={{ width: 32, height: 32, borderRadius: 16, background: "linear-gradient(135deg, #111827, #000)", color: "#fff", fontSize: 11, fontWeight: 600, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {user.charAt(0)}
        </div>
        <div>
          <div style={{ fontSize: 12.5, fontWeight: 500, color: "#000" }}>{user}</div>
          <div style={{ fontSize: 10.5, color: APP.gray500 }}>{email}</div>
        </div>
      </div>
    </div>
  </div>
);

/** Browser window + sidebar + the scrolling main column. Centered on the world origin. */
export const ApplicationShell: React.FC<{
  readonly children: React.ReactNode;
  readonly overlay?: React.ReactNode;
  readonly waiting: number;
  readonly user: string;
  readonly email: string;
  readonly scroll?: number;
  readonly style?: React.CSSProperties;
}> = ({ children, overlay, waiting, user, email, scroll = 0, style }) => {
  const { width, height, titlebar, sidebar } = APP_WINDOW;
  return (
    <div
      style={{
        position: "absolute",
        left: -width / 2,
        top: -(height + titlebar) / 2,
        width,
        height: height + titlebar,
        borderRadius: 14,
        overflow: "hidden",
        backgroundColor: APP.bg,
        fontFamily: FONT.app,
        color: APP.text,
        boxShadow: "0 0 0 1px rgba(20,19,15,0.08), 0 50px 120px -30px rgba(20,19,15,0.35), 0 18px 40px -18px rgba(20,19,15,0.25)",
        ...style,
      }}
    >
      <div
        style={{
          height: titlebar,
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          backgroundColor: "#F3F1EC",
          borderBottom: "1px solid rgba(20,19,15,0.07)",
          position: "relative",
        }}
      >
        <TrafficLights />
        <div
          style={{
            position: "absolute",
            left: "50%",
            translate: "-50% 0",
            width: 420,
            height: 26,
            borderRadius: 8,
            backgroundColor: "rgba(20,19,15,0.055)",
          }}
        />
      </div>
      <div style={{ position: "absolute", top: titlebar, left: 0, right: 0, bottom: 0, overflow: "hidden" }}>
        <Sidebar waiting={waiting} user={user} email={email} />
        <div style={{ position: "absolute", left: sidebar, right: 0, top: 0, bottom: 0, overflow: "hidden" }}>
          <div style={{ translate: `0 ${-scroll}px`, padding: "40px 48px 80px", fontFamily: FONT.app }}>
            <div style={{ maxWidth: 768, margin: "0 auto" }}>{children}</div>
          </div>
        </div>
        {overlay}
      </div>
    </div>
  );
};
