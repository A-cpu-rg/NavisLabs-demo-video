import { AbsoluteFill } from "remotion";
import { BEAT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { FILM, FONT } from "../config/navisBrand";
import { linePath, NavisLine } from "../components/BlueLine";
import { Grain } from "../components/World";
import { easeInOut, useSceneClock } from "../ui/kit";
import { FilmLabel, Lockup, ProductTitle } from "./shared";

// S03 · P2 "Navis turns those signals into one shared understanding." · the first wow.
// After the silence: the NavisLabs lockup (website treatment) and its line.
// The lockup rises; the line branches into the two products — Navis
// App for people, Navis Developer for developers and AI agents
// (private preview). Deck p.5 "Two products, one core". S04 wipes to light
// over this scene's last frames.

const BRANCH_X = 440;

export const S03: React.FC = () => {
  const { r } = useSceneClock("S03");
  const tile = r(BEAT.logoTile, BEAT.logoTile + 0.6);
  const word = r(BEAT.logoWord, BEAT.logoWord + 0.6);
  const line = r(BEAT.logoLine, BEAT.logoLine + 1.2, easeInOut);
  const lift = r(BEAT.archApp - 0.35, BEAT.archApp + 0.45, easeInOut);
  const app = r(BEAT.archApp, BEAT.archApp + 0.55);
  const dev = r(BEAT.archDev, BEAT.archDev + 0.55);
  const ways = r(BEAT.archDev + 0.55, BEAT.archDev + 1.05);
  const drift = 1 + 0.025 * r(BEAT.logoTile, BEAT.toLight + 0.9);
  // The first wow: on "Navis" the mark comes into focus — a short lens pull, no glow — as the music opens.
  const focus = r(BEAT.logoTile - 0.05, BEAT.logoTile + 0.6);
  const logoY = 470 - 150 * lift;
  const lineY = logoY + 170;
  const dropTo = lineY + 92;
  return (
    <AbsoluteFill style={{ backgroundColor: FILM.ink }}>
      <AbsoluteFill style={{ scale: String(drift) }}>
        <div style={{ position: "absolute", left: 960, top: logoY, translate: "-50% -50%", scale: String(0.965 + 0.035 * focus), filter: focus < 1 ? `blur(${(1 - focus) * 7}px)` : undefined }}>
          <Lockup size={112} tile={tile} word={word} />
        </div>
        <div style={{ position: "absolute", left: 960, top: lineY, width: 0, height: 0 }}>
          <NavisLine d={linePath({ x: -480, y: 0 }, { x: 480, y: 0 })} trim={[0.5 - line / 2, 0.5 + line / 2]} />
          <NavisLine d={linePath({ x: -BRANCH_X, y: 0 }, { x: -BRANCH_X, y: dropTo - lineY })} trim={[0, app]} width={1.6} />
          <NavisLine d={linePath({ x: BRANCH_X, y: 0 }, { x: BRANCH_X, y: dropTo - lineY })} trim={[0, dev]} width={1.6} />
        </div>
        <div style={{ position: "absolute", left: 960 - BRANCH_X, top: dropTo + 28, translate: "-50% 0" }}>
          <ProductTitle name={copy("product.application")} audience={copy("product.application.audience")} tone="dark" size={42} reveal={app} />
        </div>
        <div style={{ position: "absolute", left: 960 + BRANCH_X, top: dropTo + 28, translate: "-50% 0", display: "flex", flexDirection: "column", alignItems: "center" }}>
          <ProductTitle name={copy("product.developer")} audience={copy("product.developer.audience")} tone="dark" size={42} reveal={dev} />
          <div style={{ marginTop: 18, opacity: dev, padding: "5px 12px", borderRadius: 999, border: "1px solid rgba(237,235,230,0.22)", fontFamily: FONT.mono, fontSize: 12, letterSpacing: "0.18em", textTransform: "uppercase", color: FILM.onInkMuted }}>
            {copy("product.developer.status")}
          </div>
        </div>
        <div style={{ position: "absolute", left: 960, top: dropTo + 250, translate: "-50% 0", opacity: ways }}>
          <FilmLabel size={19} tracking={0.3} color={FILM.onInk}>
            {copy("twoWays")}
          </FilmLabel>
        </div>
      </AbsoluteFill>
      <Grain opacity={0.025} />
    </AbsoluteFill>
  );
};
