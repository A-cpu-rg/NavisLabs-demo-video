import { z } from "zod";
import rawSpec from "../../navislabs_v8_film_spec.json";
import type { SceneId } from "./types";

// navislabs_v8_film_spec.json (built by scripts/build-film-data-v8.py) carries
// scene timing, every on-screen beat, typing runs and the film's copy — all
// derived from the founder's measured voiceover (the master clock). Words live
// in src/data/navislabs_v8_copy.json; run npm run data:build, re-render.

const BEAT_KEYS = [
  "runComplete",
  "memoryPoint", "memoryLine",
  "signalDecision", "signalCustomer", "signalCommitment", "signalMeeting", "signalContext",
  "scatter", "tilesSettle", "problem",
  "peopleStart", "copy1", "copy2", "copy3", "agentsStart",
  "taskPreview", "questionCard", "blackout",
  "logoTile", "logoWord", "logoLine", "toLight", "iconsIn", "signalsOut", "understanding", "entitiesIn",
  "appRise", "whatChanged", "waiting", "backToCard",
  "whyClick", "whyOpen", "evidence0", "evidence1", "evidence2", "evidence3", "freshness", "youCanDo",
  "whyClose", "reviewReplyClick", "drawerOpen", "reviewDraftClick", "preparing", "draftShown",
  "selectStart", "selectEnd", "caption", "approveHover", "approveClick",
  "approved", "sending", "gmailAccepted", "replySent",
  "devCut", "devCaption", "agentEnter", "agentRead", "agentNeeds",
  "contextCall", "contextResult", "contextSource", "contextFresh",
  "dayOne", "dayTwo", "restore", "restoreTask", "restoreDecisions", "restoreOpen",
  "permAuthorized", "permDenied", "refusal",
  "agentUses", "agentDone", "runs",
  "notChatbot", "notAutomation", "heroIn", "sharedSignal", "sharedUnderstanding",
  "modelsChange", "agentsChange", "yours", "wordsIn", "collapse",
  "endLockup", "endProducts", "endUnderstanding", "endUrl", "fadeOut",
  // v3
  "archApp", "archDev", "roadmapIn", "glance", "priorityFocus",
  "connectIn", "surfaceMcp", "surfaceApi", "surfaceSdk", "surfaceCli", "mcpCommand",
  "sdkIn", "apiIn", "modelNeutral", "permIdentity", "runOpen", "runTimeline",
  "sameFacts", "sameSources", "sameFreshness",
  "toolsChange", "clientsIn", "loopIn", "pillars", "endTagline",
  // v4
  "intelIn", "prioritiesIn", "evidence4", "evidence5", "explodeIn", "resolveIn", "proofRail",
  "mcpAdd", "mcpAdded", "mcpList", "mcpConnected", "agentReason",
  "sdkInstalled", "sdkCode", "apiResponse", "permOwnScope", "runRow", "runOutcome",
  "peopleAgents",
  // v4 picture lock
  "orgIn", "expandIn", "flowMemory", "flowContext", "flowIntel", "flowDecision", "flowExecution", "flowOutcome", "flowLearning",
  "membersIn", "addMember", "invited",
  "soloIn", "soloPick", "soloWorkspace", "soloCheckpoint", "soloCheckpointOk", "soloDayTwo", "soloRestore", "soloSections",
  // v5 narrative
  "truthLabels", "truthPeople", "truthAgent", "truthDiff", "signalAccount", "staysYours", "recordIn",
  // v6 (voice clock, launch state)
  "signalCrm", "signalJira", "signalKnowledge", "evidence6", "acrossIn", "teamIn",
] as const;
export type BeatKey = (typeof BEAT_KEYS)[number];

const TYPING_KEYS = ["taskPreview", "agentTask", "humanEdit", "mcpList", "sdkInstall"] as const;
export type TypingKey = (typeof TYPING_KEYS)[number];

const sceneId = z.enum(["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S12", "S13", "S14", "S15", "S16", "S17", "S18"]);
const transition = z.object({ type: z.enum(["none", "fade", "wipe"]), frames: z.number().int().nonnegative(), direction: z.enum(["from-top", "from-bottom", "from-left", "from-right"]).nullable() });

const schema = z.looseObject({
  format: z.object({ width: z.literal(1920), height: z.literal(1080), fps: z.literal(30), duration_s: z.number().min(60).max(180), frames: z.number().int().positive() }),
  scenes: z.array(z.object({ id: sceneId, from_s: z.number(), to_s: z.number(), overlap_frames: z.number().int().nonnegative(), transition_out: transition, beat: z.string(), act: z.string() })).length(18),
  timing: z.object({
    beats: z.record(z.string(), z.number()),
    typing: z.record(z.string(), z.object({ start: z.number(), text: z.string().min(1), cps: z.number().positive() })),
  }),
  onscreen_copy: z.record(z.string(), z.string()),
  voiceover: z.looseObject({ ids: z.array(z.string()) }),
});

const parsed = schema.safeParse(rawSpec);
if (!parsed.success) throw new Error(`navislabs_v8_film_spec.json is invalid:\n${z.prettifyError(parsed.error)}`);
export const filmSpec = parsed.data;

for (const k of BEAT_KEYS) {
  if (typeof filmSpec.timing.beats[k] !== "number") throw new Error(`Spec timing.beats is missing "${k}"`);
}
for (const k of TYPING_KEYS) {
  if (!filmSpec.timing.typing[k]) throw new Error(`Spec timing.typing is missing "${k}"`);
}

export const SPEC_BEATS = filmSpec.timing.beats as Record<BeatKey, number>;
export const SPEC_TYPING = filmSpec.timing.typing as Record<TypingKey, { start: number; text: string; cps: number }>;
export type SpecTransition = z.infer<typeof transition>;
export const SPEC_SCENES = filmSpec.scenes as readonly { id: SceneId; from_s: number; to_s: number; overlap_frames: number; transition_out: SpecTransition; beat: string; act: string }[];

/** The film's own on-screen copy, by id. */
export const copy = (id: string): string => {
  const v = filmSpec.onscreen_copy[id];
  if (v === undefined) throw new Error(`onscreen_copy "${id}" is not in navislabs_v8_film_spec.json`);
  return v;
};
