import { BEAT } from "../config/beats";
import { useSceneClock } from "../ui/kit";
import { DevFlow } from "./DevFlow";

// S12 · 52.4–55.9 s · V15 "The agent asks — and gets cited facts, with their
// freshness."
// navis_get_relevant_context (MCP) prints KAVERI FREIGHTWORKS as a table in Claude
// Code: five facts, each with source · date and freshness (auth_state ·
// last_success_at); macro on SOURCE, then FRESHNESS; the agent cites them.
export const S12: React.FC = () => {
  const { at, T, end } = useSceneClock("S12");
  return (
    <DevFlow
      T={T}
      keyframes={[
        { f: 0, x: 450, y: -170, scale: 1.5, easing: "drift", note: "cut: back to the agent" },
        { f: at(BEAT.contextResult - 0.05), x: 450, y: -160, scale: 1.5, easing: "drift" },
        { f: at(BEAT.contextResult + 0.25), x: 450, y: -90, scale: 1.55, easing: "glide" },
        // V7: the macros on SOURCE and FRESHNESS are clean cuts (precise, readable — no smear).
        { f: at(BEAT.contextSource) - 1, x: 450, y: -86, scale: 1.56, easing: "drift" },
        { f: at(BEAT.contextSource), x: 520, y: -60, scale: 2.0, easing: "drift", note: "cut: SOURCE" },
        { f: at(BEAT.contextFresh) - 1, x: 524, y: -58, scale: 2.02, easing: "drift" },
        { f: at(BEAT.contextFresh), x: 640, y: -60, scale: 2.0, easing: "drift", note: "cut: FRESHNESS" },
        { f: at(BEAT.agentReason) - 1, x: 644, y: -58, scale: 2.02, easing: "drift" },
        { f: at(BEAT.agentReason), x: 450, y: 20, scale: 1.55, easing: "drift", note: "cut: the agent reasons" },
        { f: at(end), x: 450, y: 24, scale: 1.56, easing: "drift" },
      ]}
    />
  );
};
