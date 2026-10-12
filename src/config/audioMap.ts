import { getStaticFiles, staticFile } from "remotion";
import { z } from "zod";
import rawMap from "../../navislabs_v8_audio_map.json";

// Resolves every audio slot in navislabs_v8_audio_map.json to a file in public/:
// FINAL if it exists, else TEMP, else nothing (the slot is silent and nothing
// crashes). Code never names a temp file; swapping in the founder's final
// takes is a file drop, not an edit.

const file = z.string().min(1);
const voLine = z.object({
  // V5 lines (V01…) or the founder's V6 performance chunks (P1…P8).
  id: z.string().regex(/^(?:[LV]\d{2}|P\d)$/),
  scene: z.string().nullable(),
  start_s: z.number().nullable(),
  end_s: z.number().nullable(),
  ceiling_s: z.number().nullable(),
  text: z.string().nullable(),
  final: file,
  temp: file,
  note: z.string().optional(),
  shows: z.string().optional(),
});
const slot = z.object({ final: file, temp: file, gain_db: z.number().optional(), category: z.string().optional() });
const layer = z.object({ gain_db: z.number() });
const keyframes = z.object({ t: z.array(z.number()).min(2), db: z.array(z.number()).min(2) }).refine((k) => k.t.length === k.db.length && k.t.every((x, i) => i === 0 || x > k.t[i - 1]), "keyframes: t strictly increasing, one dB per time");

const schema = z.looseObject({
  fps: z.literal(30),
  resolve_order: z.tuple([z.literal("final"), z.literal("temp")]),
  voiceover: z.array(voLine).min(1),
  music: slot.loose().extend({
    sections: z.array(z.looseObject({ id: z.string(), from_s: z.number(), to_s: z.number(), brief: z.string() })),
    gain_db: z.number(),
    duck_under_vo_db: z.number(),
    duck_key_line_db: z.number().optional(),
    duck_attack_s: z.number(),
    duck_release_s: z.number(),
    dips: z.array(z.object({ from_s: z.number(), to_s: z.number(), db: z.number(), why: z.string(), ramp_s: z.number().optional() })),
    // V7: the score as stems, each mixed through keyframed volume curves (seconds → dB).
    stems: z.array(slot.extend({ id: z.string(), role: z.string(), gain_db: z.number(), duck: z.number().min(0).max(1) })).optional(),
    curves: z.object({ duck: keyframes, dips: keyframes }).optional(),
  }),
  sfx: z.looseObject({ library: z.record(z.string(), slot) }),
  layers: z.object({ vo: layer, music: layer, ui_sfx: layer, transitions: layer, ambience: layer }),
  ambience: slot.extend({ from_s: z.number(), to_s: z.number(), gain_db: z.number() }),
  // Measured speech, line by line (V6): the ducking follows the real voice.
  speech: z.array(z.object({ from_s: z.number(), to_s: z.number(), chunk: z.string(), key: z.boolean() })).optional(),
  // V8: the fourth layer — room tone, present only in the pauses (keyframed curve, dB).
  room: slot.extend({ gain_db: z.number(), curve: keyframes }).optional(),
});

const parsed = schema.safeParse(rawMap);
if (!parsed.success) {
  throw new Error(`navislabs_v8_audio_map.json is invalid:\n${z.prettifyError(parsed.error)}`);
}
export const audioMap = parsed.data;
export type VoLine = z.infer<typeof voLine>;

export type Resolved = { readonly src: string; readonly file: string; readonly tier: "final" | "temp" };

const names = (): Set<string> => new Set(getStaticFiles().map((f) => f.name));

export const resolveSlot = (s: { final: string; temp: string }): Resolved | null => {
  const present = names();
  if (present.has(s.final)) return { src: staticFile(s.final), file: s.final, tier: "final" };
  if (present.has(s.temp)) return { src: staticFile(s.temp), file: s.temp, tier: "temp" };
  return null;
};

/** Lines that have a start time and text (L21 is a reserved, empty slot). */
export const scheduledLines = audioMap.voiceover.filter(
  (l): l is VoLine & { start_s: number; ceiling_s: number; text: string } =>
    l.start_s !== null && l.ceiling_s !== null && l.text !== null,
);

export const sfxSlot = (name: string) => {
  const s = audioMap.sfx.library[name];
  if (!s) throw new Error(`SFX "${name}" is not in navislabs_v8_audio_map.json`);
  return s;
};

/** What a final render still lacks: every scheduled line and the score must be FINAL. */
export const missingFinalAudio = (): string[] => {
  const missing: string[] = [];
  for (const l of scheduledLines) {
    if (resolveSlot(l)?.tier !== "final") missing.push(`${l.id} voiceover (public/${l.final})`);
  }
  const stemsFinal = (audioMap.music.stems ?? []).length > 0 && (audioMap.music.stems ?? []).every((st) => resolveSlot(st)?.tier === "final");
  if (resolveSlot(audioMap.music)?.tier !== "final" && !stemsFinal) missing.push(`music score (public/${audioMap.music.final}, or every stem in public/music/final/v7/)`);
  return missing;
};
