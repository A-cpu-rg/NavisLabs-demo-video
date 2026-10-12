// The production blueprint is the shot-level instruction for every scene.
// It is read-only data: scenes read it by id instead of copying values into
// React. The master spec stays the timing authority, so loading fails if the
// two ever disagree about where a scene starts or ends.
import { z } from "zod";
import blueprintJson from "../../navis_launch_production_blueprint.json";
import { spec } from "./loadSpec";
import { EASING_NAMES, SCENE_IDS, type SceneId } from "./types";

const keyframeSchema = z.looseObject({
  f: z.number().int().nonnegative(),
  x: z.number(),
  y: z.number(),
  scale: z.number().positive(),
  easing: z.enum(EASING_NAMES),
  note: z.string().optional(),
});
export type BlueprintKeyframe = z.infer<typeof keyframeSchema>;

const textSchema = z.looseObject({
  id: z.string(),
  text: z.string(),
  role: z.enum([
    "statement",
    "wordmark",
    "title_mono",
    "caption_mono",
    "label_mono_small",
    "legal",
  ]),
  in_f: z.number().int().nonnegative(),
  out_f: z.number().int().nullable(),
  position: z.string(),
});
export type BlueprintText = z.infer<typeof textSchema>;

const secondaryTextSchema = z.looseObject({
  id: z.string(),
  text: z.string().optional(),
  in_f: z.number().optional(),
  highlight_f: z.number().optional(),
  opacity: z.number().optional(),
});

const shotSchema = z.looseObject({
  shot_id: z.string(),
  local_frames: z.tuple([z.number().int(), z.number().int()]),
  real_screen_to_record: z.string().nullable(),
});
export type BlueprintShot = z.infer<typeof shotSchema>;

const sceneSchema = z.looseObject({
  scene_id: z.enum(SCENE_IDS),
  start_frame: z.number().int(),
  end_frame: z.number().int(),
  recording_id: z.array(z.string()),
  recording_id_conditional: z.array(z.string()),
  on_screen_text: z.array(textSchema),
  on_screen_text_secondary: z.array(secondaryTextSchema),
  shots: z.array(shotSchema).min(1),
  zoom_target: z.string(),
  proof_level: z.enum([
    "LIVE_VERIFIED",
    "REAL_PRODUCT_RECORDING",
    "ABSTRACTED_PRODUCT_CONCEPT",
    "CONCEPTUAL",
    "FUTURE",
  ]),
});
export type BlueprintScene = z.infer<typeof sceneSchema>;

const cursorPointSchema = z.looseObject({ x: z.number(), y: z.number() });
const cursorSceneSchema = z.looseObject({
  scene_id: z.enum(SCENE_IDS),
  start: z.union([cursorPointSchema, z.string()]).nullable(),
  path: z
    .array(
      z.looseObject({
        to: z.string(),
        from_f: z.number().int(),
        to_f: z.number().int(),
        easing: z.enum(EASING_NAMES),
        curve: z.string().optional(),
      }),
    )
    .nullable(),
  click: z.array(z.looseObject({ at_f: z.number().int(), target: z.string() })).nullable(),
  exit: z.string().nullable(),
});
export type BlueprintCursor = z.infer<typeof cursorSceneSchema>;

const blueprintSchema = z.looseObject({
  voiceover_line_map: z.array(
    z.looseObject({
      line_id: z.string().regex(/^L\d{2}$/),
      scene_id: z.enum(SCENE_IDS),
      text: z.string(),
      start_frame: z.number().int(),
      end_frame: z.number().int(),
      hard_latest_end_s: z.number(),
      asset_id: z.string(),
    }),
  ),
  // Legacy plan (read-only file): its own 17 scenes; the film now has 18.
  scene_timeline: z.array(sceneSchema).length(17),
  camera_plan: z.array(
    z.looseObject({
      scene_id: z.enum(SCENE_IDS),
      keyframes: z.array(keyframeSchema).min(1),
      motion_blur: z.union([z.boolean(), z.string()]),
    }),
  ),
  cursor_plan: z.looseObject({ scenes: z.array(cursorSceneSchema) }),
  sound_design: z.looseObject({
    events: z.array(
      z.looseObject({
        event_id: z.string(),
        frame: z.number().int(),
        scene_id: z.enum(SCENE_IDS),
        sound: z.string(),
        level: z.string(),
        asset_id: z.string(),
      }),
    ),
  }),
  music_plan: z.looseObject({
    cues: z.array(
      z.looseObject({ cue: z.string(), from_frame: z.number().int(), to_frame: z.number().int() }),
    ),
    silences_and_drops: z.array(
      z.looseObject({ from: z.number(), to: z.number(), what: z.string() }),
    ),
  }),
  asset_manifest: z.array(
    z.looseObject({
      asset_id: z.string(),
      type: z.string(),
      required: z.boolean(),
      file_path: z.string().nullable(),
      description: z.string(),
    }),
  ),
  screen_recording_plan: z.looseObject({
    recordings: z.array(
      z.looseObject({
        recording_id: z.string(),
        recording_name: z.string(),
        required: z.boolean(),
      }),
    ),
  }),
});

const parsed = blueprintSchema.safeParse(blueprintJson as unknown);
if (!parsed.success) {
  throw new Error(
    `navis_launch_production_blueprint.json does not match the schema:\n${z.prettifyError(parsed.error)}`,
  );
}
export const blueprint = parsed.data;

// The master spec is the timing authority.
for (const scene of blueprint.scene_timeline) {
  const master = spec.scenes.find((s) => s.scene_id === scene.scene_id);
  if (
    !master ||
    master.start_frame !== scene.start_frame ||
    master.end_frame !== scene.end_frame
  ) {
    throw new Error(
      `Blueprint ${scene.scene_id} frames ${scene.start_frame}–${scene.end_frame} differ from the master spec`,
    );
  }
}

const byId = <T extends { scene_id: string }>(list: readonly T[], id: SceneId): T => {
  const found = list.find((x) => x.scene_id === id);
  if (!found) throw new Error(`Blueprint has no entry for ${id}`);
  return found;
};

export const blueprintScene = (id: SceneId) => byId(blueprint.scene_timeline, id);
export const cameraPlan = (id: SceneId) => byId(blueprint.camera_plan, id);
export const cursorPlan = (id: SceneId) => byId(blueprint.cursor_plan.scenes, id);

export const sceneText = (id: SceneId, textId: string): BlueprintText => {
  const text = blueprintScene(id).on_screen_text.find((t) => t.id === textId);
  if (!text) throw new Error(`${id} has no on-screen text ${textId}`);
  return text;
};

export const secondaryText = (id: SceneId) => blueprintScene(id).on_screen_text_secondary;

// "first 10 frames only (…)" / "frames 0–20 only" -> 10 / 20; false -> 0.
export const motionBlurFrames = (id: SceneId): number => {
  const value = cameraPlan(id).motion_blur;
  if (value === false) return 0;
  if (value === true) throw new Error(`${id}: motion_blur must name its frames`);
  const match = value.match(/first (\d+) frames|frames \d+[–-](\d+)/);
  if (!match) throw new Error(`${id}: cannot read motion_blur "${value}"`);
  return Number(match[1] ?? match[2]);
};

export const recordingName = (rid: string): string =>
  blueprint.screen_recording_plan.recordings.find((r) => r.recording_id === rid)
    ?.recording_name ?? rid;
