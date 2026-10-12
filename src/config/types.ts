import { z } from "zod";

// Zod schemas for the parts of the two source JSON files that the film code
// depends on. `looseObject` keeps every key the schema doesn't name, so the
// parsed spec carries the full document, not a trimmed copy.

export const SCENE_IDS = [
  "S01",
  "S02",
  "S03",
  "S04",
  "S05",
  "S06",
  "S07",
  "S08",
  "S09",
  "S10",
  "S11",
  "S12",
  "S13",
  "S14",
  "S15",
  "S16",
  "S17",
  "S18",
] as const;
export type SceneId = (typeof SCENE_IDS)[number];

export const SCENE_STATUSES = [
  "conceptual",
  "working",
  "local",
  "staging",
  "future",
] as const;
export type SceneStatus = (typeof SCENE_STATUSES)[number];

export const EASING_NAMES = [
  "glide",
  "settle",
  "weighted",
  "exit",
  "drift",
] as const;
export type EasingName = (typeof EASING_NAMES)[number];

export const ENDING_VARIANT_IDS = ["A", "B", "C"] as const;
export type EndingVariantId = (typeof ENDING_VARIANT_IDS)[number];

export const ALTERNATE_IDS = ["ALT_A", "ALT_B", "ALT_C", "ALT_D"] as const;

const easingName = z.enum(EASING_NAMES);
const bezier = z.tuple([z.number(), z.number(), z.number(), z.number()]);
const bezierEasing = z.looseObject({ bezier, use: z.string() });

const cameraKeyframeSchema = z.looseObject({
  f: z.number().int().nonnegative(),
  x: z.number(),
  y: z.number(),
  scale: z.number().positive(),
  easing: easingName,
});
export type CameraKeyframe = z.infer<typeof cameraKeyframeSchema>;

const cursorSchema = z.looseObject({
  // Either normalized recording coordinates or a hand-off note such as
  // "inherits S12 end position".
  start: z.union([z.looseObject({ x: z.number(), y: z.number() }), z.string()]),
  path: z.array(
    z.looseObject({
      to: z.string(),
      from_f: z.number().int().nonnegative(),
      to_f: z.number().int().nonnegative(),
      easing: easingName,
    }),
  ),
  click: z
    .array(z.looseObject({ at_f: z.number().int().nonnegative(), target: z.string() }))
    .nullable(),
});
export type CursorSpec = z.infer<typeof cursorSchema>;

export const sceneSchema = z.looseObject({
  scene_id: z.enum(SCENE_IDS),
  start_time: z.number().nonnegative(),
  end_time: z.number().positive(),
  duration: z.number().positive(),
  start_frame: z.number().int().nonnegative(),
  end_frame: z.number().int().positive(),
  act: z.string(),
  product: z.string(),
  purpose: z.string(),
  narrative_role: z.string(),
  voiceover: z.string(),
  onscreen_text: z.array(z.string()),
  visual_type: z.string(),
  source_asset: z.string(),
  screen_recording: z.union([z.string(), z.array(z.string())]).nullable(),
  camera: z.looseObject({
    keyframes: z.array(cameraKeyframeSchema).min(1),
    motion_blur: z.union([z.boolean(), z.string()]),
  }),
  cursor: cursorSchema.nullable(),
  transition_in: z.string(),
  transition_out: z.string(),
  music: z.string(),
  evidence: z.array(z.string()),
  status: z.enum(SCENE_STATUSES),
  risk: z.string(),
});
export type Scene = z.infer<typeof sceneSchema>;

const typeRoleSchema = z.looseObject({
  role: z.string(),
  family: z.string(),
  weight: z.number(),
  size: z.number().positive(),
  line_height: z.number().optional(),
  tracking_em: z.number().optional(),
  case: z.literal("upper").optional(),
  opacity: z.number().optional(),
});
export type TypeRole = z.infer<typeof typeRoleSchema>;

const windowChromeSchema = z.looseObject({
  radius_px: z.number(),
  titlebar_height_px: z.number(),
  background: z.string(),
});

const compositionSpecSchema = z.looseObject({
  id: z.string(),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  fps: z.number().int().positive().optional(),
  durationInFrames: z.number().int().positive().optional(),
  frame: z.number().int().nonnegative().optional(),
});

export const specSchema = z.looseObject({
  project: z.looseObject({
    id: z.string(),
    title: z.string(),
    version: z.string(),
    runtime_seconds: z.number().positive(),
    fps: z.number().int().positive(),
    total_frames: z.number().int().positive(),
    master_composition: z.looseObject({
      width: z.number().int().positive(),
      height: z.number().int().positive(),
    }),
    deliverables: z.array(
      z.looseObject({
        id: z.string(),
        description: z.string(),
        requires_external_approval: z.boolean(),
      }),
    ),
  }),
  visual_system: z.looseObject({
    color_tokens: z.looseObject({
      ink: z.string(),
      ink_raised: z.string(),
      ink_line: z.string(),
      on_ink_text: z.string(),
      on_ink_muted: z.string(),
      canvas: z.string(),
      surface: z.string(),
      surface_alt: z.string(),
      line: z.string(),
      line_strong: z.string(),
      text: z.string(),
      text_muted: z.string(),
      text_subtle: z.string(),
      navis_blue: z.string(),
      navis_blue_gradient: z.tuple([z.string(), z.string()]),
    }),
    typography: z.looseObject({
      hierarchy_px_at_1080p: z.array(typeRoleSchema),
    }),
    window_chrome: z.looseObject({
      terminal: windowChromeSchema,
      browser: windowChromeSchema,
    }),
    safe_areas: z.looseObject({
      title_safe_px: z.looseObject({ x: z.number(), y: z.number() }),
    }),
  }),
  motion_system: z.looseObject({
    easings: z.looseObject({
      glide: bezierEasing,
      settle: bezierEasing,
      weighted: bezierEasing,
      exit: bezierEasing,
      drift: bezierEasing,
      spring_ui: z.looseObject({
        remotion_spring: z.looseObject({
          damping: z.number(),
          stiffness: z.number(),
          mass: z.number(),
        }),
      }),
    }),
    transition_language: z.array(
      z.looseObject({
        id: z.string().regex(/^T_[A-Z_]+$/),
        frames: z.number().int().nonnegative(),
        used: z.array(z.string()),
      }),
    ),
  }),
  voiceover: z.looseObject({
    selected: z.string(),
    // The selected version is split into lines; alternates are prose drafts.
    versions: z.record(
      z.string(),
      z.looseObject({
        lines: z
          .array(z.looseObject({ id: z.string(), text: z.string() }))
          .optional(),
        text: z.string().optional(),
      }),
    ),
    timing: z.array(
      z.looseObject({
        line: z.string(),
        scene: z.enum(SCENE_IDS),
        start: z.number().nonnegative(),
        end: z.number().positive(),
      }),
    ),
  }),
  onscreen_copy: z.looseObject({
    deck: z.array(
      z.looseObject({
        id: z.string(),
        scene: z.string(),
        text: z.string(),
        style: z.string(),
      }),
    ),
  }),
  audio_system: z.looseObject({
    music: z.looseObject({
      arc: z.array(
        z.looseObject({
          cue: z.string(),
          from: z.number(),
          to: z.number(),
          level: z.number(),
        }),
      ),
    }),
    sfx: z.array(z.looseObject({ t: z.number(), sound: z.string() })),
  }),
  announcement: z.looseObject({
    ending_variants: z.array(
      z.looseObject({
        id: z.enum(ENDING_VARIANT_IDS),
        name: z.string(),
        requires_external_approval: z.boolean(),
        approval_ref: z.string().optional(),
        end_card: z.record(z.string(), z.string()),
        legal_line: z.string(),
      }),
    ),
  }),
  alternates: z.array(
    z.looseObject({
      id: z.string(),
      name: z.string(),
      status: z.string(),
      recording: z.string().optional(),
    }),
  ),
  verified_features: z.array(
    z.looseObject({
      feature_id: z.string(),
      name: z.string(),
      status: z.string(),
      audit_reference: z.string().nullable(),
    }),
  ),
  claims: z.array(z.looseObject({ claim_id: z.string() })),
  recording_plan: z.looseObject({
    recordings: z.array(z.looseObject({ id: z.string(), product: z.string() })),
  }),
  asset_plan: z.array(
    z.looseObject({ id: z.string(), asset: z.string(), status: z.string() }),
  ),
  unresolved_items: z.array(
    z.looseObject({
      id: z.string(),
      item: z.string(),
      owner: z.string(),
      blocking: z.string(),
    }),
  ),
  scene_order: z.array(z.enum(SCENE_IDS)),
  scene_status_definitions: z.record(z.string(), z.string()),
  scenes: z.array(sceneSchema),
  remotion_architecture: z.looseObject({
    compositions: z.array(compositionSpecSchema),
  }),
});
export type Spec = z.infer<typeof specSchema>;

export const auditSchema = z.looseObject({
  audit_meta: z.looseObject({
    date: z.string(),
    status_vocabulary: z.record(z.string(), z.string()),
  }),
  implemented: z.looseObject({}),
  mocked_or_stubbed: z.array(z.unknown()),
  planned_not_implemented: z.array(z.unknown()),
  top_10_technically_interesting_features: z.array(
    z.looseObject({ name: z.string(), status: z.string() }),
  ),
});
export type Audit = z.infer<typeof auditSchema>;

// Every scene component receives the same props so the master composition can
// render them from one map. Only S17 (end card) reads the ending variant.
export type SceneProps = {
  readonly endingVariant: EndingVariantId;
};
