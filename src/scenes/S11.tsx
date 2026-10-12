import { AbsoluteFill } from "remotion";
import { BEAT, TYPING, sec } from "../config/beats";
import { DEMO, DEV } from "../config/navisBrand";
import { Camera } from "../components/Camera";
import { ShellLine } from "../ui/developer/AgentConversation";
import {
  ConnectPage,
  ConsoleShell,
  MembersPage,
} from "../ui/developer/Console";
import { DeveloperShell, TerminalWindow } from "../ui/developer/DeveloperShell";
import { TEAM } from "../ui/demoContent";
import { caretOn, typedCount, useSceneClock } from "../ui/kit";
import { UiCursor, arcPoint } from "./shared";

// S11 · 48.4–52.4 s · V14 "Invite the team. Connect once — MCP, API, SDK or CLI."
// 1) Console › Settings › Members: "Add a member" (Email · Application role ·
//    Developer access) → the row appears as "Invited" (MembersPanel.tsx,
//    InviteMemberForm.tsx). The teammate is demo data.
// 2) Abhishek's macOS Terminal: the Console's own MCP command (key shown as
//    its placeholder) → `claude mcp list` → "✓ Connected".
// 3) Console › Connect: MCP, Developer API, SDK, CLI light as they are named.

const USER = `${DEMO.macUser}@${DEMO.macHost}`;
const ADD =
  "claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> -- node ./services/mcp-server/dist/stdio.js";
// World position of "Add member" on the Members page (checked against stills).
const ADD_BUTTON = { x: 390, y: -44 };

export const S11: React.FC = () => {
  const { at, r, t, T, end } = useSceneClock("S11");
  // Light Console → dark terminal → light Console: short dissolves (0.16 s), not hard flips.
  const toTerminal = r(BEAT.mcpAdd - 0.08, BEAT.mcpAdd + 0.08);
  const toConnect = r(BEAT.connectIn - 0.08, BEAT.connectIn + 0.08);
  const layers = {
    members: 1 - toTerminal,
    terminal: toTerminal * (1 - toConnect),
    connect: toConnect,
  };
  const press =
    r(BEAT.addMember, BEAT.addMember + 0.06) *
    (1 - r(BEAT.addMember + 0.06, BEAT.addMember + 0.16));
  const arrive = r(BEAT.invited, BEAT.invited + 0.25);
  const pending = T >= BEAT.addMember && T < BEAT.invited;
  const cursor = arcPoint(
    { x: 120, y: 160 },
    ADD_BUTTON,
    r(BEAT.membersIn + 0.05, BEAT.addMember - 0.14),
    -0.1,
  );
  const added = T >= BEAT.mcpAdded;
  const list = TYPING.mcpList;
  const listTyped = typedCount(list.text, sec(T), sec(list.start), list.cps);
  const checking = T >= list.start + list.text.length / list.cps + 0.06;
  const connected = r(BEAT.mcpConnected, BEAT.mcpConnected + 0.12);
  const surfaces = [
    BEAT.surfaceMcp,
    BEAT.surfaceApi,
    BEAT.surfaceSdk,
    BEAT.surfaceCli,
  ];
  const reveal = surfaces.map((b, i) => (i === 0 ? 1 : r(b - 0.2, b + 0.1)));
  const focus = surfaces.map(
    (b, i) =>
      r(b, b + 0.1) *
      (1 - (i < 3 ? r(surfaces[i + 1], surfaces[i + 1] + 0.1) : 0)),
  );
  return (
    <AbsoluteFill>
      <DeveloperShell lift={0}>
        {layers.members > 0 ? (
          <AbsoluteFill style={{ opacity: layers.members }}>
            <Camera
              keyframes={[
                { f: 0, x: 120, y: -150, scale: 1.3, easing: "drift" },
                {
                  f: at(BEAT.mcpAdd),
                  x: 130,
                  y: -140,
                  scale: 1.33,
                  easing: "drift",
                },
              ]}
            >
              <ConsoleShell active="Members">
                <MembersPage
                  team={TEAM}
                  arrive={arrive}
                  press={press}
                  pending={pending}
                />
              </ConsoleShell>
              <UiCursor
                x={cursor.x}
                y={cursor.y}
                opacity={r(BEAT.membersIn + 0.05, BEAT.membersIn + 0.15)}
                clickFrames={[sec(BEAT.addMember)]}
                frameOverride={sec(T)}
              />
            </Camera>
          </AbsoluteFill>
        ) : null}
        {layers.terminal > 0 ? (
          <AbsoluteFill style={{ opacity: layers.terminal }}>
            <Camera
              keyframes={[
                {
                  f: at(BEAT.mcpAdd),
                  x: 0,
                  y: -30,
                  scale: 1.2,
                  easing: "drift",
                  note: "cut: terminal",
                },
                {
                  f: at(BEAT.mcpConnected),
                  x: 0,
                  y: -10,
                  scale: 1.22,
                  easing: "drift",
                },
                {
                  f: at(BEAT.connectIn),
                  x: 0,
                  y: -4,
                  scale: 1.24,
                  easing: "drift",
                },
              ]}
            >
              <TerminalWindow
                width={1520}
                height={400}
                title={`${DEMO.repo} — zsh — 160×20`}
              >
                <ShellLine user={USER} repo={DEMO.repo} command={ADD} />
                {added ? (
                  <div style={{ color: DEV.termMuted }}>
                    Added stdio MCP server navis with command: node
                    ./services/mcp-server/dist/stdio.js to local config
                  </div>
                ) : null}
                {T >= list.start - 0.15 ? (
                  <div style={{ marginTop: 10 }}>
                    <ShellLine
                      user={USER}
                      repo={DEMO.repo}
                      command={list.text.slice(0, listTyped)}
                    />
                  </div>
                ) : null}
                {checking ? (
                  <div style={{ color: DEV.termMuted }}>
                    Checking MCP server health…
                  </div>
                ) : null}
                {connected > 0 ? (
                  <div style={{ marginTop: 14, opacity: connected }}>
                    <span style={{ color: DEV.termText }}>navis</span>
                    <span style={{ color: DEV.termMuted }}>
                      : node ./services/mcp-server/dist/stdio.js -{" "}
                    </span>
                    <span style={{ color: DEV.termGreen }}>✓ Connected</span>
                  </div>
                ) : null}
                {connected > 0 ? (
                  <div
                    style={{
                      marginTop: 14,
                      display: "flex",
                      alignItems: "center",
                    }}
                  >
                    <ShellLine user={USER} repo={DEMO.repo} command="" />
                    <span
                      style={{
                        display: "inline-block",
                        width: 9,
                        height: 18,
                        marginLeft: 2,
                        backgroundColor: caretOn(t, false)
                          ? DEV.termText
                          : "transparent",
                      }}
                    />
                  </div>
                ) : null}
              </TerminalWindow>
            </Camera>
          </AbsoluteFill>
        ) : null}
        {layers.connect > 0 ? (
          <AbsoluteFill style={{ opacity: layers.connect }}>
            <Camera
              keyframes={[
                {
                  f: at(BEAT.connectIn),
                  x: 60,
                  y: -20,
                  scale: 1.08,
                  easing: "drift",
                  note: "cut: Console › Connect",
                },
                { f: at(end), x: 63, y: -17, scale: 1.1, easing: "drift" },
              ]}
            >
              <ConsoleShell active="Connect">
                <ConnectPage reveal={reveal} focus={focus} />
              </ConsoleShell>
            </Camera>
          </AbsoluteFill>
        ) : null}
      </DeveloperShell>
    </AbsoluteFill>
  );
};
