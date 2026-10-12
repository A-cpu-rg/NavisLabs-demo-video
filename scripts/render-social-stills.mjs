/* global process, console */
// Renders stills of the NavisSocialV1 composition (4:5) from one bundle.
// Usage: node scripts/render-social-stills.mjs <outDir> <scale> <frame> [frame...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import path from "node:path";
const root = "/Users/abhishekmeena/Desktop/Navis-Launch-Film";
const out = process.argv[2];
const scale = Number(process.argv[3] ?? 0.5);
const frames = process.argv.slice(4).map(Number);
const serveUrl = await bundle({ entryPoint: path.join(root, "src/index.ts"), rspack: true, publicDir: path.join(root, "public") });
const composition = await selectComposition({ serveUrl, id: "NavisSocialV1", inputProps: { stem: "mix" } });
for (const frame of frames) {
  await renderStill({ composition, serveUrl, frame, output: path.join(out, `s${String(frame).padStart(4, "0")}.png`), inputProps: { stem: "mix" }, scale });
  console.log("frame", frame);
}
