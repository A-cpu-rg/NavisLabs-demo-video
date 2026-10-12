import { BEAT } from "../config/beats";
import { useSceneClock } from "../ui/kit";
import { AppFlow } from "./AppFlow";

// S07 · 29.7–34.2 s · V09 "Navis shows why — every fact with its source and
// its time."
// "Why this matters" opens the real "Why Navis surfaced this" drawer; its
// evidence rows arrive with the film's trace notes (source, timeline,
// freshness), then "What you can do".
export const S07: React.FC = () => {
  const { at, T } = useSceneClock("S07");
  return (
    <AppFlow
      T={T}
      keyframes={[
        { f: 0, x: 240, y: 200, scale: 1.42, easing: "drift" },
        { f: at(BEAT.whyClick - 0.05), x: 255, y: 210, scale: 1.44, easing: "glide" },
        { f: at(BEAT.whyOpen + 0.3), x: 100, y: 0, scale: 1.0, easing: "glide" },
        { f: at(BEAT.evidence0 + 0.25), x: 150, y: 185, scale: 1.4, easing: "glide" },
        // V8: a slower push onto source, time and freshness (1.1 s) — readable while the facts are said.
        { f: at(BEAT.explodeIn - 0.05), x: 440, y: 205, scale: 1.7, easing: "glide" },
        { f: at(BEAT.explodeIn), x: 441, y: 205, scale: 1.7, easing: "drift" },
      ]}
    />
  );
};
