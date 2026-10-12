import { Easing, interpolate, useCurrentFrame } from "remotion";
import { sec } from "../config/beats";
import { endFrame, filmScene, startFrame } from "../config/timeline";
import type { SceneId } from "../config/types";

// Small helpers shared by the reconstructed UI and the scenes.

export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const easeOut = Easing.bezier(0.22, 1, 0.36, 1);
export const easeInOut = Easing.bezier(0.65, 0, 0.35, 1);

/** 0..1 between two frames, clamped, eased. */
export const ramp = (frame: number, from: number, to: number, easing: (t: number) => number = easeOut) =>
  interpolate(frame, [from, to], [0, 1], { ...CLAMP, easing });

/**
 * Scene-local clock. Beats are absolute seconds; `at(s)` turns one into this
 * scene's local frame, and `t` is the local frame now.
 */
export const useSceneClock = (sceneId: SceneId) => {
  const t = useCurrentFrame();
  const scene = filmScene(sceneId);
  const start = startFrame(scene);
  const at = (s: number) => sec(s) - start;
  const r = (from: number, to: number, easing?: (x: number) => number) => ramp(t, at(from), at(to), easing);
  /** Absolute film time in seconds. */
  const T = (start + t) / 30;
  /** The scene's nominal end in absolute seconds (hold keyframes are written against it). */
  const end = scene.to;
  return { t, at, r, T, end, length: endFrame(scene) - start };
};

/** Characters of `text` typed by local frame `t` when typing starts at `start` (frames). */
export const typedCount = (text: string, t: number, start: number, cps: number) =>
  Math.max(0, Math.min(text.length, Math.floor(((t - start) / 30) * cps)));

/** Blinking block/bar caret (500 ms period), solid while typing. */
export const caretOn = (t: number, typing: boolean) => typing || Math.floor(t / 15) % 2 === 0;

// ------------------------------------------------------------------ icons
// Line icons drawn in the lucide style (24-unit grid, 2 px stroke, round caps)
// for the glyphs the real UI uses (lucide-react in Navis-AI).

type IconProps = { readonly size?: number; readonly color?: string; readonly strokeWidth?: number; readonly style?: React.CSSProperties };

const Svg: React.FC<IconProps & { readonly children: React.ReactNode }> = ({ size = 14, color = "currentColor", strokeWidth = 2, style, children }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, ...style }}>
    {children}
  </svg>
);

export const Icon = {
  Send: (p: IconProps) => (
    <Svg {...p}>
      <path d="M14.5 21.5 22 2 2.5 9.5l7.8 3.2z" />
      <path d="m22 2-11.7 10.7" />
    </Svg>
  ),
  Check: (p: IconProps) => (
    <Svg {...p}>
      <path d="M20 6 9 17l-5-5" />
    </Svg>
  ),
  X: (p: IconProps) => (
    <Svg {...p}>
      <path d="M18 6 6 18M6 6l12 12" />
    </Svg>
  ),
  Loader: ({ rotation = 0, ...p }: IconProps & { readonly rotation?: number }) => (
    <Svg {...p} style={{ ...p.style, rotate: `${rotation}deg` }}>
      <path d="M21 12a9 9 0 1 1-6.2-8.6" />
    </Svg>
  ),
  Inbox: (p: IconProps) => (
    <Svg {...p}>
      <path d="M22 12h-6l-2 3h-4l-2-3H2" />
      <path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.7 1.1z" />
    </Svg>
  ),
  Sparkles: (p: IconProps) => (
    <Svg {...p}>
      <path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" />
      <path d="M19 3v4M21 5h-4" />
    </Svg>
  ),
  Messages: (p: IconProps) => (
    <Svg {...p}>
      <path d="M14 9a2 2 0 0 1-2 2H6l-4 4V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2z" />
      <path d="M18 9h2a2 2 0 0 1 2 2v11l-4-4h-6a2 2 0 0 1-2-2v-1" />
    </Svg>
  ),
  Users: (p: IconProps) => (
    <Svg {...p}>
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8" />
    </Svg>
  ),
  Layers: (p: IconProps) => (
    <Svg {...p}>
      <path d="m12 2 10 5-10 5L2 7z" />
      <path d="m2 17 10 5 10-5M2 12l10 5 10-5" />
    </Svg>
  ),
  Building: (p: IconProps) => (
    <Svg {...p}>
      <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18z" />
      <path d="M6 12H4a2 2 0 0 0-2 2v8h4M18 9h2a2 2 0 0 1 2 2v11h-4M10 6h4M10 10h4M10 14h4M10 18h4" />
    </Svg>
  ),
  History: (p: IconProps) => (
    <Svg {...p}>
      <path d="M3 12a9 9 0 1 0 9-9 9.8 9.8 0 0 0-6.7 2.7L3 8" />
      <path d="M3 3v5h5M12 7v5l4 2" />
    </Svg>
  ),
  Scroll: (p: IconProps) => (
    <Svg {...p}>
      <path d="M15 12h-5M15 8h-5M19 17V5a2 2 0 0 0-2-2H4" />
      <path d="M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3" />
    </Svg>
  ),
  Activity: (p: IconProps) => (
    <Svg {...p}>
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
    </Svg>
  ),
  Shield: (p: IconProps) => (
    <Svg {...p}>
      <path d="M20 13c0 5-3.5 7.5-7.7 9a1 1 0 0 1-.7 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.2-2.7a1.2 1.2 0 0 1 1.6 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z" />
    </Svg>
  ),
  CheckSquare: (p: IconProps) => (
    <Svg {...p}>
      <path d="m9 11 3 3L22 4" />
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
    </Svg>
  ),
  Calendar: (p: IconProps) => (
    <Svg {...p}>
      <rect width="18" height="18" x="3" y="4" rx="2" />
      <path d="M16 2v4M8 2v4M3 10h18" />
    </Svg>
  ),
  Play: (p: IconProps) => (
    <Svg {...p}>
      <path d="M6 3l14 9-14 9z" fill={p.color ?? "currentColor"} />
    </Svg>
  ),
  Refresh: (p: IconProps) => (
    <Svg {...p}>
      <path d="M3 2v6h6M21 12A9 9 0 0 0 6 5.3L3 8M21 22v-6h-6M3 12a9 9 0 0 0 15 6.7l3-2.7" />
    </Svg>
  ),
  External: (p: IconProps) => (
    <Svg {...p}>
      <path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    </Svg>
  ),
  Mail: (p: IconProps) => (
    <Svg {...p}>
      <rect x="2" y="4" width="20" height="16" rx="2" />
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
    </Svg>
  ),
  User: (p: IconProps) => (
    <Svg {...p}>
      <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </Svg>
  ),
  ArrowUpRight: (p: IconProps) => (
    <Svg {...p}>
      <path d="M7 7h10v10M7 17 17 7" />
    </Svg>
  ),
  Plug: (p: IconProps) => (
    <Svg {...p}>
      <path d="M12 22v-5M9 8V2M15 8V2M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8z" />
    </Svg>
  ),
  Settings: (p: IconProps) => (
    <Svg {...p}>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </Svg>
  ),
  Lock: (p: IconProps) => (
    <Svg {...p}>
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </Svg>
  ),
  Key: (p: IconProps) => (
    <Svg {...p}>
      <circle cx="7.5" cy="15.5" r="5.5" />
      <path d="m21 2-9.6 9.6M15.5 7.5l3 3L22 7l-3-3" />
    </Svg>
  ),
  Alert: (p: IconProps) => (
    <Svg {...p}>
      <path d="m21.7 18-8-14a2 2 0 0 0-3.5 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.7-3" />
      <path d="M12 9v4M12 17h.01" />
    </Svg>
  ),
} as const;
