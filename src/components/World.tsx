import { AbsoluteFill, random, useCurrentFrame } from "remotion";
import { assetSrc } from "../config/assets";
import { colors } from "../config/design";

// visual_system.background_treatment: dark = ink with a blue radial lift once
// the line exists; light = canvas with a soft edge falloff; monochrome grain
// on both (2.5% dark, 1.5% light), re-offset every frame.

const GRAIN_TILE = `url("data:image/svg+xml;utf8,${encodeURIComponent(
  `<svg xmlns='http://www.w3.org/2000/svg' width='512' height='512'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix type='saturate' values='0'/></filter><rect width='512' height='512' filter='url(#n)'/></svg>`,
)}")`;

// Asset A08 (a 512 px grain tile) when it exists; until then the same
// texture generated procedurally.
export const Grain: React.FC<{ readonly opacity: number }> = ({ opacity }) => {
  const frame = useCurrentFrame();
  const tile = assetSrc("TEX_GRAIN_A08");
  const x = Math.floor(random(`grain-x-${frame}`) * 512);
  const y = Math.floor(random(`grain-y-${frame}`) * 512);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: tile ? `url("${tile}")` : GRAIN_TILE,
        backgroundSize: "512px 512px",
        backgroundPosition: `${x}px ${y}px`,
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};

type Props = {
  readonly tone: "dark" | "light";
  /** 0..1 strength of the blue radial lift (dark only, after the line exists). */
  readonly lift?: number;
  readonly opacity?: number;
  readonly style?: React.CSSProperties;
};

export const World: React.FC<Props> = ({ tone, lift = 0, opacity = 1, style }) => (
  <AbsoluteFill style={{ opacity, ...style }}>
    {tone === "dark" ? (
      <AbsoluteFill style={{ backgroundColor: colors.ink }}>
        {lift > 0 ? (
          <AbsoluteFill
            style={{
              opacity: lift,
              background:
                "radial-gradient(ellipse 70% 60% at 50% 115%, rgba(25,118,254,0.08), rgba(25,118,254,0) 100%)",
            }}
          />
        ) : null}
      </AbsoluteFill>
    ) : (
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at center, ${colors.canvas} 85%, #EFECE6 100%)`,
        }}
      />
    )}
    <Grain opacity={tone === "dark" ? 0.025 : 0.015} />
  </AbsoluteFill>
);
