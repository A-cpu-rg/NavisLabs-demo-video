import { FILM, FONT } from "../config/navisBrand";

// The moment a product is named on screen: its name and audience, in the
// film's type, on a quiet pill so it reads over light or dark product UI.

export const ProductReveal: React.FC<{
  readonly name: string;
  readonly audience: string;
  readonly reveal: number;
  readonly tone: "dark" | "light";
  readonly badge?: string;
  readonly style?: React.CSSProperties;
}> = ({ name, audience, reveal, tone, badge, style }) => {
  if (reveal <= 0) return null;
  const dark = tone === "dark";
  return (
    <div
      style={{
        position: "absolute",
        left: 64,
        top: 52,
        opacity: reveal,
        translate: `${(1 - reveal) * -16}px 0`,
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "14px 22px",
        borderRadius: 16,
        backgroundColor: dark ? "rgba(20,19,15,0.9)" : "rgba(247,246,243,0.94)",
        border: `1px solid ${dark ? "rgba(237,235,230,0.12)" : "rgba(28,25,20,0.08)"}`,
        boxShadow: dark ? "0 18px 40px -18px rgba(0,0,0,0.7)" : "0 18px 40px -18px rgba(20,19,15,0.25)",
        ...style,
      }}
    >
      <div style={{ fontFamily: FONT.display, fontSize: 26, fontWeight: 600, letterSpacing: "0.06em", color: dark ? FILM.onInk : FILM.ink, whiteSpace: "nowrap" }}>{name}</div>
      <div style={{ width: 1, height: 22, backgroundColor: dark ? "rgba(237,235,230,0.22)" : "rgba(28,25,20,0.18)" }} />
      <div style={{ fontFamily: FONT.mono, fontSize: 15, letterSpacing: "0.12em", color: dark ? FILM.onInkMuted : FILM.textSubtle, whiteSpace: "nowrap" }}>{audience}</div>
      {badge ? (
        <div style={{ marginLeft: 4, padding: "4px 10px", borderRadius: 999, border: `1px solid ${dark ? "rgba(237,235,230,0.22)" : "rgba(28,25,20,0.16)"}`, fontFamily: FONT.mono, fontSize: 11, letterSpacing: "0.16em", textTransform: "uppercase", color: dark ? FILM.onInkMuted : FILM.textSubtle }}>
          {badge}
        </div>
      ) : null}
    </div>
  );
};

/**
 * The product's name above its window, centred in the top margin — used only
 * while the window is framed small enough to leave that margin, so it never
 * sits on the UI.
 */
export const ProductTag: React.FC<{ readonly name: string; readonly audience: string; readonly reveal: number; readonly tone: "dark" | "light"; readonly badge?: string; readonly top?: number }> = ({ name, audience, reveal, tone, badge, top = 40 }) => {
  if (reveal <= 0) return null;
  const dark = tone === "dark";
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top, display: "flex", justifyContent: "center", opacity: reveal, translate: `0 ${(1 - reveal) * -8}px` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div style={{ fontFamily: FONT.display, fontSize: 24, fontWeight: 600, letterSpacing: "0.08em", color: dark ? FILM.onInk : FILM.ink, whiteSpace: "nowrap" }}>{name}</div>
        <div style={{ width: 1, height: 18, backgroundColor: dark ? "rgba(237,235,230,0.25)" : "rgba(28,25,20,0.2)" }} />
        <div style={{ fontFamily: FONT.mono, fontSize: 14, letterSpacing: "0.12em", color: dark ? FILM.onInkMuted : FILM.textSubtle, whiteSpace: "nowrap" }}>{audience}</div>
        {badge ? <div style={{ padding: "3px 10px", borderRadius: 999, border: `1px solid ${dark ? "rgba(237,235,230,0.22)" : "rgba(28,25,20,0.16)"}`, fontFamily: FONT.mono, fontSize: 11, letterSpacing: "0.16em", textTransform: "uppercase", color: dark ? FILM.onInkMuted : FILM.textSubtle }}>{badge}</div> : null}
      </div>
    </div>
  );
};
