import { filmSpec, SPEC_BEATS, SPEC_SCENES, type SpecTransition } from "./filmSpec";
import type { SceneId } from "./types";

// The film timeline, read from navislabs_v8_film_spec.json: 18 scenes on the
// founder's voice clock (~125 s), 30 fps. `overlap` is how many frames a scene keeps playing under the
// next one; the incoming scene draws the transition over it.

export type FilmScene = { readonly id: SceneId; readonly from: number; readonly to: number; readonly overlap: number; readonly transitionOut: SpecTransition; readonly beat: string };

export const FILM_SCENES: readonly FilmScene[] = SPEC_SCENES.map((s) => ({ id: s.id, from: s.from_s, to: s.to_s, overlap: s.transition_out.frames, transitionOut: s.transition_out, beat: s.beat }));

export const FILM_FPS = 30;
/** Total length, decided by the founder's measured performance (not a fixed 100 s). */
export const FILM_FRAMES = filmSpec.format.frames;
export const FILM_SECONDS = filmSpec.format.duration_s;
/** Frame shown by the poster composition: the hero shot, thesis on screen. */
export const POSTER_FRAME = Math.round((SPEC_BEATS.sharedUnderstanding + 0.9) * FILM_FPS);

export const filmScene = (id: SceneId): FilmScene => {
  const s = FILM_SCENES.find((x) => x.id === id);
  if (!s) throw new Error(`Scene ${id} is not on the timeline`);
  return s;
};

export const startFrame = (s: FilmScene) => Math.round(s.from * FILM_FPS);
export const endFrame = (s: FilmScene) => Math.round(s.to * FILM_FPS);

// The timeline must tile 0..FILM_SECONDS exactly.
FILM_SCENES.forEach((s, i) => {
  const prev = FILM_SCENES[i - 1];
  if (i === 0 && s.from !== 0) throw new Error("Timeline must start at 0");
  if (prev && Math.abs(prev.to - s.from) > 1e-9) throw new Error(`Gap/overlap between ${prev.id} and ${s.id}`);
  if (s.to <= s.from) throw new Error(`${s.id} has no length`);
});
if (endFrame(FILM_SCENES[FILM_SCENES.length - 1]) !== FILM_FRAMES) throw new Error(`Timeline must end at ${FILM_SECONDS} s (${FILM_FRAMES} frames)`);
