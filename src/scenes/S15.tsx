import { AbsoluteFill } from "remotion";
import { BEAT } from "../config/beats";
import { Camera } from "../components/Camera";
import { ConsoleShell, RunDetailPage, RunsPage } from "../ui/developer/Console";
import { DeveloperShell } from "../ui/developer/DeveloperShell";
import { easeInOut, useSceneClock } from "../ui/kit";
import { DevFlow } from "./DevFlow";

// S15 · 62.2–66.6 s (fades into the solo developer) · V18 "The agent does the work, and the run is on record."
// Macro on the diff in kaveri-renewal.ts (renewsOn Nov 28, annual terms); cut
// to what the agent says it relied on. Then the Navis Developer Console: the
// new run arrives in Runs → the Run page fills its timeline step by step
// (Context → Read → Edit → Verification → Outcome, with times). Model, tokens,
// cost and latency were not reported, so they read "—"; Outcome "Not judged".

export const S15: React.FC = () => {
  const { at, r, T, end } = useSceneClock("S15");
  const consoleIn = r(BEAT.runs, BEAT.runs + 0.2, easeInOut);
  const detail = T >= BEAT.runOpen;
  // RUN START → WORK → RUN COMPLETE: the run arrives as Running, its timeline fills step by
  // step, and it reads Completed as the last step lands (BEAT.runComplete).
  const rows = [0, 1, 2, 3, 4].map((i) => r(BEAT.runTimeline + i * 0.15, BEAT.runTimeline + 0.14 + i * 0.15));
  const complete = T >= BEAT.runComplete;
  const outcome = r(BEAT.runOutcome, BEAT.runOutcome + 0.25);
  return (
    <AbsoluteFill>
      <DevFlow
        T={T}
        keyframes={[
          { f: 0, x: -330, y: -230, scale: 1.55, easing: "drift", note: "cut: the diff" },
          { f: at(BEAT.agentDone - 0.05), x: -322, y: -226, scale: 1.58, easing: "drift" },
          { f: at(BEAT.agentDone), x: 450, y: 60, scale: 1.5, easing: "drift", note: "cut: what it relied on" },
          { f: at(BEAT.runs), x: 452, y: 62, scale: 1.52, easing: "drift" },
        ]}
      />
      {consoleIn > 0 ? (
        <AbsoluteFill style={{ opacity: consoleIn }}>
          <DeveloperShell lift={0}>
            {!detail ? (
              <Camera
                keyframes={[
                  { f: at(BEAT.runs), x: 150, y: -150, scale: 1.45, easing: "drift" },
                  { f: at(BEAT.runOpen), x: 140, y: -158, scale: 1.48, easing: "drift" },
                ]}
              >
                <ConsoleShell active="Runs">
                  <RunsPage highlight={r(BEAT.runRow + 0.15, BEAT.runRow + 0.4)} arrive={r(BEAT.runRow, BEAT.runRow + 0.25)} running />
                </ConsoleShell>
              </Camera>
            ) : (
              <Camera
                keyframes={[
                  { f: at(BEAT.runOpen), x: 90, y: -20, scale: 1.16, easing: "drift", note: "cut: the run" },
                  { f: at(end + 0.6), x: 96, y: -12, scale: 1.19, easing: "drift" },
                ]}
              >
                <ConsoleShell active="Runs">
                  <RunDetailPage rows={rows} outcome={outcome} complete={complete} />
                </ConsoleShell>
              </Camera>
            )}
          </DeveloperShell>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
