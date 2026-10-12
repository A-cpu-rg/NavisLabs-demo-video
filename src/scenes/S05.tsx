import { AbsoluteFill } from "remotion";
import { BEAT } from "../config/beats";
import { useSceneClock } from "../ui/kit";
import { AppFlow } from "./AppFlow";

// S05 · 22.6–26.6 s · V07 "Inside a company, the Navis App is for people."
// The organization (teams, people, customers/projects/commitments, the live
// systems) → the Navis App opens (WIDE, product name above the window) →
// MACRO on "Today at a glance" → Abhishek scrolls to Your attention (MEDIUM).
// the Navis App opens ("Good morning, Abhishek.", the product name above
// the window) → macro on "Today at a glance" (Decisions and Waiting on you) →
// Abhishek scrolls to Your attention: Revenue at risk · Delivery blocked ·
// Commitment due.
export const S05: React.FC = () => {
  const { at, T, end } = useSceneClock("S05");
  return (
    <AbsoluteFill>
      <AppFlow
        T={T}
        keyframes={[
          { f: 0, x: 0, y: 0, scale: 0.86, easing: "drift" },
          { f: at(BEAT.glance - 0.01), x: 0, y: -8, scale: 0.875, easing: "drift" },
          { f: at(BEAT.glance), x: 140, y: 40, scale: 1.5, easing: "drift", note: "cut: Today at a glance" },
          { f: at(BEAT.prioritiesIn - 0.01), x: 146, y: 45, scale: 1.52, easing: "drift" },
          { f: at(BEAT.prioritiesIn), x: 100, y: 70, scale: 1.05, easing: "drift", note: "cut: Your attention" },
          { f: at(end), x: 104, y: 76, scale: 1.07, easing: "drift" },
      ]}
      />
    </AbsoluteFill>
  );
};
