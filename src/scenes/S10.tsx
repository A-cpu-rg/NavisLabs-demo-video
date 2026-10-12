import { AbsoluteFill } from "remotion";
import { BEAT, TYPING } from "../config/beats";
import { linePath, NavisLine } from "../components/BlueLine";
import { useSceneClock } from "../ui/kit";
import { DevFlow } from "./DevFlow";

// S10 · 44.8–48.4 s · V13 "The same company's agents use Navis Developer."
// Light → dark: the wipe comes down from the top (the line rides its edge)
// into Abhishek's VS Code on the same company's repository — Claude Code
// in the terminal, the task typed, the file read, the context it lacks.

const WIPE_FRAMES = 18;

export const S10: React.FC = () => {
  const { at, t, T, end } = useSceneClock("S10");
  const task = TYPING.agentTask;
  const p = Math.min(1, t / WIPE_FRAMES);
  return (
    <AbsoluteFill>
      <DevFlow
        T={T}
        keyframes={[
          { f: 0, x: 0, y: 0, scale: 0.86, easing: "drift" },
          { f: at(task.start - 0.3), x: 0, y: -6, scale: 0.875, easing: "drift" },
          { f: at(task.start), x: 450, y: -300, scale: 1.6, easing: "glide" },
          { f: at(BEAT.agentEnter), x: 450, y: -282, scale: 1.58, easing: "drift" },
          { f: at(BEAT.agentNeeds + 0.1), x: 450, y: -232, scale: 1.52, easing: "glide" },
          { f: at(end), x: 450, y: -226, scale: 1.53, easing: "drift" },
        ]}
      />
      {p < 1 ? (
        <div style={{ position: "absolute", left: 0, top: 1080 * p }}>
          <NavisLine d={linePath({ x: 0, y: 0 }, { x: 1920, y: 0 })} bounds={{ x: -10, y: -40, w: 1940, h: 80 }} width={1.6} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
