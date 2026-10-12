import { useId } from "react";
import { interpolateColors } from "remotion";

// The Navis line: the only element that glows (visual_system.glow: 2 px core
// #1976FE + 0 0 24px rgba(25,118,254,0.45)). One component draws every state
// in the film — neutral, ignited, drawn on, trimmed, dashed, bent — so it
// always reads as the same physical line.

export type Pt = { x: number; y: number };

export const linePath = (a: Pt, b: Pt) => `M ${a.x} ${a.y} L ${b.x} ${b.y}`;

const toPath = (pts: readonly Pt[]) =>
  pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(" ");

/** Points along a straight segment. */
export const sampleLine = (a: Pt, b: Pt, n: number): Pt[] =>
  Array.from({ length: n + 1 }, (_, i) => ({ x: a.x + ((b.x - a.x) * i) / n, y: a.y + ((b.y - a.y) * i) / n }));

/** Points along a circular arc; angles in degrees, 0 = right, clockwise positive (screen space). */
export const sampleArc = (c: Pt, r: number, fromDeg: number, toDeg: number, n: number): Pt[] =>
  Array.from({ length: n + 1 }, (_, i) => {
    const a = ((fromDeg + ((toDeg - fromDeg) * i) / n) * Math.PI) / 180;
    return { x: c.x + r * Math.cos(a), y: c.y + r * Math.sin(a) };
  });

/** Morphs one point list into another of the same length (the line 'bending'). */
export const morphPath = (from: readonly Pt[], to: readonly Pt[], t: number) =>
  toPath(from.map((p, i) => ({ x: p.x + (to[i].x - p.x) * t, y: p.y + (to[i].y - p.y) * t })));

export const pointsPath = toPath;

const NEUTRAL = "rgba(237,235,230,0.4)";
const BLUE = "rgba(25,118,254,1)";

type Props = {
  readonly d: string;
  /** 0 = the neutral line of S03/S04, 1 = Navis blue with glow. */
  readonly ignite?: number;
  /** Visible portion along the path, 0..1. */
  readonly trim?: readonly [number, number];
  readonly dashed?: readonly [number, number];
  readonly width?: number;
  readonly color?: string;
  readonly opacity?: number;
  /** World-space box the SVG covers (paths are drawn in world coordinates). */
  readonly bounds?: { x: number; y: number; w: number; h: number };
};

export const NavisLine: React.FC<Props> = ({
  d,
  ignite = 1,
  trim = [0, 1],
  dashed,
  width,
  color,
  opacity = 1,
  bounds = { x: -1400, y: -900, w: 2800, h: 1800 },
}) => {
  const maskId = `navis-line-${useId().replace(/[^a-zA-Z0-9_-]/g, "")}`;
  const stroke = color ?? interpolateColors(ignite, [0, 1], [NEUTRAL, BLUE]);
  const strokeWidth = Math.min(width ?? 1 + ignite, 1.6);
  const [t0, t1] = trim;
  const visible = Math.max(0, t1 - t0);
  if (visible <= 0 || opacity <= 0) return null;
  const glow = ignite > 0 && !color ? `drop-shadow(0 0 3px rgba(25,118,254,${0.22 * ignite}))` : undefined;

  return (
    <svg
      width={bounds.w}
      height={bounds.h}
      viewBox={`${bounds.x} ${bounds.y} ${bounds.w} ${bounds.h}`}
      style={{ position: "absolute", left: bounds.x, top: bounds.y, overflow: "visible", opacity, filter: glow, pointerEvents: "none" }}
    >
      {dashed ? (
        <>
          <defs>
            <mask id={maskId} maskUnits="userSpaceOnUse" x={bounds.x} y={bounds.y} width={bounds.w} height={bounds.h}>
              <path d={d} pathLength={1} fill="none" stroke="white" strokeWidth={strokeWidth + 8}
                strokeDasharray={`${visible} 2`} strokeDashoffset={-t0} />
            </mask>
          </defs>
          <path d={d} fill="none" stroke={stroke} strokeWidth={strokeWidth} strokeLinecap="round"
            strokeDasharray={`${dashed[0]} ${dashed[1]}`} mask={`url(#${maskId})`} />
        </>
      ) : (
        <path d={d} pathLength={1} fill="none" stroke={stroke} strokeWidth={strokeWidth} strokeLinecap="round"
          strokeDasharray={`${visible} 2`} strokeDashoffset={-t0} />
      )}
    </svg>
  );
};
