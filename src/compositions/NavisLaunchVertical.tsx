import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { colors, fontStack } from "../config/design";
import { getScene, spec } from "../config/loadSpec";
import type { SceneId } from "../config/types";

// project.deliverables.vertical_45s names its source scenes in prose
// ("derived from scenes S02, S08, S09, S14, S17").
const deliverable = spec.project.deliverables.find((d) => d.id === "vertical_45s");
const sourceScenes = (deliverable?.description.match(/\bS\d{2}\b/g) ??
  []) as SceneId[];
const sourceFrames = sourceScenes.reduce(
  (sum, id) => sum + getScene(id).end_frame - getScene(id).start_frame,
  0,
);

/**
 * Bootstrap placeholder. The spec fixes the format (1080x1920, 30 fps,
 * 1350 frames) and the source scenes, but no edit decision list: there are no
 * per-scene in/out points, so no cut is invented here.
 */
export const NavisLaunchVertical: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames, fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: colors.ink,
        color: colors.on_ink_text,
        padding: "160px 96px",
        fontFamily: fontStack("Geist Mono"),
        fontSize: 26,
        lineHeight: 1.6,
        letterSpacing: "0.04em",
        gap: 36,
      }}
    >
      <div style={{ fontSize: 34, letterSpacing: "0.2em", textTransform: "uppercase" }}>
        NavisLaunchVertical
      </div>
      <div style={{ color: colors.on_ink_muted }}>
        Placeholder — not final film
      </div>
      <div>{deliverable?.description}</div>
      <div>
        Source scenes at master timing: {sourceScenes.join(" · ")} ={" "}
        {sourceFrames} f. Target: {durationInFrames} f.
      </div>
      <div style={{ color: colors.on_ink_muted }}>
        Edit decision list not specified in the master spec — needs per-scene
        in/out points before this cut can be built.
      </div>
      <div style={{ marginTop: "auto", color: colors.on_ink_muted }}>
        f {frame} / {durationInFrames} · {(frame / fps).toFixed(2)} s
      </div>
    </AbsoluteFill>
  );
};
