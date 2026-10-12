import { CameraMotionBlur } from "@remotion/motion-blur";
import { createContext, useContext } from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { colors, easings } from "../config/design";
import type { BlueprintKeyframe } from "../config/loadBlueprint";
import type { CameraKeyframe } from "../config/types";

export type CameraState = { x: number; y: number; scale: number };
type Keyframe = CameraKeyframe | BlueprintKeyframe;

const isCut = (kf: Keyframe) => "note" in kf && typeof kf.note === "string" && /\bcut\b/i.test(kf.note);

// motion_system.camera_model: each segment eases with the easing named on its
// destination keyframe. A destination whose note names a cut ("match cut to
// R10") is a hard cut: the camera holds, then jumps on that frame.
// V7: the spec's "glide" (bezier 0.22, 1, 0.36, 1) starts at ~4.5× its average speed, which
// smeared the first frames of every push and pull. The camera uses a gentle-start glide instead
// (soft departure, firm settle; peak ≈ 2× average), so fast moves stay readable. The protected
// spec file is not modified; element entrances keep the spec's curves.
const CAMERA_EASINGS = { ...easings, glide: Easing.bezier(0.45, 0, 0.2, 1) };

export const cameraAt = (frame: number, keyframes: readonly Keyframe[]): CameraState => {
  const first = keyframes[0];
  if (keyframes.length === 1 || frame <= first.f) return first;
  for (let i = 1; i < keyframes.length; i++) {
    const from = keyframes[i - 1];
    const to = keyframes[i];
    if (frame < to.f || (frame === to.f && !isCut(to))) {
      if (isCut(to)) return from;
      const p = interpolate(frame, [from.f, to.f], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: CAMERA_EASINGS[to.easing],
      });
      return {
        x: from.x + (to.x - from.x) * p,
        y: from.y + (to.y - from.y) * p,
        scale: from.scale + (to.scale - from.scale) * p,
      };
    }
  }
  return keyframes[keyframes.length - 1];
};

export const useCameraState = (keyframes: readonly Keyframe[]): CameraState =>
  cameraAt(useCurrentFrame(), keyframes);

/** Screen position of a world point under a camera. */
export const worldToScreen = (
  p: { x: number; y: number },
  cam: CameraState,
  width = 1920,
  height = 1080,
) => ({
  x: width / 2 + (p.x - cam.x) * cam.scale,
  y: height / 2 + (p.y - cam.y) * cam.scale,
});

const CameraContext = createContext<CameraState>({ x: 0, y: 0, scale: 1 });

type Props = {
  readonly keyframes: readonly Keyframe[];
  /** Blur fast camera moves (default on). Only frames that move faster than BLUR_SPEED get it. */
  readonly motionBlur?: boolean;
  /** Extra zoom around the frame center, multiplied on top of the keyframes (used for zoom-through exits). */
  readonly extraScale?: number;
  readonly children: React.ReactNode;
};

// Screen px per frame above which a camera move gets motion blur. Drifts and
// holds stay sharp; only real glides and push-ins blur. Samples look forward
// within the frame (CameraMotionBlur), so a hard cut never ghosts.
// V7/V8: a gentle shutter (90°) and a high threshold (60 px/frame): ordinary eased moves stay
// crisp and readable; only a true whip would blur (none remain — fast changes are cuts).
const BLUR_SPEED = 60;
const BLUR_SAMPLES = 6;
const SHUTTER = 90;

/** Fastest screen-space speed (px/frame) of any frame corner between two frames. */
export const cameraSpeed = (keyframes: readonly Keyframe[], frame: number, width = 1920, height = 1080) => {
  const a = cameraAt(frame, keyframes);
  const b = cameraAt(frame + 1, keyframes);
  const pan = Math.hypot((b.x - a.x) * a.scale, (b.y - a.y) * a.scale);
  const zoom = (Math.hypot(width, height) / 2) * Math.abs(b.scale / a.scale - 1);
  return pan + zoom;
};

const isCutAt = (keyframes: readonly Keyframe[], frame: number) =>
  keyframes.some((kf) => isCut(kf) && kf.f > frame && kf.f <= frame + 1);

// The world is evaluated inside CameraMotionBlur's Freeze, so each blur
// sample recomputes the camera at its own sub-frame time.
const World: React.FC<{ readonly keyframes: readonly Keyframe[]; readonly extraScale: number; readonly children: React.ReactNode }> = ({ keyframes, extraScale, children }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const cam = cameraAt(frame, keyframes);
  const scale = cam.scale * extraScale;
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          transformOrigin: "0 0",
          translate: `${width / 2 - cam.x * scale}px ${height / 2 - cam.y * scale}px`,
          scale: String(scale),
        }}
      >
        <CameraContext.Provider value={cam}>{children}</CameraContext.Provider>
      </div>
    </AbsoluteFill>
  );
};

/**
 * The world plane has its origin at its center; children are positioned in
 * world px around it. camera.x/y is the world point placed at the frame
 * center; camera.scale is zoom.
 */
export const Camera: React.FC<Props> = ({ keyframes, motionBlur = true, extraScale = 1, children }) => {
  const frame = useCurrentFrame();
  const world = (
    <World keyframes={keyframes} extraScale={extraScale}>
      {children}
    </World>
  );
  const blur = motionBlur && !isCutAt(keyframes, frame) && cameraSpeed(keyframes, frame) > BLUR_SPEED;
  return blur ? (
    <CameraMotionBlur shutterAngle={SHUTTER} samples={BLUR_SAMPLES}>
      {world}
    </CameraMotionBlur>
  ) : (
    world
  );
};

/** motion_system.camera_model.depth: layer offset = camera delta * (1 + z/1000). */
export const ParallaxLayer: React.FC<{ readonly z: number; readonly children: React.ReactNode }> = ({ z, children }) => {
  const cam = useContext(CameraContext);
  return (
    <div style={{ position: "absolute", left: 0, top: 0, translate: `${(-cam.x * z) / 1000}px ${(-cam.y * z) / 1000}px` }}>
      {children}
    </div>
  );
};

/** Places children centered on a world point. */
export const At: React.FC<{
  readonly x: number;
  readonly y: number;
  readonly anchor?: "center" | "left" | "right";
  readonly style?: React.CSSProperties;
  readonly children: React.ReactNode;
}> = ({ x, y, anchor = "center", style, children }) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      translate: anchor === "center" ? "-50% -50%" : anchor === "left" ? "0 -50%" : "-100% -50%",
      whiteSpace: "nowrap",
      ...style,
    }}
  >
    {children}
  </div>
);

/** Darkens the frame edges as the camera moves into a macro (dark world only). */
export const FocusVignette: React.FC<{ readonly scale: number }> = ({ scale }) => {
  const strength = interpolate(scale, [1.3, 2.0], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  if (strength === 0) return null;
  return (
    <AbsoluteFill
      style={{
        pointerEvents: "none",
        opacity: strength,
        background: `radial-gradient(ellipse 75% 70% at 50% 50%, rgba(20,19,15,0) 55%, ${colors.ink}59 100%)`,
      }}
    />
  );
};
