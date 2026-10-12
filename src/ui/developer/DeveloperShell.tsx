import { AbsoluteFill } from "remotion";
import { DEV, FILM, FONT } from "../../config/navisBrand";
import { Grain } from "../../components/World";
import { TrafficLights } from "../../components/TrafficLights";

// The dark world Navis Developer lives in: the developer's terminal, where an
// AI agent (Claude Code) runs. Evidence: Devtool/packages/cli (the `navis`
// CLI and its Claude Code hooks) is a terminal product; the console palette
// is Devtool/apps/dashboard/src/app/globals.css.

export const DeveloperShell: React.FC<{
  readonly children: React.ReactNode;
  /** 0..1 strength of the faint cobalt floor light (only once the line exists). */
  readonly lift?: number;
  readonly style?: React.CSSProperties;
}> = ({ children, lift = 0.6, style }) => (
  <AbsoluteFill style={{ backgroundColor: FILM.ink, ...style }}>
    <AbsoluteFill
      style={{
        opacity: 0.18 * lift,
        background: "radial-gradient(ellipse 80% 55% at 50% 120%, rgba(25,118,254,0.10), rgba(25,118,254,0) 70%)",
      }}
    />
    <AbsoluteFill
      style={{
        opacity: 0.3,
        backgroundImage:
          "linear-gradient(rgba(237,235,230,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(237,235,230,0.025) 1px, transparent 1px)",
        backgroundSize: "64px 64px",
        maskImage: "radial-gradient(ellipse 70% 70% at 50% 50%, black 30%, transparent 85%)",
      }}
    />
    {children}
    <Grain opacity={0.025} />
  </AbsoluteFill>
);

/** A terminal window: macOS chrome, mono title, ink body. Sized in world px. */
export const TerminalWindow: React.FC<{
  readonly width: number;
  readonly height: number;
  readonly title: string;
  readonly children: React.ReactNode;
  /** 0 = live, 1 = session closed (dimmed). */
  readonly dim?: number;
  readonly style?: React.CSSProperties;
}> = ({ width, height, title, children, dim = 0, style }) => (
  <div
    style={{
      position: "absolute",
      left: -width / 2,
      top: -height / 2,
      width,
      height,
      borderRadius: 14,
      backgroundColor: DEV.termRaised,
      boxShadow: "0 0 0 1px rgba(237,235,230,0.09), 0 40px 120px -20px rgba(0,0,0,0.65), 0 12px 40px -12px rgba(0,0,0,0.5)",
      overflow: "hidden",
      ...style,
    }}
  >
    <div
      style={{
        height: 38,
        display: "flex",
        alignItems: "center",
        padding: "0 16px",
        borderBottom: "1px solid rgba(237,235,230,0.06)",
        backgroundColor: "#1F1E1A",
        position: "relative",
      }}
    >
      <TrafficLights />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: FONT.mono,
          fontSize: 13,
          color: DEV.termDim,
          letterSpacing: "0.02em",
        }}
      >
        {title}
      </div>
    </div>
    <div
      style={{
        position: "absolute",
        inset: "38px 0 0 0",
        padding: "22px 30px",
        fontFamily: FONT.mono,
        fontSize: 15,
        lineHeight: 1.6,
        color: DEV.termText,
        overflow: "hidden",
      }}
    >
      {children}
    </div>
    {dim > 0 ? <div style={{ position: "absolute", inset: 0, backgroundColor: FILM.ink, opacity: dim * 0.72 }} /> : null}
  </div>
);
