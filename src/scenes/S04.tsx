import { AbsoluteFill } from "remotion";
import { BEAT } from "../config/beats";
import { linePath, NavisLine } from "../components/BlueLine";
import { Camera } from "../components/Camera";
import { Grain } from "../components/World";
import { DataFlow } from "../film/DataFlow";
import { useSceneClock } from "../ui/kit";

// S04 · 14.3–22.6 s
//   V05 "Every email, meeting, document and message becomes a signal —"
//   V06 "remembered, connected, and turned into what should happen next."
// Light canvas (the TransitionSeries wipe brings it up from below; the line
// rides the wipe's edge). The camera follows the information and pulls back
// progressively: close on the connected systems and signals, wider along memory →
// context → intelligence → decision → execution, then the whole chain with
// outcome (building) and learning (next) — the scattered pieces becoming one.

const WIPE_FRAMES = 27;

export const S04: React.FC = () => {
  const { at, t, T, end } = useSceneClock("S04");
  const p = Math.min(1, t / WIPE_FRAMES);
  const edge = 1080 * (1 - p);
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #FFFFFF 0%, #F7F6F3 55%, #ECE9E3 100%)" }}>
      {/* V8: no camera blur here — the pan travels along readable labels; crisp frames read better. */}
      <Camera
        motionBlur={false}
        keyframes={[
          // V7: a progressive pull-back — close on the systems, wider at each stage, the whole chain at the end.
          { f: 0, x: -170, y: 10, scale: 1.08, easing: "drift" },
          { f: at(BEAT.flowIntel - 0.55), x: -90, y: 10, scale: 1.03, easing: "drift" },
          // V8: a slower pan along the pipeline (1.1 s) — readable, no smear.
          { f: at(BEAT.flowIntel + 0.55), x: 620, y: 10, scale: 0.96, easing: "glide" },
          { f: at(BEAT.flowExecution), x: 680, y: 10, scale: 0.94, easing: "drift" },
          { f: at(BEAT.flowExecution + 0.4), x: 900, y: 10, scale: 0.88, easing: "glide" },
          { f: at(BEAT.flowLearning + 0.1), x: 920, y: 10, scale: 0.86, easing: "drift" },
          { f: at(BEAT.flowLearning + 0.6), x: 700, y: 0, scale: 0.66, easing: "glide" },
          { f: at(end + 0.7), x: 700, y: 0, scale: 0.655, easing: "drift" },
        ]}
      >
        <DataFlow T={T} />
      </Camera>
      <Grain opacity={0.015} />
      {p < 1 ? (
        <div style={{ position: "absolute", left: 0, top: edge }}>
          <NavisLine d={linePath({ x: 0, y: 0 }, { x: 1920, y: 0 })} bounds={{ x: -10, y: -40, w: 1940, h: 80 }} width={1.6} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
