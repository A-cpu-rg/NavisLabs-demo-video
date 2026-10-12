// The two JSON files at the project root are read-only snapshots copied from
// the Devtool repo. They are the single source of truth for the film; nothing
// in this project writes to them.
import specJson from "../../navis_master_cinematic_launch_spec.json";
import auditJson from "../../navis_code_audit.json";
import type { EndingVariantId, Scene, SceneId } from "./types";
import { validateSpec } from "./validateSpec";

// Throws at module load if the spec is invalid, so Studio and every render
// fail loudly instead of drawing a film from inconsistent data.
const validated = validateSpec(specJson as unknown, auditJson as unknown);

for (const warning of validated.warnings) {
  console.warn(`[spec] ${warning}`);
}

export const spec = validated.spec;
export const audit = validated.audit;
export const specWarnings = validated.warnings;
export const timelineSummary = validated.summary;

export const getScene = (id: SceneId): Scene => {
  const scene = spec.scenes.find((s) => s.scene_id === id);
  if (!scene) throw new Error(`Scene ${id} is not in the master spec`);
  return scene;
};

export const getCompositionSpec = (id: string) => {
  const comp = spec.remotion_architecture.compositions.find((c) => c.id === id);
  if (!comp) throw new Error(`Composition ${id} is not in remotion_architecture`);
  return comp;
};

export const getEndingVariant = (id: EndingVariantId) => {
  const variant = spec.announcement.ending_variants.find((v) => v.id === id);
  if (!variant) throw new Error(`Ending variant ${id} is not in the spec`);
  return variant;
};
