import { Img, staticFile } from "remotion";
import { BRAND, FILM, FONT } from "../config/navisBrand";
import { Cursor } from "../components/Cursor";

// Film-level typography and brand pieces shared by the scenes. UI text lives
// in src/ui; this is the film's own voice (labels, product names, lockup).

/** Mono uppercase label, the film's caption style. */
export const FilmLabel: React.FC<{
  readonly children: React.ReactNode;
  readonly size?: number;
  readonly color?: string;
  readonly tracking?: number;
  readonly opacity?: number;
  readonly style?: React.CSSProperties;
}> = ({ children, size = 18, color = FILM.onInkMuted, tracking = 0.22, opacity = 1, style }) => (
  <div
    style={{
      fontFamily: FONT.mono,
      fontSize: size,
      letterSpacing: `${tracking}em`,
      textTransform: "uppercase",
      color,
      opacity,
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {children}
  </div>
);

/** A product name with its audience: "NAVIS DEVELOPER" / "FOR AGENTS". */
export const ProductTitle: React.FC<{
  readonly name: string;
  readonly audience: string;
  readonly tone: "dark" | "light";
  readonly size?: number;
  readonly reveal?: number;
  readonly align?: "left" | "center" | "right";
}> = ({ name, audience, tone, size = 44, reveal = 1, align = "center" }) => (
  <div style={{ textAlign: align, opacity: reveal, translate: `0 ${(1 - reveal) * 12}px` }}>
    <div
      style={{
        fontFamily: FONT.display,
        fontSize: size,
        fontWeight: 600,
        letterSpacing: "0.06em",
        color: tone === "dark" ? FILM.onInk : FILM.ink,
        whiteSpace: "nowrap",
      }}
    >
      {name}
    </div>
    <FilmLabel size={Math.round(size * 0.36)} color={tone === "dark" ? FILM.onInkMuted : FILM.textSubtle} style={{ marginTop: size * 0.32 }}>
      {audience}
    </FilmLabel>
  </div>
);

/**
 * The NavisLabs lockup: the real mark (navis-logo.png artwork, cut out of its
 * black tile — no tile, no pill, no halo) + "NavisLabs" in Geist Sans
 * semibold, 0.01em tracking, as the website's wordmark.tsx sets it. `size` is
 * the mark's box; the wordmark is 0.6 of it.
 */
export const NavisMark: React.FC<{ readonly size: number; readonly tone?: "dark" | "light"; readonly opacity?: number; readonly style?: React.CSSProperties }> = ({ size, tone = "dark", opacity = 1, style }) => (
  <Img src={staticFile(tone === "dark" ? BRAND.mark.dark : BRAND.mark.light)} style={{ width: size, height: size, display: "block", opacity, flexShrink: 0, ...style }} />
);

export const Lockup: React.FC<{
  readonly size: number;
  readonly tone?: "dark" | "light";
  /** 0..1: mark in, then the wordmark. */
  readonly tile?: number;
  readonly word?: number;
  /** Kept for call sites; the identity has no glow. */
  readonly glow?: number;
  /** false draws the mark alone. */
  readonly showWord?: boolean;
}> = ({ size, tone = "dark", tile = 1, word = 1, showWord = true }) => (
  <div style={{ display: "flex", alignItems: "center", gap: size * 0.3 }}>
    <div style={{ opacity: tile, scale: String(0.96 + 0.04 * tile) }}>
      <NavisMark size={size} tone={tone} />
    </div>
    {showWord ? (
      <div
        style={{
          fontFamily: FONT.display,
          fontWeight: 600,
          fontSize: size * 0.6,
          letterSpacing: "0.01em",
          color: tone === "dark" ? "#FFFFFF" : FILM.ink,
          opacity: word,
          translate: `${(1 - word) * -8}px 0`,
          whiteSpace: "nowrap",
        }}
      >
        {BRAND.company}
      </div>
    ) : null}
  </div>
);

/** DAY 1 / DAY 2 tag. */
export const DayTag: React.FC<{ readonly label: string; readonly opacity: number; readonly style?: React.CSSProperties }> = ({ label, opacity, style }) => (
  <div
    style={{
      position: "absolute",
      left: 56,
      top: 44,
      opacity,
      padding: "10px 18px 10px 20px",
      borderRadius: 999,
      backgroundColor: "rgba(20,19,15,0.88)",
      border: "1px solid rgba(237,235,230,0.14)",
      boxShadow: "0 10px 30px -10px rgba(0,0,0,0.6)",
      ...style,
    }}
  >
    <FilmLabel size={18} color={FILM.onInk} tracking={0.3}>
      {label}
    </FilmLabel>
  </div>
);

/** Which product we are looking at, top-right, quiet. */
export const CornerProduct: React.FC<{ readonly name: string; readonly tone: "dark" | "light"; readonly opacity: number }> = ({ name, tone, opacity }) => (
  <div
    style={{
      position: "absolute",
      right: 56,
      top: 44,
      opacity,
      padding: "11px 18px",
      borderRadius: 999,
      backgroundColor: tone === "dark" ? "rgba(20,19,15,0.88)" : "rgba(247,246,243,0.9)",
      border: `1px solid ${tone === "dark" ? "rgba(237,235,230,0.1)" : "rgba(28,25,20,0.08)"}`,
    }}
  >
    <FilmLabel size={16} tracking={0.26} color={tone === "dark" ? FILM.onInkMuted : FILM.textSubtle}>
      {name}
    </FilmLabel>
  </div>
);

/** The pointer at UI scale inside a camera world (the arrow is 23x32 at 1x). */
export const UiCursor: React.FC<{
  readonly x: number;
  readonly y: number;
  readonly clickFrames?: readonly number[];
  readonly opacity?: number;
  readonly scale?: number;
  /** Absolute frame for click timing when clickFrames are absolute. */
  readonly frameOverride?: number;
}> = ({ x, y, clickFrames, opacity = 1, scale = 0.72, frameOverride }) => (
  <div style={{ position: "absolute", left: x, top: y, width: 0, height: 0, scale: String(scale), transformOrigin: "0 0" }}>
    <Cursor x={0} y={0} clickFrames={clickFrames} tone="light" opacity={opacity} frame={frameOverride} />
  </div>
);

/** Point on a gentle arc between two points (cursor travel), t in 0..1. */
export const arcPoint = (a: { x: number; y: number }, b: { x: number; y: number }, t: number, bend = 0.18) => {
  const mx = (a.x + b.x) / 2;
  const my = (a.y + b.y) / 2;
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const cx = mx - dy * bend;
  const cy = my + dx * bend;
  const u = 1 - t;
  return { x: u * u * a.x + 2 * u * t * cx + t * t * b.x, y: u * u * a.y + 2 * u * t * cy + t * t * b.y };
};
