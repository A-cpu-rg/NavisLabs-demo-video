import { BEAT } from "../config/beats";
import { useSceneClock } from "../ui/kit";
import { MemoryFlow } from "./MemoryFlow";

// S01 · 0–6.2 s · V01–V02: people and agents see different truths; the truth is scattered.
export const S01: React.FC = () => {
  const { at, T, end } = useSceneClock("S01");
  return (
    <MemoryFlow
      T={T}
      keyframes={[
        { f: 0, x: 0, y: 0, scale: 0.98, easing: "drift" },
        { f: at(BEAT.scatter), x: 0, y: 0, scale: 1.0, easing: "drift" },
        { f: at(BEAT.scatter + 1.0), x: 0, y: 0, scale: 0.86, easing: "glide" },
        { f: at(end + 0.6), x: 0, y: 0, scale: 0.85, easing: "drift" },
      ]}
    />
  );
};
