import { Easing } from "remotion";
import { spec } from "./loadSpec";
import type { EasingName, TypeRole } from "./types";

// Visual and motion tokens, read from the spec rather than copied, so a spec
// change never leaves a stale value behind in code.

export const colors = spec.visual_system.color_tokens;

const { easings: easingSpec } = spec.motion_system;

const bezier = (name: EasingName) => {
  const [x1, y1, x2, y2] = easingSpec[name].bezier;
  return Easing.bezier(x1, y1, x2, y2);
};

export const easings: Record<EasingName, (t: number) => number> = {
  glide: bezier("glide"),
  settle: bezier("settle"),
  weighted: bezier("weighted"),
  exit: bezier("exit"),
  drift: bezier("drift"),
};

export const springUi = easingSpec.spring_ui.remotion_spring;

// Geist Sans / Geist Mono are asset A03 and not loaded yet; the fallbacks keep
// the layout usable until public/fonts/ holds the woff2 files.
export const fontStacks = {
  "Geist Sans": '"Geist Sans", "Geist", system-ui, -apple-system, sans-serif',
  "Geist Mono": '"Geist Mono", ui-monospace, "SF Mono", Menlo, monospace',
} as const;

export type TypeRoleName =
  | "statement"
  | "wordmark"
  | "title_mono"
  | "caption_mono"
  | "label_mono_small"
  | "legal";

export const typeRole = (name: TypeRoleName): TypeRole => {
  const role = spec.visual_system.typography.hierarchy_px_at_1080p.find(
    (r) => r.role === name,
  );
  if (!role) throw new Error(`Type role ${name} is not in the spec`);
  return role;
};

export const fontStack = (family: string): string =>
  family in fontStacks
    ? fontStacks[family as keyof typeof fontStacks]
    : fontStacks["Geist Sans"];

export const titleSafe = spec.visual_system.safe_areas.title_safe_px;
export const windowChrome = spec.visual_system.window_chrome;
