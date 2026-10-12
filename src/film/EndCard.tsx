import { copy } from "../config/filmSpec";
import { FILM, FONT } from "../config/navisBrand";
import { Lockup } from "../scenes/shared";

// The final frame: the NavisLabs mark + wordmark (no tile, no glow), the
// website's headline, its two products and who each is for, navislabs.in.
// One small disclosure line.

const Product: React.FC<{ readonly name: string; readonly audience: string; readonly badge?: string }> = ({ name, audience, badge }) => (
  <div style={{ textAlign: "center" }}>
    <div style={{ fontFamily: FONT.display, fontSize: 26, fontWeight: 600, letterSpacing: "0.08em", color: FILM.onInk, whiteSpace: "nowrap" }}>{name}</div>
    <div style={{ marginTop: 10, fontFamily: FONT.mono, fontSize: 16, letterSpacing: "0.1em", color: FILM.onInkMuted, whiteSpace: "nowrap" }}>
      {audience}
      {badge ? <span style={{ color: FILM.onInkDim }}> · {badge}</span> : null}
    </div>
  </div>
);

export const EndCard: React.FC<{
  readonly tile: number;
  readonly word: number;
  readonly tagline: number;
  readonly products: number;
  readonly cta: number;
  readonly disclosure: number;
}> = ({ tile, word, tagline, products, cta, disclosure }) => (
  <>
    <div style={{ position: "absolute", left: 0, right: 0, top: 270, display: "flex", justifyContent: "center" }}>
      <Lockup size={100} tile={tile} word={word} />
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 452, display: "flex", justifyContent: "center", opacity: tagline, translate: `0 ${(1 - tagline) * 10}px` }}>
      <div style={{ fontFamily: FONT.display, fontSize: 40, fontWeight: 500, letterSpacing: "-0.015em", color: FILM.onInk }}>{copy("tagline")}</div>
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 580, display: "flex", justifyContent: "center", alignItems: "center", gap: 64, opacity: products, translate: `0 ${(1 - products) * 10}px` }}>
      <Product name={copy("product.application")} audience={copy("product.application.audience")} />
      <div style={{ width: 1, height: 52, backgroundColor: "rgba(237,235,230,0.22)" }} />
      <Product name={copy("product.developer")} audience={copy("product.developer.audience")} badge={copy("product.developer.status")} />
    </div>
    <div style={{ position: "absolute", left: 0, right: 0, top: 740, display: "flex", justifyContent: "center", opacity: cta }}>
      <div style={{ fontFamily: FONT.mono, fontSize: 26, letterSpacing: "0.06em", color: FILM.onInk }}>{copy("url")}</div>
    </div>
    {/* The disclosure names the fictional customer, so it must stay readable at 1080p. */}
    <div style={{ position: "absolute", left: 220, right: 220, bottom: 40, display: "flex", justifyContent: "center", opacity: disclosure * 0.9 }}>
      <div style={{ fontFamily: FONT.display, fontSize: 15, lineHeight: 1.55, letterSpacing: "0.005em", textAlign: "center", color: FILM.onInkDim }}>{copy("disclosure")}</div>
    </div>
  </>
);
