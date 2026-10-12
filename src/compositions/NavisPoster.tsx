import { Freeze } from "remotion";
import { POSTER_FRAME } from "../config/timeline";
import { NavisLaunch } from "./NavisLaunch";

// The poster is the film itself, frozen on the S05 frame where the NavisLabs
// lockup and both products are on screen, so it can never drift from the film.
// Registered as a <Composition> at the film's length rather than a <Still>:
// a <Still> is 1 frame long and Remotion caps nested <Sequence>s at that.
export const NavisPoster: React.FC = () => (
  <Freeze frame={POSTER_FRAME}>
    <NavisLaunch endingVariant="A" useAlternates={[]} mode="preview" />
  </Freeze>
);
