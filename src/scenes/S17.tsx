import { AbsoluteFill } from "remotion";
import { BEAT } from "../config/beats";
import { FILM } from "../config/navisBrand";
import { Camera } from "../components/Camera";
import { Grain } from "../components/World";
import { ProductSplit } from "../film/ProductSplit";
import { useSceneClock } from "../ui/kit";

// S17 · 73.4–84.0 s · one company, two products.
//   V19 "The person and the agent acted on the same event."
//   V20 "Same facts. Same sources. Same freshness."
//   V21 "One company. One understanding. Two ways in."
// The hero: the Navis App and Navis Developer either side of the
// NavisLabs understanding layer; the Kaveri event reaches both. Macro cuts on
// the same fact, source and freshness as each product shows it; then the
// thesis and "People + AI agents · one shared understanding".

export const S17: React.FC = () => {
  const { at, r, T, end } = useSceneClock("S17");
  return (
    <AbsoluteFill style={{ backgroundColor: FILM.ink }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse 65% 55% at 50% 42%, rgba(237,235,230,0.06), rgba(20,19,15,0) 70%)", opacity: r(BEAT.heroIn, BEAT.heroIn + 1) }} />
      <Camera
        keyframes={[
          { f: 0, x: 0, y: -70, scale: 1.04, easing: "drift" },
          { f: at(BEAT.sharedSignal + 0.6), x: 0, y: -60, scale: 1.0, easing: "glide" },
          { f: at(BEAT.sameFacts - 0.01), x: 0, y: -56, scale: 0.99, easing: "drift" },
          { f: at(BEAT.sameFacts), x: 30, y: 270, scale: 1.2, easing: "drift", note: "cut: same fact" },
          { f: at(BEAT.sameSources - 0.01), x: 30, y: 272, scale: 1.215, easing: "drift" },
          { f: at(BEAT.sameSources), x: 30, y: 334, scale: 1.2, easing: "drift", note: "cut: same source" },
          { f: at(BEAT.sameFreshness - 0.01), x: 30, y: 336, scale: 1.215, easing: "drift" },
          { f: at(BEAT.sameFreshness), x: 30, y: 398, scale: 1.2, easing: "drift", note: "cut: same freshness" },
          { f: at(BEAT.sharedUnderstanding - 0.46), x: 30, y: 400, scale: 1.215, easing: "drift" },
          { f: at(BEAT.sharedUnderstanding - 0.45), x: 0, y: 100, scale: 1.03, easing: "drift", note: "cut: all three" },
          { f: at(BEAT.sharedUnderstanding + 1.1), x: 0, y: 90, scale: 0.93, easing: "glide", note: "'One understanding.' — the camera pulls back" },
          { f: at(end + 0.6), x: 0, y: 90, scale: 0.925, easing: "drift" },
        ]}
      >
        <ProductSplit T={T} />
      </Camera>
      <Grain opacity={0.025} />
    </AbsoluteFill>
  );
};
