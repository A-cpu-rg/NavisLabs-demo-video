import { AbsoluteFill, interpolate } from "remotion";
import { BEAT, EVIDENCE, FPS, TYPING, sec } from "../config/beats";
import { copy } from "../config/filmSpec";
import { DEMO, FILM, FONT } from "../config/navisBrand";
import type { CameraKeyframe } from "../config/types";
import { Camera } from "../components/Camera";
import { Grain } from "../components/World";
import { ProductTag } from "../film/ProductReveal";
import { EvidenceExploded } from "../film/EvidenceExploded";
import { OrgIntro } from "../film/OrgIntro";
import { AcrossSystems } from "../film/AcrossSystems";
import { BrandIcon } from "../ui/Integrations";
import { APP_WINDOW, ApplicationShell } from "../ui/application/ApplicationShell";
import { DecisionDrawer } from "../ui/application/DecisionDrawer";
import { DraftEditor, HumanEdit, PreparingDraft } from "../ui/application/DraftEditor";
import { SendingState, SentState } from "../ui/application/SendStatus";
import { GLANCE_HEIGHT, PriorityCard, TodayDashboard } from "../ui/application/TodayDashboard";
import { WhyThisDrawer } from "../ui/application/WhyThisDrawer";
import { PRIORITIES } from "../ui/demoContent";
import { CLAMP, caretOn, easeInOut, easeOut, typedCount } from "../ui/kit";
import { UiCursor, arcPoint } from "./shared";

// S05–S09 are one continuous take inside the Navis App: Today and "Today
// at a glance", what changed, why (the trace), what's waiting, the draft, the
// person's edit, approval, and Gmail's confirmation. App state is a function
// of absolute time; each scene renders it with its own camera. Macro "cuts"
// are camera keyframes with a 'cut' note plus an instant page scroll.

const r = (T: number, a: number, b: number, e: (x: number) => number = easeOut) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

// World positions (window centred on the origin) of what the cursor
// touches, with the page scrolled to CARD_SCROLL; checked against stills.
export const TARGET = {
  why: { x: 452, y: 232 },
  review: { x: -164, y: 246 },
  reviewDraft: { x: 40, y: 70 },
  sentenceStart: { x: -668, y: 92 },
  sentenceEnd: { x: -372, y: 92 },
  approve: { x: -624, y: 250 },
} as const;

const DRAWER_SCROLL = 232;
const CARD_SCROLL = GLANCE_HEIGHT;
/** The waiting macro ends and the take returns to the Kaveri card. */
export const BACK_FROM_WAITING = BEAT.waiting + 0.8;
const DRAFT_LOADING = BEAT.preparing + 0.22;
const CURSOR_REST = BEAT.selectStart - 0.5;
const TO_APPROVE = BEAT.approveHover - 0.65;

/** Height the third priority card adds to Your attention (card + gap). */
export const THIRD_CARD = 190;
/** Your attention with all three priorities in view. */
const PRIORITIES_SCROLL = GLANCE_HEIGHT + 150;

/**
 * Page scroll of the Today column. Abhishek scrolls from the top of Today
 * down to his priorities (a real, eased scroll); the macro cuts to What
 * changed and Waiting on you jump with their camera cuts.
 */
const pageScroll = (T: number) => {
  if (T < BEAT.whatChanged) return PRIORITIES_SCROLL * r(T, BEAT.prioritiesIn, BEAT.prioritiesIn + 0.45, easeInOut);
  if (T < BEAT.priorityFocus) return 470 + GLANCE_HEIGHT + THIRD_CARD;
  if (T >= BEAT.waiting && T < BACK_FROM_WAITING) return 640 + GLANCE_HEIGHT + THIRD_CARD;
  return CARD_SCROLL;
};

const cursorAt = (T: number) => {
  const start = { x: 640, y: 520 };
  if (T < BEAT.whyClick) return arcPoint(start, TARGET.why, r(T, BEAT.backToCard, BEAT.whyClick - SETTLE, easeInOut));
  const parkedWhy = { x: 560, y: 380 };
  if (T < BACK_FROM_WAITING) return arcPoint(TARGET.why, parkedWhy, r(T, BEAT.whyClick + 0.15, BEAT.whyClick + 0.6, easeInOut), 0.1);
  if (T < BEAT.reviewReplyClick) return arcPoint(parkedWhy, TARGET.review, r(T, BACK_FROM_WAITING, BEAT.reviewReplyClick - SETTLE, easeInOut), -0.08);
  if (T < BEAT.reviewDraftClick) return arcPoint(TARGET.review, TARGET.reviewDraft, r(T, BEAT.drawerOpen + 0.05, BEAT.reviewDraftClick - SETTLE, easeInOut), -0.1);
  const rest = { x: 180, y: 250 };
  if (T < CURSOR_REST) return arcPoint(TARGET.reviewDraft, rest, r(T, BEAT.reviewDraftClick + 0.1, CURSOR_REST - 0.1, easeInOut), 0.1);
  if (T < BEAT.selectStart) return arcPoint(rest, TARGET.sentenceStart, r(T, CURSOR_REST, BEAT.selectStart - SETTLE, easeInOut), -0.12);
  if (T < BEAT.selectEnd + 0.08) {
    const k = r(T, BEAT.selectStart, BEAT.selectEnd, (x) => x);
    return { x: TARGET.sentenceStart.x + (TARGET.sentenceEnd.x - TARGET.sentenceStart.x) * k, y: TARGET.sentenceStart.y };
  }
  const parked = { x: TARGET.sentenceEnd.x + 60, y: TARGET.sentenceEnd.y + 50 };
  if (T < TO_APPROVE) return arcPoint(TARGET.sentenceEnd, parked, r(T, BEAT.selectEnd + 0.1, BEAT.selectEnd + 0.5, easeInOut), 0.1);
  if (T < BEAT.approveClick + 0.18) return arcPoint(parked, TARGET.approve, r(T, TO_APPROVE, BEAT.approveHover, easeInOut), 0.14);
  // After the press the hand comes off the button — a small, unhurried move away as it fades.
  return arcPoint(TARGET.approve, { x: TARGET.approve.x + 70, y: TARGET.approve.y + 64 }, r(T, BEAT.approveClick + 0.18, BEAT.approved + 0.5, easeInOut), 0.08);
};

/** A real user arrives, settles, then clicks: arrivals end this long before the click. */
const SETTLE = 0.14;

const press = (T: number, at: number) => r(T, at, at + 0.06) * (1 - r(T, at + 0.06, at + 0.16));

export const AppFlow: React.FC<{
  /** Absolute seconds. */
  readonly T: number;
  /** Camera keyframes in this scene's local frames. */
  readonly keyframes: readonly CameraKeyframe[];
}> = ({ T, keyframes }) => {
  const rise = r(T, BEAT.appRise, BEAT.appRise + 0.6);
  const cards = [r(T, BEAT.appRise + 0.3, BEAT.appRise + 0.6), r(T, BEAT.appRise + 0.4, BEAT.appRise + 0.7), r(T, BEAT.appRise + 0.5, BEAT.appRise + 0.8)];
  // The product name sits above the window only while it is framed small.
  const caption = r(T, BEAT.appRise + 0.15, BEAT.appRise + 0.45) * (1 - r(T, BEAT.glance - 0.3, BEAT.glance - 0.05));
  // "Today at a glance": a quick sweep, then Decisions and Waiting on you hold.
  const glanceFocus = [0, 1, 2, 3, 4, 5].map((i) => {
    const a = BEAT.glance + 0.2 + i * 0.12;
    const sweep = r(T, a, a + 0.1) * (1 - r(T, a + 0.25, a + 0.45));
    const hold = i === 0 || i === 4 ? r(T, BEAT.glance + 0.95, BEAT.glance + 1.15) : 0;
    return Math.max(sweep, hold);
  });

  // Trace (the drawer is gone at the hard cut to Waiting on you).
  const why = T >= BEAT.waiting ? 0 : r(T, BEAT.whyOpen, BEAT.whyOpen + 0.4) * (1 - r(T, BEAT.whyClose - 0.2, BEAT.whyClose + 0.1, easeInOut));
  const rows = EVIDENCE.map((e) => r(T, e, e + 0.3));
  const focus = EVIDENCE.map((e) => r(T, e, e + 0.15) * (1 - r(T, e + 0.4, e + 0.7)));
  const blocks = {
    happening: r(T, BEAT.whyOpen + 0.15, BEAT.whyOpen + 0.45),
    who: r(T, BEAT.whyOpen + 0.2, BEAT.whyOpen + 0.5),
    matters: r(T, BEAT.whyOpen + 0.25, BEAT.whyOpen + 0.55),
    connected: r(T, BEAT.whyOpen + 0.35, BEAT.whyOpen + 0.7),
    rows,
    canDo: r(T, BEAT.youCanDo, BEAT.youCanDo + 0.3),
  };
  const freshness = r(T, BEAT.freshness, BEAT.freshness + 0.35);

  // Decision drawer and draft.
  const drawer = r(T, BEAT.drawerOpen, BEAT.drawerOpen + 0.38);
  const buttonLabel = T < BEAT.preparing ? ("Review draft" as const) : T < DRAFT_LOADING ? ("Preparing draft…" as const) : null;
  const loading = T >= DRAFT_LOADING && T < BEAT.draftShown;
  const draftIn = r(T, BEAT.draftShown, BEAT.draftShown + 0.2);
  const scroll = DRAWER_SCROLL * r(T, BEAT.draftShown, BEAT.draftShown + 0.55, easeInOut) * (1 - r(T, BEAT.sending, BEAT.sending + 0.35, easeInOut));
  const spin = ((T * FPS) % 30) * 12;
  const typed = typedCount(TYPING.humanEdit.text, sec(T), sec(TYPING.humanEdit.start), TYPING.humanEdit.cps);
  const typingNow = T >= TYPING.humanEdit.start && typed < TYPING.humanEdit.text.length;
  const select = r(T, BEAT.selectStart, BEAT.selectEnd, (x) => x);
  const focused = T >= BEAT.selectStart;
  const approveHover = r(T, BEAT.approveHover - 0.1, BEAT.approveHover + 0.1);
  const approved = r(T, BEAT.approved, BEAT.approved + 0.2);
  const sending = T >= BEAT.sending && T < BEAT.replySent;
  const sent = T >= BEAT.replySent;

  const cursor = cursorAt(T);
  // Hidden while the evidence is read (drawer open → exploded view → waiting macro).
  // Hidden while the evidence is read: it fades out as the drawer opens and
  // comes back on the cut back to the card (BACK_FROM_WAITING) — never a pop.
  const hidden = T < BACK_FROM_WAITING ? r(T, BEAT.whyOpen + 0.2, BEAT.whyOpen + 0.4) : 1 - r(T, BACK_FROM_WAITING, BACK_FROM_WAITING + 0.12);
  const cursorOpacity = (1 - hidden) * r(T, BEAT.backToCard, BEAT.backToCard + 0.15) * (1 - r(T, BEAT.approved + 0.2, BEAT.approved + 0.5));
  const clicks = [BEAT.whyClick, BEAT.reviewReplyClick, BEAT.reviewDraftClick, BEAT.selectStart, BEAT.approveClick];

  const panel = loading ? (
    <PreparingDraft spin={spin} />
  ) : T >= BEAT.draftShown && !sending && !sent ? (
    <div style={{ opacity: draftIn }}>
      <DraftEditor
        edit={<HumanEdit select={select} typed={typed} caret={focused && caretOn(sec(T), typingNow)} />}
        focused={focused && approved === 0}
        dirty={typed > 0}
        approved={approved}
        approveHover={approveHover}
        approvePress={press(T, BEAT.approveClick)}
      />
    </div>
  ) : sending ? (
    <div style={{ opacity: r(T, BEAT.sending, BEAT.sending + 0.2) }}>
      <SendingState spin={spin} />
    </div>
  ) : sent ? (
    <div style={{ opacity: r(T, BEAT.replySent, BEAT.replySent + 0.25), scale: String(0.985 + 0.015 * r(T, BEAT.replySent, BEAT.replySent + 0.25)) }}>
      <SentState />
    </div>
  ) : null;

  // Proof rail, once the camera has pulled back below the window.
  const steps = [
    { label: "Prepared by Navis", at: BEAT.proofRail, icon: "dot" },
    { label: `Edited & approved by ${DEMO.userFirst}`, at: BEAT.proofRail + 0.25, icon: "dot" },
    { label: "Sent via Gmail", at: BEAT.proofRail + 0.5, icon: "gmail" },
    { label: "Gmail accepted the message", at: BEAT.proofRail + 0.75, icon: "done" },
  ] as const;
  const rail = r(T, BEAT.proofRail - 0.1, BEAT.proofRail + 0.25);

  return (
    <AbsoluteFill style={{ backgroundColor: FILM.canvas }}>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #FFFFFF 0%, #F7F6F3 55%, #ECE9E3 100%)" }} />
      <Camera keyframes={keyframes}>
        <div style={{ opacity: rise, translate: `0 ${(1 - rise) * 70}px` }}>
          <ApplicationShell
            waiting={0}
            user={DEMO.user}
            email={DEMO.userEmail}
            scroll={pageScroll(T)}
            overlay={
              <>
                <WhyThisDrawer open={why} windowHeight={APP_WINDOW.height} blocks={blocks} freshness={freshness} focus={focus} />
                <DecisionDrawer open={drawer} buttonLabel={buttonLabel} buttonPress={press(T, BEAT.reviewDraftClick)} windowHeight={APP_WINDOW.height} scroll={scroll}>
                  {panel}
                </DecisionDrawer>
              </>
            }
          >
            <TodayDashboard
              reveal={cards}
              glanceFocus={glanceFocus}
              primary={
                <PriorityCard
                  item={PRIORITIES[0]}
                  primary
                  hover={{ why: r(T, BEAT.whyClick - 0.2, BEAT.whyClick - 0.08), review: r(T, BEAT.reviewReplyClick - 0.2, BEAT.reviewReplyClick - 0.08) }}
                  press={{ why: press(T, BEAT.whyClick), review: press(T, BEAT.reviewReplyClick) }}
                />
              }
            />
          </ApplicationShell>
          {cursorOpacity > 0 ? <UiCursor x={cursor.x} y={cursor.y} opacity={cursorOpacity} clickFrames={clicks.map((c) => sec(c))} frameOverride={sec(T)} /> : null}
        </div>
      </Camera>
      {T < BEAT.appRise + 0.05 ? (
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #FFFFFF 0%, #F7F6F3 60%, #EEEBE5 100%)", opacity: 1 - r(T, BEAT.appRise - 0.3, BEAT.appRise + 0.02, easeInOut) }}>
          <OrgIntro T={T} />
        </AbsoluteFill>
      ) : null}
      <ProductTag name={copy("product.application")} audience={copy("product.application.audience")} reveal={caption} tone="light" />
      {T >= BEAT.explodeIn && T < BEAT.waiting ? (
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, #FFFFFF 0%, #F7F6F3 60%, #EEEBE5 100%)" }}>
          <EvidenceExploded T={T} />
        </AbsoluteFill>
      ) : null}
      {rail > 0 ? (
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 52, display: "flex", justifyContent: "center", opacity: rail }}>
          <div style={{ display: "flex", gap: 16, alignItems: "center", padding: "12px 24px", borderRadius: 999, backgroundColor: "#FFFFFF", boxShadow: "0 10px 30px -14px rgba(20,19,15,0.3), inset 0 0 0 1px rgba(28,25,20,0.08)" }}>
            {steps.map((st, i) => {
              const lit = r(T, st.at, st.at + 0.2);
              return (
                <div key={st.label} style={{ display: "flex", alignItems: "center", gap: 16 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, opacity: 0.3 + 0.7 * lit }}>
                    {st.icon === "gmail" ? <BrandIcon id="gmail" height={13} /> : <span style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: st.icon === "done" ? "#10B981" : FILM.ink }} />}
                    <span style={{ fontFamily: FONT.app, fontSize: 15, fontWeight: 500, color: "#111827", whiteSpace: "nowrap" }}>{st.label}</span>
                  </div>
                  {i < steps.length - 1 ? <div style={{ width: 34, height: 1, backgroundColor: FILM.ink, opacity: 0.15 + 0.35 * lit }} /> : null}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
      {/* The same event across the company's connected systems (after the reply). */}
      <AcrossSystems T={T} x={1352} y={300} />
      <Grain opacity={0.012} />
    </AbsoluteFill>
  );
};
