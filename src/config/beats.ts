import { filmSpec, SPEC_BEATS, SPEC_TYPING, type TypingKey } from "./filmSpec";

// Every on-screen beat (absolute seconds) comes from
// navislabs_v8_film_spec.json → timing.beats (the founder's voice clock). Scenes animate from these
// and AudioLayer places keyboard, click and confirmation sounds from the same
// values, so picture and SFX cannot drift apart.

export const FPS = 30;
export const sec = (s: number) => Math.round(s * FPS);

export type Typing = { readonly id: string; readonly start: number; readonly text: string; readonly cps: number };

/** Seconds at which the last character of a typing run lands. */
export const typingEnd = (t: Typing) => t.start + t.text.length / t.cps;

export const TYPING = Object.fromEntries(
  (Object.keys(SPEC_TYPING) as TypingKey[]).map((k) => [k, { id: k, ...SPEC_TYPING[k] }]),
) as Record<TypingKey, Typing>;

export const BEAT = SPEC_BEATS;
export const EVIDENCE = [BEAT.evidence0, BEAT.evidence1, BEAT.evidence2, BEAT.evidence3, BEAT.evidence4, BEAT.evidence5, BEAT.evidence6] as const;
export const ICON_STEP = 0.25;
export const SIGNAL_FLIGHT = 0.9;

/** Sound events derived from the beats (absolute seconds). */
// The eighteen sound categories of the V7 brief plus the V8 product moments
// (workspace created, shared understanding) — navislabs_v8_sfx_map.json. Every
// event names one; MOUSE stays empty on purpose — the cursor moves silently and
// only a visible press makes a sound.
export const SFX_CATEGORIES = [
  "KEYBOARD",
  "TERMINAL",
  "MOUSE",
  "UI CLICK",
  "DATA ARRIVAL",
  "SOURCE APPEAR",
  "MCP CONNECT",
  "API RESPONSE",
  "CONTEXT RETRIEVAL",
  "PERMISSION DENIED",
  "APPROVE",
  "SEND",
  "GMAIL CONFIRM",
  "RUN START",
  "RUN COMPLETE",
  "PRODUCT REVEAL",
  "TRANSITION",
  "END REVEAL",
  "WORKSPACE CREATED",
  "SHARED UNDERSTANDING",
] as const;
export type SfxCategory = (typeof SFX_CATEGORIES)[number];
export type SfxEvent = { readonly at: number; readonly sfx: string; readonly category: SfxCategory; readonly gainDb?: number; readonly why: string };

const keyRun = (t: Typing, why: string): SfxEvent[] => {
  const step = Math.max(1, Math.round(t.cps / 13));
  const out: SfxEvent[] = [];
  for (let i = 0; i < t.text.length; i += step) {
    const jitter = ((i * 37) % 11) / 1000;
    out.push({ at: t.start + i / t.cps + jitter, sfx: ["key1", "key2", "key3", "key4"][(i * 7) % 4], category: "KEYBOARD", gainDb: t.cps > 30 ? -3 : 0, why });
  }
  return out;
};
const typedEnd = (t: Typing) => t.start + t.text.length / t.cps;

// Deliberate silences (no SFX inside): before V01, the breath before
// NavisLabs, the held breath after Approve, the refusal, and the ending.
export const SFX_SILENCES: readonly { readonly from: number; readonly to: number; readonly why: string }[] = [
  { from: 0, to: BEAT.truthPeople - 0.15, why: "the film opens on the voice" },
  { from: BEAT.blackout, to: BEAT.logoTile - 0.06, why: "breath before NavisLabs" },
  { from: BEAT.approveClick + 0.05, to: BEAT.sending, why: "held breath after Approve & send" },
  { from: BEAT.permDenied + 0.1, to: BEAT.agentUses - 0.05, why: "the refusal sits in near-silence" },
  { from: BEAT.sameFacts - 0.3, to: BEAT.sharedUnderstanding - 0.5, why: "'Same facts. Same sources. Same freshness.' is carried by the voice alone" },
  { from: BEAT.endLockup + 0.1, to: filmSpec.format.duration_s, why: "the end card resolves into silence" },
];

export const SFX_EVENTS: readonly SfxEvent[] = [
  // S01 · the person's view and the agent's view appear; then a piece of the truth lands in each system.
  { at: BEAT.truthPeople, sfx: "source", category: "SOURCE APPEAR", gainDb: -4, why: "the person's view: the email" },
  { at: BEAT.truthAgent, sfx: "source", category: "SOURCE APPEAR", gainDb: -4, why: "the agent's view: the workflow file" },
  ...[BEAT.signalDecision, BEAT.signalCustomer, BEAT.signalCommitment, BEAT.signalMeeting, BEAT.signalContext, BEAT.signalAccount, BEAT.signalCrm, BEAT.signalJira, BEAT.signalKnowledge].map((at, i) => ({ at, sfx: "data", category: "DATA ARRIVAL" as const, gainDb: -7 - (i % 3), why: "a piece of the truth lands in its system" })),
  // S02 · a person copies by hand.
  ...[BEAT.copy1, BEAT.copy2, BEAT.copy3].map((at) => ({ at, sfx: "click", category: "UI CLICK" as const, gainDb: -8, why: "copying a fragment by hand" })),
  // S03 · Navis: the reveal; then the light world.
  { at: BEAT.logoTile - 0.05, sfx: "reveal", category: "PRODUCT REVEAL", why: "the Navis mark appears as 'Navis' is spoken" },
  { at: BEAT.toLight - 0.1, sfx: "whoosh", category: "TRANSITION", why: "a very subtle whoosh on the wipe into the light data-flow world" },
  { at: BEAT.iconsIn, sfx: "sweep", category: "DATA ARRIVAL", why: "the connected systems appear (one soft sweep, not a tick per tile)" },
  // S04 · signals enter the pipeline; context is assembled.
  ...[0, 2, 4, 6].map((i) => ({ at: BEAT.signalsOut + 0.7 + i * 0.24, sfx: "data", category: "DATA ARRIVAL" as const, gainDb: -7, why: "signals leave the systems (every other one — restraint)" })),
  { at: BEAT.flowContext, sfx: "retrieve", category: "CONTEXT RETRIEVAL", gainDb: -2, why: "memory becomes context" },
  // S05–S09 · Navis App.
  { at: BEAT.appRise, sfx: "air", category: "TRANSITION", gainDb: -4, why: "the Navis App opens" },
  { at: BEAT.whyClick, sfx: "click", category: "UI CLICK", why: "Why this matters" },
  ...EVIDENCE.map((at) => ({ at, sfx: "source", category: "SOURCE APPEAR" as const, gainDb: -6, why: "an evidence row with its source" })),
  { at: BEAT.resolveIn, sfx: "retrieve", category: "CONTEXT RETRIEVAL", gainDb: -5, why: "the connected systems resolve into one customer state" },
  { at: BEAT.reviewReplyClick, sfx: "click", category: "UI CLICK", why: "Review & reply" },
  { at: BEAT.reviewDraftClick, sfx: "click", category: "UI CLICK", gainDb: -2, why: "Review draft" },
  { at: BEAT.selectStart, sfx: "click", category: "UI CLICK", gainDb: -4, why: "the person selects a sentence" },
  ...keyRun(TYPING.humanEdit, "the person writes their own sentence"),
  { at: BEAT.approveClick, sfx: "approve", category: "APPROVE", why: "Approve & send" },
  { at: BEAT.sending + 0.05, sfx: "sent", category: "SEND", why: "Sending…" },
  { at: BEAT.gmailAccepted, sfx: "gmail", category: "GMAIL CONFIRM", why: "Gmail accepted the message" },
  { at: BEAT.acrossIn + 0.05, sfx: "source", category: "SOURCE APPEAR", gainDb: -6, why: "the same event across the company's systems" },
  // S10–S15 · Navis Developer.
  { at: BEAT.devCut - 0.05, sfx: "whoosh", category: "TRANSITION", why: "a very subtle whoosh, light → dark: Navis Developer" },
  ...keyRun(TYPING.agentTask, "the task typed to the agent"),
  { at: BEAT.agentEnter, sfx: "enter", category: "TERMINAL", why: "the task is sent" },
  { at: BEAT.addMember, sfx: "click", category: "UI CLICK", why: "Add member" },
  { at: BEAT.mcpAdd + 0.05, sfx: "enter", category: "TERMINAL", gainDb: -4, why: "claude mcp add" },
  ...keyRun(TYPING.mcpList, "claude mcp list"),
  { at: typedEnd(TYPING.mcpList) + 0.03, sfx: "enter", category: "TERMINAL", gainDb: -4, why: "claude mcp list" },
  { at: BEAT.mcpConnected, sfx: "connect", category: "MCP CONNECT", why: "✓ Connected" },
  ...[BEAT.surfaceMcp, BEAT.surfaceApi, BEAT.surfaceSdk, BEAT.surfaceCli].map((at) => ({ at, sfx: "surface", category: "MCP CONNECT" as const, why: "an access surface lights as it is said" })),
  { at: BEAT.contextCall, sfx: "retrieve", category: "CONTEXT RETRIEVAL", why: "navis_get_relevant_context" },
  ...[0, 1, 2, 3, 4, 5].map((i) => ({ at: BEAT.contextResult + 0.1 + i * 0.12, sfx: "data", category: "DATA ARRIVAL" as const, gainDb: -4 - (i % 2) * 2, why: "a cited fact arrives with its source and freshness" })),
  ...keyRun(TYPING.sdkInstall, "npm install ./navis-sdk-0.1.0.tgz"),
  // No Enter accent on npm install: it lands under the key line "Navis isn't the model."
  { at: BEAT.apiResponse, sfx: "api", category: "API RESPONSE", why: "the API returns items, sources, freshness" },
  { at: BEAT.permAuthorized, sfx: "source", category: "SOURCE APPEAR", gainDb: -8, why: "ALLOWED" },
  { at: BEAT.permOwnScope, sfx: "source", category: "SOURCE APPEAR", gainDb: -8, why: "OWN SCOPE" },
  { at: BEAT.permDenied, sfx: "deny", category: "PERMISSION DENIED", why: "DENIED: a key without view_memory is refused" },
  { at: BEAT.agentUses, sfx: "run", category: "RUN START", why: "the agent starts the work" },
  { at: BEAT.runComplete, sfx: "complete", category: "RUN COMPLETE", gainDb: -2, why: "the last step lands: the run is on record, Completed" },
  // S16 · solo developer → team → continuity.
  { at: BEAT.soloPick, sfx: "click", category: "UI CLICK", why: "For myself" },
  { at: BEAT.soloWorkspace + 0.1, sfx: "workspace", category: "WORKSPACE CREATED", why: "the personal workspace exists" },
  { at: BEAT.soloCheckpoint + 0.4, sfx: "enter", category: "TERMINAL", gainDb: -4, why: "navis workstate checkpoint" },
  { at: BEAT.soloCheckpointOk, sfx: "save", category: "TERMINAL", why: "Checkpoint recorded" },
  { at: BEAT.soloRestore, sfx: "retrieve", category: "CONTEXT RETRIEVAL", gainDb: -4, why: "the next session restores the work state" },
  // S17–S18 · one company; the name.
  { at: BEAT.heroIn - 0.9, sfx: "rwhoosh", category: "TRANSITION", why: "a soft reverse whoosh into one company" },
  { at: BEAT.sharedSignal, sfx: "air", category: "TRANSITION", gainDb: -6, why: "the event reaches both products" },
  { at: BEAT.sharedUnderstanding - 0.45, sfx: "lock", category: "SHARED UNDERSTANDING", why: "same fact, source and freshness lock into one understanding" },
  { at: BEAT.endLockup, sfx: "end", category: "END REVEAL", why: "an extremely subtle low resolve under the end lockup (no logo hit)" },
];
