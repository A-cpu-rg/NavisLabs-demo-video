import { AbsoluteFill } from "remotion";
import { BEAT, sec } from "../config/beats";
import { copy } from "../config/filmSpec";
import { DEMO, DEV, FILM } from "../config/navisBrand";
import { Camera } from "../components/Camera";
import { AgentConversation, AgentText, PromptInput, ShellLine, UserTurn } from "../ui/developer/AgentConversation";
import { ConsoleShell, MembersPage, PersonalWorkspacePanel, SignUpChoice } from "../ui/developer/Console";
import { DeveloperShell, TerminalWindow } from "../ui/developer/DeveloperShell";
import { CheckpointCommand, WorkStateCard } from "../ui/developer/WorkState";
import { SOLO_STATE, TEAM, TEAM_STATE } from "../ui/demoContent";
import { caretOn, useSceneClock } from "../ui/kit";
import { DayTag, FilmLabel, UiCursor, arcPoint } from "./shared";

// S16 · P5 "A solo builder gets a private workspace. A team can work together.
// And the work state carries into the next session. [pause]"
// Navis Developer stands on its own — no Navis App required:
//   1) solo: sign up "For myself" (features/auth/SignUpForm.tsx) → Settings ›
//      Organization: Workspace "Personal", ownership "Owner" (OrganizationPanel.tsx);
//   2) team: the company workspace's Members with their roles (MembersPanel.tsx);
//   3) continuity: the team's agent records `navis workstate checkpoint`
//      (packages/cli workstate.ts); the next session's SessionStart hook restores
//      NAVIS WORK CONTINUITY (restore.ts), held through the founder's pause.
// The solo developer, the personal workspace and the work streams are demo data (SYNTHETIC).

const TEAM_PROMPT_USER = `${DEMO.macUser}@${DEMO.macHost}`;
const PICK = { x: 160, y: -10 };

export const S16: React.FC = () => {
  const { at, r, t, T, end } = useSceneClock("S16");
  const phase = T < BEAT.soloWorkspace ? "signup" : T < BEAT.teamIn ? "workspace" : T < BEAT.soloCheckpoint ? "team" : T < BEAT.soloDayTwo ? "dayOne" : "dayTwo";
  const selected = r(BEAT.soloPick, BEAT.soloPick + 0.12);
  const hover = r(BEAT.soloPick - 0.2, BEAT.soloPick - 0.1);
  const cursor = arcPoint({ x: -160, y: 200 }, PICK, r(BEAT.soloIn + 0.05, BEAT.soloPick - 0.14), -0.1);
  const cmd = r(BEAT.soloCheckpoint, BEAT.soloCheckpoint + 0.35, (x) => x);
  const ok = r(BEAT.soloCheckpointOk, BEAT.soloCheckpointOk + 0.2);
  const ckSections = [0, 1, 2].map((i) => r(BEAT.soloCheckpointOk + 0.1 + i * 0.1, BEAT.soloCheckpointOk + 0.3 + i * 0.1));
  const header = r(BEAT.soloRestore, BEAT.soloRestore + 0.25);
  const sections = [0, 1, 2].map((i) => r(BEAT.soloSections + i * 0.2, BEAT.soloSections + 0.25 + i * 0.2));
  const resume = r(BEAT.soloSections + 0.85, BEAT.soloSections + 1.1);
  const tag = r(BEAT.soloIn + 0.05, BEAT.soloIn + 0.3);
  const solo = phase === "signup" || phase === "workspace";
  return (
    <AbsoluteFill>
      <DeveloperShell lift={0}>
        {phase === "signup" ? (
          <Camera keyframes={[{ f: 0, x: 0, y: 0, scale: 1.3, easing: "drift" }, { f: at(BEAT.soloWorkspace), x: 10, y: 0, scale: 1.33, easing: "drift" }]}>
            <div style={{ position: "absolute", left: -310, top: -190 }}>
              <SignUpChoice selectedPersonal={selected} hoverPersonal={hover} name={SOLO_STATE.user} email={SOLO_STATE.email} />
            </div>
            <UiCursor x={cursor.x} y={cursor.y} opacity={r(BEAT.soloIn + 0.05, BEAT.soloIn + 0.15)} clickFrames={[sec(BEAT.soloPick)]} frameOverride={sec(T)} />
          </Camera>
        ) : phase === "workspace" ? (
          <Camera keyframes={[{ f: at(BEAT.soloWorkspace), x: 150, y: -190, scale: 1.4, easing: "drift", note: "cut: personal workspace" }, { f: at(BEAT.teamIn), x: 156, y: -186, scale: 1.43, easing: "drift" }]}>
            <ConsoleShell active="Organization">
              <PersonalWorkspacePanel name={SOLO_STATE.workspace} slug={SOLO_STATE.workspace.toLowerCase().replace(/[^a-z]+/g, "-").replace(/-$/, "")} reveal={1} />
            </ConsoleShell>
          </Camera>
        ) : phase === "team" ? (
          <Camera keyframes={[{ f: at(BEAT.teamIn), x: 120, y: -140, scale: 1.3, easing: "drift", note: "cut: the team" }, { f: at(BEAT.soloCheckpoint), x: 128, y: -134, scale: 1.33, easing: "drift" }]}>
            <ConsoleShell active="Members">
              <MembersPage team={TEAM} arrive={1} press={0} pending={false} />
            </ConsoleShell>
          </Camera>
        ) : phase === "dayOne" ? (
          <Camera keyframes={[{ f: at(BEAT.soloCheckpoint), x: -30, y: 10, scale: 1.24, easing: "drift", note: "cut: terminal" }, { f: at(BEAT.soloDayTwo), x: -26, y: 16, scale: 1.26, easing: "drift" }]}>
            <TerminalWindow width={1400} height={600} title={`${TEAM_STATE.repo} — claude — 132×30`}>
              <AgentConversation>
                <div style={{ opacity: 0.5 }}>
                  <ShellLine user={TEAM_PROMPT_USER} repo={TEAM_STATE.repo} command="claude" />
                  <UserTurn text="Checkpoint this before I stop for the day." />
                </div>
                <CheckpointCommand repo={TEAM_STATE.repo} branch={TEAM_STATE.branch} command={cmd} status={ok > 0 ? "ok" : "running"} sections={ckSections} okOpacity={ok} stream={TEAM_STATE} />
              </AgentConversation>
            </TerminalWindow>
          </Camera>
        ) : (
          <Camera keyframes={[{ f: at(BEAT.soloDayTwo), x: 0, y: -40, scale: 1.08, easing: "drift", note: "cut: next session" }, { f: at(BEAT.soloRestore + 0.2), x: -40, y: -110, scale: 1.26, easing: "glide" }, { f: at(end + 0.6), x: -40, y: -96, scale: 1.29, easing: "drift" }]}>
            <TerminalWindow width={1400} height={760} title={`${TEAM_STATE.repo} — claude — 132×36`}>
              <AgentConversation>
                <ShellLine user={TEAM_PROMPT_USER} repo={TEAM_STATE.repo} command="claude" />
                {header > 0 ? <WorkStateCard repo={TEAM_STATE.repo} branch={TEAM_STATE.branch} age="14 hour(s) ago" header={header} sections={sections} accent={-1} reveal={{ opacity: header, y: (1 - header) * 8 }} stream={TEAM_STATE} /> : null}
                {resume > 0 ? (
                  <AgentText reveal={{ opacity: resume }}>
                    Picking up from the checkpoint: {TEAM_STATE.decision} <span style={{ color: DEV.termMuted }}>Next: {TEAM_STATE.open}</span>
                  </AgentText>
                ) : null}
                <PromptInput text="" caret={caretOn(t, false)} />
              </AgentConversation>
            </TerminalWindow>
          </Camera>
        )}
        {phase === "dayTwo" ? <DayTag label="Next session" opacity={1} /> : null}
        <div style={{ position: "absolute", left: 0, right: 0, top: 40, display: "flex", justifyContent: "center", opacity: solo ? tag : phase === "team" ? 1 : 0 }}>
          <FilmLabel size={15} tracking={0.3} color={FILM.onInkMuted}>
            {copy("product.developer")} · {solo ? copy("solo") : copy("team")}
          </FilmLabel>
        </div>
      </DeveloperShell>
    </AbsoluteFill>
  );
};
