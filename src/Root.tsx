import { Composition } from "remotion";
import {
  calculateNavisLaunchMetadata,
  NavisLaunch,
  navisLaunchSchema,
} from "./compositions/NavisLaunch";
import { NavisLaunchVertical } from "./compositions/NavisLaunchVertical";
import { NavisPoster } from "./compositions/NavisPoster";
import { SOCIAL_FPS, SOCIAL_FRAMES, SocialFilm } from "./social/SocialFilm";
import { getCompositionSpec } from "./config/loadSpec";
import { FILM_FRAMES } from "./config/timeline";

// Sizes and fps come from remotion_architecture.compositions in the master
// spec. The launch film's LENGTH comes from the founder's voiceover
// (navislabs_v8_film_spec.json → FILM_FRAMES), not from the legacy 100 s.
const launch = getCompositionSpec("NavisLaunch");
const vertical = getCompositionSpec("NavisLaunchVertical");
const poster = getCompositionSpec("NavisPoster");

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="NavisLaunch"
        component={NavisLaunch}
        width={launch.width}
        height={launch.height}
        fps={launch.fps ?? 30}
        durationInFrames={FILM_FRAMES}
        schema={navisLaunchSchema}
        defaultProps={{ endingVariant: "A", useAlternates: [], mode: "preview" }}
        calculateMetadata={calculateNavisLaunchMetadata}
      />
      <Composition
        id="NavisLaunchVertical"
        component={NavisLaunchVertical}
        width={vertical.width}
        height={vertical.height}
        fps={vertical.fps ?? 30}
        durationInFrames={vertical.durationInFrames ?? 1}
      />
      <Composition
        id="NavisPoster"
        component={NavisPoster}
        width={poster.width}
        height={poster.height}
        fps={launch.fps ?? 30}
        durationInFrames={FILM_FRAMES}
      />
      {/* SOCIAL V1 — a separate 4:5 social cut edited from the approved V7 film (V7/V8 untouched). */}
      <Composition id="NavisSocialV1" component={SocialFilm} width={1080} height={1350} fps={SOCIAL_FPS} durationInFrames={SOCIAL_FRAMES} defaultProps={{ stem: "mix" as const }} />
    </>
  );
};
