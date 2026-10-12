import { BEAT } from "../config/beats";
import { useSceneClock } from "../ui/kit";
import { AppFlow } from "./AppFlow";

// S06 · 26.6–29.7 s · V08 "Kaveri's renewal moved."
// Macro cut to What changed (one verified "Just learned" card), then to the
// Kaveri priority in Your attention: Revenue at risk, the renewal moved, terms
// not yet confirmed, with its Gmail / Calendar / commitment chips.
export const S06: React.FC = () => {
  const { at, T, end } = useSceneClock("S06");
  return (
    <AppFlow
      T={T}
      keyframes={[
        { f: 0, x: 140, y: 215, scale: 1.95, easing: "drift", note: "cut: What changed" },
        { f: at(BEAT.priorityFocus - 0.01), x: 145, y: 218, scale: 2.0, easing: "drift" },
        { f: at(BEAT.priorityFocus), x: 60, y: 100, scale: 1.55, easing: "drift", note: "cut: the customer priority" },
        // V7: a clean cut back to the card (a 0.25 s push smeared three frames).
        { f: at(BEAT.backToCard) - 1, x: 64, y: 104, scale: 1.56, easing: "drift" },
        { f: at(BEAT.backToCard), x: 200, y: 180, scale: 1.42, easing: "drift", note: "cut: back to the card" },
        { f: at(end), x: 210, y: 186, scale: 1.43, easing: "drift" },
      ]}
    />
  );
};
