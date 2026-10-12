import { createContext, useContext } from "react";
import { colors, fontStack } from "../config/design";

// Film modes:
//   development  HUD with scene, time and which audio tier is playing.
//   preview      clean picture (no HUD); temp audio allowed. Default for renders.
//   final        clean picture; refuses to render until every voice line and
//                the score are FINAL files (see src/config/audioMap.ts).
export type FilmMode = "development" | "preview" | "final";

const DevModeContext = createContext<FilmMode>("development");
export const DevModeProvider = DevModeContext.Provider;
export const useIsDev = () => useContext(DevModeContext) === "development";

/** Small mono tag used by every development label. */
export const DevLabel: React.FC<{
  readonly children: React.ReactNode;
  readonly tone?: "dark" | "light";
  readonly style?: React.CSSProperties;
}> = ({ children, tone = "dark", style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      padding: "6px 12px",
      borderRadius: 999,
      fontFamily: fontStack("Geist Mono"),
      fontSize: 13,
      letterSpacing: "0.14em",
      textTransform: "uppercase",
      whiteSpace: "nowrap",
      color: tone === "dark" ? colors.on_ink_muted : colors.text_subtle,
      border: `1px dashed ${tone === "dark" ? "rgba(237,235,230,0.28)" : colors.line_strong}`,
      backgroundColor: tone === "dark" ? "rgba(20,19,15,0.6)" : "rgba(247,246,243,0.7)",
      ...style,
    }}
  >
    <span
      style={{
        width: 6,
        height: 6,
        borderRadius: 3,
        backgroundColor: tone === "dark" ? "rgba(237,235,230,0.5)" : colors.text_subtle,
      }}
    />
    {children}
  </div>
);

/** World-space crosshair marking where the camera will focus in real footage. */
export const FocusMarker: React.FC<{
  readonly x: number;
  readonly y: number;
  readonly label: string;
  readonly tone: "dark" | "light";
}> = ({ x, y, label, tone }) => {
  const stroke = tone === "dark" ? "rgba(237,235,230,0.32)" : "rgba(28,25,20,0.3)";
  return (
    <div style={{ position: "absolute", left: x, top: y, pointerEvents: "none" }}>
      <div
        style={{
          position: "absolute",
          left: -18,
          top: -18,
          width: 36,
          height: 36,
          borderRadius: 18,
          border: `1px dashed ${stroke}`,
        }}
      />
      <div style={{ position: "absolute", left: -26, top: 0, width: 52, height: 1, backgroundColor: stroke }} />
      <div style={{ position: "absolute", left: 0, top: -26, width: 1, height: 52, backgroundColor: stroke }} />
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 34,
          translate: "-50% 0",
          fontFamily: fontStack("Geist Mono"),
          fontSize: 12,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          whiteSpace: "nowrap",
          color: stroke,
        }}
      >
        focus · {label}
      </div>
    </div>
  );
};
