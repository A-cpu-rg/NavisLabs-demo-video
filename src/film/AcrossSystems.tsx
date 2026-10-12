import { interpolate } from "remotion";
import { BEAT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { APP, FONT } from "../config/navisBrand";
import { ACROSS_SYSTEMS, EVENT_FACT } from "../ui/demoContent";
import { BrandIcon } from "../ui/Integrations";
import { CLAMP, easeOut } from "../ui/kit";

// S09, after "Then the company acts." — the same organizational event as the
// company's other systems hold it (demo data). Upcoming integrations are labelled
// "upcoming" (demo configuration): nothing is shown executed through them.
// Navis does not update those systems itself: each row says what the system
// shows and who owns the next step. The GitHub row is the bridge to Navis
// Developer, where the agent makes that change.

const r = (T: number, a: number, b: number) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: easeOut });

const STATUS: Record<(typeof ACROSS_SYSTEMS)[number]["status"], { label: string; color: string; bg: string }> = {
  done: { label: "Done", color: "#047857", bg: "#ECFDF5" },
  next: { label: "Next", color: "#B45309", bg: "#FFFBEB" },
  related: { label: "Related", color: "#4B5563", bg: "#F3F4F6" },
};

export const AcrossSystems: React.FC<{ readonly T: number; readonly x: number; readonly y: number; readonly w?: number }> = ({ T, x, y, w = 520 }) => {
  const panel = r(T, BEAT.acrossIn, BEAT.acrossIn + 0.3);
  if (panel <= 0) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: w,
        opacity: panel,
        translate: `${(1 - panel) * 18}px 0`,
        borderRadius: 16,
        backgroundColor: "#FFFFFF",
        boxShadow: "0 24px 60px -28px rgba(20,19,15,0.35), inset 0 0 0 1px rgba(28,25,20,0.08)",
        padding: "20px 22px",
        boxSizing: "border-box",
        fontFamily: FONT.app,
      }}
    >
      <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: "0.2em", textTransform: "uppercase", color: APP.gray500 }}>{copy("acrossSystems")}</div>
      <div style={{ marginTop: 8, fontSize: 17, fontWeight: 600, color: "#111827" }}>{EVENT_FACT}</div>
      <div style={{ marginTop: 14, display: "flex", flexDirection: "column" }}>
        {ACROSS_SYSTEMS.map((row, i) => {
          const a = r(T, BEAT.acrossIn + 0.15 + i * 0.12, BEAT.acrossIn + 0.4 + i * 0.12);
          const st = STATUS[row.status];
          return (
            <div key={row.id} style={{ opacity: a, translate: `0 ${(1 - a) * 6}px`, display: "grid", gridTemplateColumns: "22px 92px 1fr auto", alignItems: "center", gap: 10, padding: "10px 0", borderTop: "1px solid #F1F1EF" }}>
              <BrandIcon id={row.id} height={row.id === "salesforce" ? 12 : 16} />
              <span style={{ fontSize: 13.5, fontWeight: 600, color: "#111827" }}>
                {row.system}
                {row.upcoming ? <span style={{ display: "block", fontSize: 10.5, fontWeight: 500, letterSpacing: "0.04em", color: APP.gray400 }}>upcoming</span> : null}
              </span>
              <span style={{ fontSize: 13, lineHeight: 1.35, color: APP.gray700 }}>
                {row.state}
                <span style={{ display: "block", fontSize: 11.5, color: APP.gray400 }}>{row.owner}</span>
              </span>
              <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.04em", color: st.color, backgroundColor: st.bg, borderRadius: 999, padding: "3px 9px" }}>{st.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
