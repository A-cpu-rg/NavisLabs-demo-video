// Builds asset_requirements.json from the master spec and checks public/ for
// each asset. Re-run (`npm run assets`) whenever assets are added.
// Nothing is generated or downloaded: a missing asset is only listed.
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const spec = JSON.parse(
  readFileSync(join(root, "navis_master_cinematic_launch_spec.json"), "utf8"),
);

const planStatus = Object.fromEntries(spec.asset_plan.map((a) => [a.id, a.status]));

const fileStatus = (path) => (existsSync(join(root, path)) ? "present" : "missing");
const dirStatus = (path) => {
  const dir = join(root, path);
  const files = existsSync(dir)
    ? readdirSync(dir).filter((f) => !f.startsWith("."))
    : [];
  return files.length > 0 ? "present" : "missing";
};

const asList = (value) => (value === null ? [] : Array.isArray(value) ? value : [value]);

const recordings = spec.recording_plan.recordings.map((r) => {
  const scenes = spec.scenes
    .filter((s) => asList(s.screen_recording).includes(r.id))
    .map((s) => s.scene_id);
  const alternates = spec.alternates
    .filter((a) => a.recording === r.id)
    .map((a) => a.id);
  const path = `public/recordings/${r.id}.mov`;
  return {
    id: r.id,
    kind: "recording",
    asset_plan_ref: "A04",
    path,
    status: fileStatus(path),
    required_by: [...scenes, ...alternates],
    optional: scenes.length === 0,
    // The legacy spec names the people product "Navis AI"; the film calls it the Navis App.
    description: `${r.product.replace(/\bNavis AI\b/g, "Navis App")} — ${r.page}`,
    capture: "see recording_plan.capture_defaults (2x HiDPI, 60 fps, ProRes 422 HQ)",
  };
});

const selected = spec.voiceover.versions[spec.voiceover.selected];
const voTiming = Object.fromEntries(spec.voiceover.timing.map((t) => [t.line, t]));
const voiceover = selected.lines.map((line) => {
  const n = line.id.replace(/^L/, "").padStart(2, "0");
  const path = `public/voiceover/L${n}.wav`;
  const timing = voTiming[line.id];
  return {
    id: line.id,
    kind: "voiceover",
    asset_plan_ref: "A05",
    path,
    status: fileStatus(path),
    required_by: timing ? [timing.scene] : [],
    window_seconds: timing ? [timing.start, timing.end] : null,
    script: line.text,
    format: spec.voiceover.recording.format,
  };
});

const assets = [
  {
    id: "A01",
    kind: "image",
    asset_plan_ref: "A01",
    path: "public/images/navis-logomark.svg",
    status: fileStatus("public/images/navis-logomark.svg"),
    required_by: ["S05", "S17", "NavisPoster"],
    description: spec.asset_plan.find((a) => a.id === "A01").asset,
    blocking_item: "U07",
  },
  {
    id: "A02",
    kind: "wordmark",
    asset_plan_ref: "A02",
    path: null,
    status: "provisional",
    required_by: ["S05", "S17"],
    description: `${spec.brand.wordmark.text} set in ${spec.brand.wordmark.provisional_typeface} until approved`,
    blocking_item: "U07",
  },
  ...["Geist-Variable.woff2", "GeistMono-Variable.woff2"].map((file) => ({
    id: `A03:${file}`,
    kind: "font",
    asset_plan_ref: "A03",
    path: `public/fonts/${file}`,
    status: fileStatus(`public/fonts/${file}`),
    required_by: ["all scenes (film typography)"],
    description: "Geist (OFL), loaded locally via @remotion/fonts; file name proposed",
  })),
  ...recordings,
  ...voiceover,
  {
    id: "A06",
    kind: "music",
    asset_plan_ref: "A06",
    path: "public/music/",
    status: dirStatus("public/music"),
    required_by: ["NavisLaunch"],
    description: spec.audio_system.music.source,
    cues: spec.audio_system.music.arc.map((c) => ({
      cue: c.cue,
      seconds: [c.from, c.to],
      mood: c.mood,
    })),
  },
  {
    id: "A07",
    kind: "sfx",
    asset_plan_ref: "A07",
    path: "public/sfx/",
    status: dirStatus("public/sfx"),
    required_by: ["NavisLaunch"],
    description: spec.asset_plan.find((a) => a.id === "A07").asset,
    cues: spec.audio_system.sfx.map((s) => ({ t: s.t, sound: s.sound })),
  },
  {
    id: "A08",
    kind: "texture",
    asset_plan_ref: "A08",
    path: "public/images/grain-512.png",
    status: fileStatus("public/images/grain-512.png"),
    required_by: ["all scenes (grain overlay)"],
    description: spec.visual_system.background_treatment.grain,
  },
  {
    id: "A09",
    kind: "approval",
    asset_plan_ref: "A09",
    path: "public/approvals.json",
    status: fileStatus("public/approvals.json"),
    required_by: ["NavisLaunch endingVariant B (U03)", "NavisLaunch endingVariant C (U04)"],
    optional: true,
    description:
      'Created only when an approval is granted. Shape: { "U03": { "approved": true }, "U04": { "approved": true } }',
  },
].map((a) => ({ ...a, spec_status: planStatus[a.asset_plan_ref] }));

const missing = assets.filter((a) => a.status === "missing");
const output = {
  generated_from: "navis_master_cinematic_launch_spec.json",
  spec_version: spec.project.version,
  path_mapping_note:
    "remotion_architecture.directory_structure names public/vo/; this project uses public/voiceover/ (same files, L01.wav ... L21.wav).",
  summary: {
    total: assets.length,
    present: assets.filter((a) => a.status === "present").length,
    missing: missing.length,
    missing_required: missing.filter((a) => !a.optional).length,
  },
  assets,
};

writeFileSync(join(root, "asset_requirements.json"), `${JSON.stringify(output, null, 2)}\n`);
console.log(
  `asset_requirements.json: ${output.summary.total} assets, ${output.summary.present} present, ${output.summary.missing} missing (${output.summary.missing_required} required)`,
);
