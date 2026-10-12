/* global process, console */
// Renders a list of frames of NavisLaunch (preview mode) as PNG stills, from one bundle.
// Usage: node scripts/render-stills.mjs <outDir> <scale> <frame> [frame...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const root = "/Users/abhishekmeena/Desktop/Navis-Launch-Film";
const out = process.argv[2];
const scale = Number(process.argv[3] ?? 0.5);
const frames = process.argv.slice(4).map(Number);
const serveUrl = await bundle({ entryPoint: path.join(root, "src/index.ts"), rspack: true, publicDir: path.join(root, "public") });
const inputProps = { endingVariant: "A", useAlternates: [], mode: "preview" };
const composition = await selectComposition({ serveUrl, id: "NavisLaunch", inputProps });
for (const frame of frames) {
  await renderStill({ composition, serveUrl, frame, output: path.join(out, `f${String(frame).padStart(4, "0")}.png`), inputProps, scale });
  console.log("frame", frame);
}
