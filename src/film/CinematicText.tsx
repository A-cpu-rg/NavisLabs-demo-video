import { FILM, FONT } from "../config/navisBrand";

// Editorial type for the film's own statements: one short line, large, with
// generous negative space. Reveal is a fade with a small rise; no per-letter
// effects.

export const CinematicText: React.FC<{
  readonly text: string;
  readonly reveal: number;
  readonly exit?: number;
  readonly size?: number;
  readonly tone?: "dark" | "light";
  readonly weight?: number;
  readonly mono?: boolean;
  readonly muted?: boolean;
  readonly style?: React.CSSProperties;
}> = ({ text, reveal, exit = 0, size = 64, tone = "dark", weight = 500, mono = false, muted = false, style }) => {
  const o = reveal * (1 - exit);
  if (o <= 0) return null;
  const color = tone === "dark" ? (muted ? FILM.onInkMuted : FILM.onInk) : muted ? FILM.textSubtle : FILM.ink;
  return (
    <div
      style={{
        opacity: o,
        translate: `0 ${(1 - reveal) * 14 - exit * 8}px`,
        filter: reveal < 1 ? `blur(${(1 - reveal) * 6}px)` : undefined,
        fontFamily: mono ? FONT.mono : FONT.display,
        fontSize: size,
        fontWeight: weight,
        letterSpacing: mono ? "0.2em" : "-0.015em",
        textTransform: mono ? "uppercase" : "none",
        lineHeight: 1.15,
        color,
        textAlign: "center",
        whiteSpace: "nowrap",
        ...style,
      }}
    >
      {text}
    </div>
  );
};
