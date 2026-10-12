import { BEAT } from "../config/beats";
import { useSceneClock } from "../ui/kit";
import { AppFlow } from "./AppFlow";

// S09 · 40.6–44.8 s (wipes light → dark into S10) · V12 "The company acts."
// "Approved — sending" → "Sending…" → Gmail accepted → "Reply sent · Gmail
// accepted the message." Sent only after a real provider receipt. The
// camera breathes out before the hard cut to Navis Developer.
export const S09: React.FC = () => {
  const { at, T, end } = useSceneClock("S09");
  return (
    <AppFlow
      T={T}
      keyframes={[
        { f: 0, x: -560, y: 250, scale: 2.0, easing: "drift" },
        // "Then the company acts." — a clean macro cut to the send state (V7: no whip, no smear).
        { f: at(BEAT.sending) - 1, x: -560, y: 250, scale: 2.02, easing: "drift" },
        { f: at(BEAT.sending), x: -330, y: 105, scale: 1.7, easing: "drift", note: "cut: the send state" },
        { f: at(BEAT.replySent), x: -350, y: 135, scale: 1.78, easing: "glide" },
        // Pull back and to the left: the window keeps the confirmation, the
        // right third holds the same event across the company's systems.
        // V8: a clean cut to the wide view just before the across-systems panel arrives (the 1.2 s
        // zoom from 1.78 to 0.7 still smeared).
        { f: at(BEAT.acrossIn - 0.1) - 1, x: -350, y: 135, scale: 1.78, easing: "drift" },
        { f: at(BEAT.acrossIn - 0.1), x: 300, y: -10, scale: 0.7, easing: "drift", note: "cut: the same event across the company's systems" },
        { f: at(end + 0.6), x: 306, y: -10, scale: 0.71, easing: "drift" },
      ]}
    />
  );
};
