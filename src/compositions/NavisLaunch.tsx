import { z } from "zod";
import {
  AbsoluteFill,
  type CalculateMetadataFunction,
  getStaticFiles,
  staticFile,
} from "remotion";
import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { wipe } from "@remotion/transitions/wipe";
import "../config/fonts";
import { missingFinalAudio } from "../config/audioMap";
import { BRAND } from "../config/navisBrand";
import { colors } from "../config/design";
import { getEndingVariant } from "../config/loadSpec";
import { endFrame, FILM_SCENES, type FilmScene, startFrame } from "../config/timeline";
import { ALTERNATE_IDS, ENDING_VARIANT_IDS } from "../config/types";
import { AudioLayer, DevHud } from "../components/AudioLayer";
import { DevModeProvider } from "../components/DevMode";
import { SCENE_COMPONENTS } from "../scenes";

// remotion_architecture.compositions[NavisLaunch].props_schema, plus the
// film mode (see components/DevMode.tsx): 'development' shows the HUD,
// 'preview' is clean with temp audio allowed, 'final' requires final audio.
export const navisLaunchSchema = z.object({
  endingVariant: z.enum(ENDING_VARIANT_IDS),
  useAlternates: z.array(z.enum(ALTERNATE_IDS)),
  mode: z.enum(["development", "preview", "final"]),
  // Audio QC only: render one stem (voice / music / sfx) on its own; default is the full mix.
  stem: z.enum(["mix", "voice", "music", "sfx", "room"]).optional(),
});
export type NavisLaunchProps = z.infer<typeof navisLaunchSchema>;

const transitionFor = (key: string, t: FilmScene["transitionOut"]) => {
  const timing = linearTiming({ durationInFrames: t.frames });
  return t.type === "wipe" ? (
    <TransitionSeries.Transition key={key} presentation={wipe({ direction: t.direction ?? "from-bottom" })} timing={timing} />
  ) : (
    <TransitionSeries.Transition key={key} presentation={fade()} timing={timing} />
  );
};

/**
 * Scenes in a TransitionSeries. Each sequence lasts its scene length plus its
 * outgoing transition, and the transition overlaps the next scene's first
 * frames — so every scene's local frame 0 is still its nominal start (the
 * clock `useSceneClock` relies on) and the total stays exactly FILM_FRAMES.
 * World changes wipe (dark → light from below, light → dark from above);
 * changes within a world fade; macro edits inside one take are cuts.
 */
export const NavisLaunch: React.FC<NavisLaunchProps> = ({ mode, stem = "mix" }) => (
  <DevModeProvider value={mode}>
    <AbsoluteFill style={{ backgroundColor: colors.ink }}>
      <TransitionSeries>
        {FILM_SCENES.flatMap((scene) => {
          const SceneComponent = SCENE_COMPONENTS[scene.id];
          const t = scene.transitionOut;
          const len = endFrame(scene) - startFrame(scene);
          const items = [
            <TransitionSeries.Sequence key={scene.id} name={`${scene.id} · ${scene.beat}`} durationInFrames={len + (t.type === "none" ? 0 : t.frames)}>
              <SceneComponent endingVariant="A" />
            </TransitionSeries.Sequence>,
          ];
          if (t.type !== "none" && t.frames > 0) {
            items.push(transitionFor(`${scene.id}-out`, t));
          }
          return items;
        })}
      </TransitionSeries>
      <AudioLayer stem={stem} />
      {mode === "development" ? <DevHud /> : null}
    </AbsoluteFill>
  </DevModeProvider>
);

// approvals.json (asset A09) is created only when an approval is granted:
// { "U03": { "approved": true, ... }, "U04": { "approved": true, ... } }
const approvalsSchema = z.record(
  z.string(),
  z.looseObject({ approved: z.boolean() }),
);

/**
 * Render guards from remotion_architecture.guards. Variants B and C fail
 * closed: no approvals file, an unreadable one, or approved !== true all throw.
 */
export const calculateNavisLaunchMetadata: CalculateMetadataFunction<
  NavisLaunchProps
> = async ({ props }) => {
  const variant = getEndingVariant(props.endingVariant);
  if (variant.requires_external_approval) {
    const ref = variant.approval_ref ?? "(none)";
    const denied = `Ending variant ${variant.id} ("${variant.name}") requires approvals.json to approve ${ref}.`;
    const response = await fetch(staticFile("approvals.json")).catch(() => null);
    if (!response?.ok) {
      throw new Error(`${denied} public/approvals.json does not exist (asset A09).`);
    }
    const approvals = approvalsSchema.safeParse(
      await response.json().catch(() => null),
    );
    if (!approvals.success || approvals.data[ref]?.approved !== true) {
      throw new Error(denied);
    }
  }

  if (props.mode === "final") {
    const missing = missingFinalAudio();
    if (!getStaticFiles().some((f) => f.name === BRAND.logo)) missing.push(`logo (public/${BRAND.logo})`);
    if (missing.length > 0) {
      throw new Error(
        `A final render needs final audio and the logo. Missing ${missing.length}:\n- ${missing.join("\n- ")}\nRender with mode "preview" for a temp-audio preview.`,
      );
    }
  }

  if (props.useAlternates.length > 0) {
    throw new Error(
      `Alternates (${props.useAlternates.join(", ")}) are not built yet; ALT_A also changes the runtime.`,
    );
  }

  return {};
};
