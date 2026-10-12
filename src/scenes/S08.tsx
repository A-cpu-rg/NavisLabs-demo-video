import { BEAT, TYPING } from "../config/beats";
import { useSceneClock } from "../ui/kit";
import { AppFlow } from "./AppFlow";

// S08 · 34.2–40.6 s
//   V10 "It's waiting on you, so Navis prepares the reply."
//   V11 "A person decides."
// Macro cut to Waiting on you; back to the Kaveri card; "Review & reply" →
// DecisionDrawer → "Review draft" → the draft. Abhishek selects one sentence
// and writes a new one; NAVIS PREPARES · A PERSON DECIDES · THE COMPANY ACTS;
// the cursor settles on "Approve & send".
const TYPED_END = TYPING.humanEdit.start + TYPING.humanEdit.text.length / TYPING.humanEdit.cps + 0.05;

export const S08: React.FC = () => {
  const { at, T, end } = useSceneClock("S08");
  return (
    <AppFlow
      T={T}
      keyframes={[
        { f: 0, x: 140, y: 250, scale: 2.05, easing: "drift", note: "cut: Waiting on you" },
        { f: at(BEAT.waiting + 0.79), x: 145, y: 252, scale: 2.1, easing: "drift" },
        { f: at(BEAT.waiting + 0.8), x: 220, y: 200, scale: 1.4, easing: "drift", note: "cut: back to the customer card" },
        { f: at(BEAT.reviewReplyClick - 0.1), x: 200, y: 210, scale: 1.38, easing: "drift" },
        // V7: a clean cut to the wider framing as the drawer opens (the pull-back smeared).
        { f: at(BEAT.drawerOpen) - 1, x: 198, y: 210, scale: 1.38, easing: "drift" },
        { f: at(BEAT.drawerOpen), x: -30, y: 160, scale: 1.15, easing: "drift", note: "cut: the drawer opens" },
        { f: at(BEAT.reviewDraftClick), x: -60, y: 170, scale: 1.2, easing: "drift" },
        { f: at(BEAT.draftShown + 0.05), x: 0, y: 90, scale: 1.15, easing: "glide" },
        { f: at(BEAT.draftShown + 0.45), x: -250, y: 40, scale: 1.35, easing: "glide" },
        { f: at(BEAT.selectStart - 0.1), x: -470, y: 110, scale: 2.1, easing: "glide" },
        // V7: the typing finishes, then a clean cut to Approve & send — the camera is still for
        // "A person decides."; only the cursor moves.
        { f: at(TYPED_END) - 1, x: -450, y: 120, scale: 2.15, easing: "drift" },
        { f: at(TYPED_END), x: -560, y: 240, scale: 1.95, easing: "drift", note: "cut: Approve & send" },
        { f: at(end), x: -560, y: 250, scale: 2.0, easing: "drift" },
      ]}
    />
  );
};
