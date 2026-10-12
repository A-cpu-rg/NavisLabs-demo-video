// Prints the film's resolved timing config (beats, SFX events, typing, scenes)
// as JSON, by bundling the real TypeScript modules with esbuild. Used by
// scripts/validate-film.py so the validators check what the film renders.
import { build } from "esbuild";
import { mkdirSync, rmSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const dir = path.join(root, "node_modules", ".cache", "navis-validate");
mkdirSync(dir, { recursive: true });
const out = path.join(dir, `config-${process.pid}.mjs`);

await build({
  stdin: {
    contents: [
      'export { BEAT, SFX_EVENTS, SFX_CATEGORIES, SFX_SILENCES, TYPING } from "./src/config/beats";',
      'export { FILM_SCENES, FILM_FRAMES, FILM_FPS } from "./src/config/timeline";',
    ].join("\n"),
    resolveDir: root,
    loader: "ts",
  },
  bundle: true,
  format: "esm",
  platform: "node",
  outfile: out,
  logLevel: "silent",
});

try {
  const m = await import(pathToFileURL(out).href);
  process.stdout.write(
    JSON.stringify({
      BEAT: m.BEAT,
      SFX_EVENTS: m.SFX_EVENTS,
      SFX_CATEGORIES: m.SFX_CATEGORIES,
      SFX_SILENCES: m.SFX_SILENCES,
      TYPING: m.TYPING,
      FILM_SCENES: m.FILM_SCENES,
      FILM_FRAMES: m.FILM_FRAMES,
      FILM_FPS: m.FILM_FPS,
    }),
  );
} finally {
  rmSync(out, { force: true });
}
