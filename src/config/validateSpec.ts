import { z } from "zod";
import {
  type Audit,
  auditSchema,
  SCENE_IDS,
  type Spec,
  specSchema,
} from "./types";

export type TimelineSummary = {
  readonly sceneCount: number;
  readonly firstScene: string;
  readonly lastScene: string;
  readonly fps: number;
  readonly totalFrames: number;
  readonly width: number;
  readonly height: number;
  readonly gaps: number;
  readonly overlaps: number;
};

export type ValidatedSpec = {
  readonly spec: Spec;
  readonly audit: Audit;
  readonly warnings: readonly string[];
  readonly summary: TimelineSummary;
};

// Leading transition id of fields such as "T_ZOOM_THROUGH (18 f, ...)".
export const parseTransitionId = (raw: string): string | null =>
  raw.match(/^T_[A-Z_]+/)?.[0] ?? null;

// The spec writes VO references as "L8 (begins)", "L3, L4", etc.
const parseVoLines = (raw: string): string[] => raw.match(/\bL\d+\b/g) ?? [];

const asList = (value: string | string[] | null): string[] =>
  value === null ? [] : Array.isArray(value) ? value : [value];

// Resolves "navis_code_audit.json#/a/b/0" against the audit document.
const resolveAuditPointer = (audit: unknown, ref: string): unknown => {
  const [file, pointer] = ref.split("#");
  if (file !== "navis_code_audit.json" || pointer === undefined) {
    return undefined;
  }
  let node: unknown = audit;
  for (const raw of pointer.split("/").slice(1)) {
    const key = raw.replace(/~1/g, "/").replace(/~0/g, "~");
    if (Array.isArray(node)) {
      node = node[Number(key)];
    } else if (node !== null && typeof node === "object") {
      node = (node as Record<string, unknown>)[key];
    } else {
      return undefined;
    }
  }
  return node;
};

const nearlyEqual = (a: number, b: number) => Math.abs(a - b) < 1e-6;

/**
 * Parses both source documents and checks that the master spec is internally
 * consistent and never claims more than the code audit supports.
 * Throws with every error at once; returns non-blocking warnings.
 */
export const validateSpec = (
  rawSpec: unknown,
  rawAudit: unknown,
): ValidatedSpec => {
  const specParse = specSchema.safeParse(rawSpec);
  const auditParse = auditSchema.safeParse(rawAudit);
  if (!specParse.success || !auditParse.success) {
    const parts = [];
    if (!specParse.success) {
      parts.push(
        `navis_master_cinematic_launch_spec.json does not match the schema:\n${z.prettifyError(specParse.error)}`,
      );
    }
    if (!auditParse.success) {
      parts.push(
        `navis_code_audit.json does not match the schema:\n${z.prettifyError(auditParse.error)}`,
      );
    }
    throw new Error(parts.join("\n\n"));
  }

  const spec = specParse.data;
  const audit = auditParse.data;
  const errors: string[] = [];
  const warnings: string[] = [];
  const { fps, total_frames, runtime_seconds, master_composition } =
    spec.project;

  // Project format
  if (total_frames !== Math.round(runtime_seconds * fps)) {
    errors.push(
      `project.total_frames ${total_frames} != runtime_seconds ${runtime_seconds} x fps ${fps}`,
    );
  }

  // Scene order: the code has exactly one component per id in SCENE_IDS.
  const ids = spec.scenes.map((s) => s.scene_id);
  // The legacy master spec (navis_master_cinematic_launch_spec.json, read-only)
  // keeps its own 17-scene plan; the film's timeline now comes from
  // navislabs_v8_film_spec.json (18 scenes). Check the legacy file only
  // against its own ids: S01..S17 in order.
  const LEGACY_IDS = SCENE_IDS.filter((id) => id !== "S18");
  if (ids.join() !== LEGACY_IDS.join()) {
    errors.push(`scenes must run ${LEGACY_IDS.join(", ")}; got ${ids.join(", ")}`);
  }
  if (spec.scene_order.join() !== ids.join()) {
    errors.push(`scene_order (${spec.scene_order.join(", ")}) != scenes order`);
  }

  // Timeline: contiguous, no gaps or overlaps, frames match seconds.
  let gaps = 0;
  let overlaps = 0;
  let cursor = 0;
  for (const scene of spec.scenes) {
    const id = scene.scene_id;
    if (scene.start_frame > cursor) {
      gaps++;
      errors.push(`${id}: gap of ${scene.start_frame - cursor} frames before it`);
    } else if (scene.start_frame < cursor) {
      overlaps++;
      errors.push(`${id}: overlaps the previous scene by ${cursor - scene.start_frame} frames`);
    }
    if (scene.end_frame <= scene.start_frame) {
      errors.push(`${id}: end_frame ${scene.end_frame} <= start_frame ${scene.start_frame}`);
    }
    if (scene.start_frame !== Math.round(scene.start_time * fps)) {
      errors.push(`${id}: start_frame ${scene.start_frame} != start_time ${scene.start_time}s`);
    }
    if (scene.end_frame !== Math.round(scene.end_time * fps)) {
      errors.push(`${id}: end_frame ${scene.end_frame} != end_time ${scene.end_time}s`);
    }
    if (!nearlyEqual(scene.duration, scene.end_time - scene.start_time)) {
      errors.push(`${id}: duration ${scene.duration}s != end_time - start_time`);
    }
    cursor = scene.end_frame;
  }
  if (spec.scenes[0]?.start_frame !== 0) {
    errors.push("first scene must start at frame 0");
  }
  if (cursor !== total_frames) {
    errors.push(`last scene ends at ${cursor}, project.total_frames is ${total_frames}`);
  }

  // Camera keyframes: strictly increasing, inside the scene.
  for (const scene of spec.scenes) {
    const length = scene.end_frame - scene.start_frame;
    scene.camera.keyframes.forEach((kf, i, all) => {
      if (kf.f > length) {
        errors.push(`${scene.scene_id}: camera keyframe f=${kf.f} is past the scene length ${length}`);
      }
      if (i > 0 && kf.f <= all[i - 1].f) {
        errors.push(`${scene.scene_id}: camera keyframes must be strictly increasing in f`);
      }
    });
  }

  // On-screen copy: every O-id a scene uses exists and belongs to that scene.
  const deck = new Map(spec.onscreen_copy.deck.map((o) => [o.id, o]));
  const usedCopy = new Set<string>();
  for (const scene of spec.scenes) {
    for (const ref of scene.onscreen_text) {
      if (!/^O\d+$/.test(ref)) {
        warnings.push(`${scene.scene_id}: on-screen text "${ref}" is not a deck id; resolved from the spec at build time`);
        continue;
      }
      usedCopy.add(ref);
      const entry = deck.get(ref);
      if (!entry) {
        errors.push(`${scene.scene_id}: on-screen text ${ref} is missing from onscreen_copy.deck`);
      } else if (entry.scene !== scene.scene_id) {
        errors.push(`${scene.scene_id}: on-screen text ${ref} belongs to ${entry.scene}`);
      }
    }
  }
  for (const id of deck.keys()) {
    if (!usedCopy.has(id)) warnings.push(`onscreen_copy.deck ${id} is not used by any scene`);
  }

  // Voiceover: selected version exists, timings sit inside their scenes.
  const selected = spec.voiceover.versions[spec.voiceover.selected];
  const lineIds = new Set(selected?.lines?.map((l) => l.id) ?? []);
  if (!selected?.lines) {
    errors.push(`voiceover.selected "${spec.voiceover.selected}" is not a version with lines`);
  }
  const scenesById = new Map(spec.scenes.map((s) => [s.scene_id, s]));
  let previousVoEnd = 0;
  for (const t of spec.voiceover.timing) {
    if (!lineIds.has(t.line)) {
      errors.push(`voiceover.timing ${t.line} is not a line in the selected version`);
    }
    const scene = scenesById.get(t.scene);
    if (scene && (t.start < scene.start_time || t.start >= scene.end_time)) {
      errors.push(`${t.line} starts at ${t.start}s, outside ${t.scene}`);
    }
    if (t.end <= t.start || t.end > runtime_seconds) {
      errors.push(`${t.line}: invalid window ${t.start}-${t.end}s`);
    }
    if (t.start < previousVoEnd) {
      errors.push(`${t.line} overlaps the previous VO line`);
    }
    previousVoEnd = t.end;
  }
  for (const scene of spec.scenes) {
    for (const line of parseVoLines(scene.voiceover)) {
      if (!lineIds.has(line)) {
        errors.push(`${scene.scene_id}: voiceover ${line} is not in the selected version`);
      }
    }
  }

  // Transitions: catalogued ids exist; out of N matches in of N+1.
  const transitions = new Set(spec.motion_system.transition_language.map((t) => t.id));
  spec.scenes.forEach((scene, i) => {
    const outId = parseTransitionId(scene.transition_out);
    if (outId && !transitions.has(outId)) {
      errors.push(`${scene.scene_id}: transition_out ${outId} is not in transition_language`);
    }
    if (!outId) {
      warnings.push(`${scene.scene_id}: transition_out "${scene.transition_out}" is not a catalogued transition (0-frame overlap assumed)`);
    }
    const next = spec.scenes[i + 1];
    const nextInId = next ? parseTransitionId(next.transition_in) : null;
    if (next && outId !== nextInId) {
      warnings.push(`${scene.scene_id} -> ${next.scene_id}: transition_out "${scene.transition_out}" vs transition_in "${next.transition_in}"`);
    }
  });

  // Status and evidence: no scene claims more than its features support.
  const features = new Map(spec.verified_features.map((f) => [f.feature_id, f]));
  const claims = new Set(spec.claims.map((c) => c.claim_id));
  for (const scene of spec.scenes) {
    if (!(scene.status in spec.scene_status_definitions)) {
      warnings.push(`${scene.scene_id}: status "${scene.status}" has no entry in scene_status_definitions`);
    }
    for (const ref of scene.evidence) {
      if (/^C\d+$/.test(ref) && !claims.has(ref)) {
        errors.push(`${scene.scene_id}: evidence ${ref} is not in claims`);
      }
      if (!/^F\d+$/.test(ref)) continue;
      const feature = features.get(ref);
      if (!feature) {
        errors.push(`${scene.scene_id}: evidence ${ref} is not in verified_features`);
      } else if (scene.status === "working" && feature.status !== "working") {
        errors.push(`${scene.scene_id} is "working" but cites ${ref} with status "${feature.status}"`);
      } else if (
        scene.status !== "future" &&
        ["planned", "unknown", "future"].includes(feature.status)
      ) {
        errors.push(`${scene.scene_id} presents ${ref} ("${feature.status}") as present-tense`);
      }
    }
    if (scene.status === "future") {
      const labelled = scene.onscreen_text.some((ref) => deck.get(ref)?.text === "NEXT");
      if (!labelled) errors.push(`${scene.scene_id} is "future" but carries no NEXT label`);
    }
  }

  // Every verified feature points at a real node in the code audit, and a
  // feature the audit marks as mock is never shown as real.
  for (const feature of spec.verified_features) {
    if (feature.audit_reference === null) continue;
    const node = resolveAuditPointer(rawAudit, feature.audit_reference);
    if (node === undefined) {
      errors.push(`${feature.feature_id}: audit_reference ${feature.audit_reference} does not resolve`);
    } else if (
      node !== null &&
      typeof node === "object" &&
      (node as { status?: unknown }).status === "mock" &&
      ["working", "local", "staging"].includes(feature.status)
    ) {
      errors.push(`${feature.feature_id} is "${feature.status}" but the audit marks it mock`);
    }
  }

  // Recordings referenced by scenes and alternates exist in the plan.
  const recordings = new Set(spec.recording_plan.recordings.map((r) => r.id));
  for (const scene of spec.scenes) {
    for (const id of asList(scene.screen_recording)) {
      if (!recordings.has(id)) errors.push(`${scene.scene_id}: recording ${id} is not in recording_plan`);
    }
  }
  for (const alt of spec.alternates) {
    if (alt.recording && !recordings.has(alt.recording)) {
      errors.push(`${alt.id}: recording ${alt.recording} is not in recording_plan`);
    }
  }

  // Compositions declared by remotion_architecture.
  const comps = new Map(spec.remotion_architecture.compositions.map((c) => [c.id, c]));
  const launch = comps.get("NavisLaunch");
  if (
    !launch ||
    launch.width !== master_composition.width ||
    launch.height !== master_composition.height ||
    launch.fps !== fps ||
    launch.durationInFrames !== total_frames
  ) {
    errors.push("remotion_architecture NavisLaunch must match project fps, size and total_frames");
  }
  const vertical = comps.get("NavisLaunchVertical");
  if (!vertical?.fps || !vertical.durationInFrames) {
    errors.push("remotion_architecture NavisLaunchVertical needs fps and durationInFrames");
  }
  const poster = comps.get("NavisPoster");
  if (poster?.frame === undefined || poster.frame >= total_frames) {
    errors.push("remotion_architecture NavisPoster needs a frame inside the master");
  }

  // Ending variants: A is the safe default; B and C name their approval.
  const unresolved = new Set(spec.unresolved_items.map((u) => u.id));
  for (const variant of spec.announcement.ending_variants) {
    if (variant.id === "A" && variant.requires_external_approval) {
      errors.push("ending variant A must not require external approval");
    }
    if (
      variant.requires_external_approval &&
      (!variant.approval_ref || !unresolved.has(variant.approval_ref))
    ) {
      errors.push(`ending variant ${variant.id} needs an approval_ref listed in unresolved_items`);
    }
  }

  // Music arc covers the runtime without gaps (warning only: a mix decision).
  let musicCursor = 0;
  for (const cue of spec.audio_system.music.arc) {
    if (!nearlyEqual(cue.from, musicCursor)) {
      warnings.push(`music cue ${cue.cue} starts at ${cue.from}s, previous ended at ${musicCursor}s`);
    }
    musicCursor = cue.to;
  }

  if (errors.length > 0) {
    throw new Error(
      `Master spec validation failed (${errors.length}):\n- ${errors.join("\n- ")}`,
    );
  }

  return {
    spec,
    audit,
    warnings,
    summary: {
      sceneCount: spec.scenes.length,
      firstScene: ids[0],
      lastScene: ids[ids.length - 1],
      fps,
      totalFrames: cursor,
      width: master_composition.width,
      height: master_composition.height,
      gaps,
      overlaps,
    },
  };
};
