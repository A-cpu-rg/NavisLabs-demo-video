// Geist Sans and Geist Mono (OFL, asset A03) from public/fonts. loadFont
// holds the render until each face is ready.
import { loadFont } from "@remotion/fonts";
import { assetSrc } from "./assets";

const faces = [
  { id: "FONT_GEIST_SANS", family: "Geist Sans" },
  { id: "FONT_GEIST_MONO", family: "Geist Mono" },
] as const;

for (const face of faces) {
  const url = assetSrc(face.id);
  if (url) {
    loadFont({ family: face.family, url, weight: "100 900", format: "woff2" }).catch(
      (err: unknown) => console.warn(`[fonts] ${face.family} failed to load`, err),
    );
  }
}
