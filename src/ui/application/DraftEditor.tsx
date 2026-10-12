import { APP, DEMO, FONT } from "../../config/navisBrand";
import { Icon } from "../kit";
import { CUSTOMER_DRAFT } from "../demoContent";
import { TYPING } from "../../config/beats";

// DraftEditor -> Navis-AI/src/components/navis/actions/DraftReviewPanel.tsx:
//   loading:  "Preparing the draft…" (rounded-xl bg-gray-50, Loader2)
//   section:  rounded-2xl bg-white ring-1 ring-black/[0.06]
//   "Why this" (10px .22em) + reason; Field labels To / Subject / Message
//   (10px .18em gray-500); Subject input and Message textarea (bg-gray-50,
//   ring-gray-200, 13px, leading 1.6); "Evidence (n)" details;
//   action row: "Approve & send" (rounded-full bg-black 12px, Send icon),
//   "Saved" / "Save changes" (dirty), "Rewrite", "Ignore", "Close";
//   approved: emerald chip "Approved — sending".
// HumanEdit: the founder's own change in the Message field (setBody + dirty).

export const DRAFT = CUSTOMER_DRAFT;

export const PreparingDraft: React.FC<{ readonly spin: number }> = ({ spin }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 8, borderRadius: 12, backgroundColor: APP.gray50, padding: "12px 16px", fontSize: 12, color: APP.gray500 }}>
    <Icon.Loader size={12} rotation={spin} />
    Preparing the draft…
  </div>
);

/** The edited sentence: selection sweep, then the founder's typed replacement. */
export const HumanEdit: React.FC<{
  /** 0..1 how much of the original sentence is selected. */
  readonly select: number;
  /** Characters of TYPING.humanEdit.text typed so far (0 = original still there). */
  readonly typed: number;
  readonly caret: boolean;
}> = ({ select, typed, caret }) => {
  if (typed > 0) {
    return (
      <span>
        <span style={{ backgroundColor: "rgba(79,70,229,0.08)", borderRadius: 3 }}>{TYPING.humanEdit.text.slice(0, typed)}</span>
        <Caret on={caret} />
      </span>
    );
  }
  const text = DRAFT.replaced;
  const cut = Math.round(text.length * select);
  return (
    <span>
      <span style={{ backgroundColor: select > 0 ? "rgba(59,130,246,0.28)" : "transparent", borderRadius: 2 }}>{text.slice(0, cut)}</span>
      <span>{text.slice(cut)}</span>
    </span>
  );
};

const Caret: React.FC<{ readonly on: boolean }> = ({ on }) => (
  <span style={{ display: "inline-block", width: 1.5, height: 16, translate: "0 3px", marginLeft: 1, backgroundColor: on ? "#000" : "transparent" }} />
);

export const ApproveButton: React.FC<{ readonly hover: number; readonly press: number }> = ({ hover, press }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      borderRadius: 999,
      padding: "6px 12px",
      fontSize: 12,
      fontWeight: 500,
      color: "#fff",
      backgroundColor: hover > 0 ? `rgb(${31 * hover},${41 * hover},${55 * hover})` : "#000",
      scale: String(1 - 0.05 * press),
      boxShadow: hover > 0 ? `0 0 0 ${3 * hover}px rgba(0,0,0,0.08)` : undefined,
    }}
  >
    <Icon.Send size={11} color="#fff" />
    Approve &amp; send
  </div>
);

const Field: React.FC<{ readonly label: string; readonly children: React.ReactNode }> = ({ label, children }) => (
  <div>
    <div style={{ marginBottom: 4, fontSize: 10, fontWeight: 600, letterSpacing: "0.18em", textTransform: "uppercase", color: APP.gray500 }}>{label}</div>
    {children}
  </div>
);

const Ghost: React.FC<{ readonly children: React.ReactNode; readonly muted?: boolean }> = ({ children, muted }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      borderRadius: 999,
      padding: "6px 12px",
      fontSize: 12,
      backgroundColor: "#fff",
      color: muted ? APP.gray500 : APP.gray700,
      boxShadow: `inset 0 0 0 1px ${APP.gray200}`,
    }}
  >
    {children}
  </div>
);

export const DraftEditor: React.FC<{
  readonly edit: React.ReactNode;
  /** Message field focused (founder clicked into it). */
  readonly focused: boolean;
  readonly dirty: boolean;
  readonly approved: number;
  readonly approveHover: number;
  readonly approvePress: number;
}> = ({ edit, focused, dirty, approved, approveHover, approvePress }) => (
  <section style={{ borderRadius: 16, backgroundColor: "#fff", boxShadow: "inset 0 0 0 1px rgba(0,0,0,0.06)", fontFamily: FONT.app }}>
    <div style={{ borderBottom: "1px solid rgba(0,0,0,0.05)", padding: "12px 16px" }}>
      <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray500 }}>Why this</div>
      <div style={{ marginTop: 4, fontSize: 13, lineHeight: 1.5, color: APP.gray700 }}>{DRAFT.reason}</div>
    </div>
    <div style={{ padding: "12px 16px", display: "flex", flexDirection: "column", gap: 12 }}>
      <Field label="To">
        <div style={{ fontSize: 13, color: APP.gray800 }}>{DEMO.contactEmail}</div>
      </Field>
      <Field label="Subject">
        <div style={{ borderRadius: 8, backgroundColor: APP.gray50, padding: "6px 10px", fontSize: 13, color: "#000", boxShadow: `inset 0 0 0 1px ${APP.gray200}`, opacity: approved > 0 ? 0.6 : 1 }}>
          {DRAFT.subject}
        </div>
      </Field>
      <Field label="Message">
        <div
          style={{
            borderRadius: 8,
            backgroundColor: focused ? "#fff" : APP.gray50,
            padding: "8px 10px",
            fontSize: 13,
            lineHeight: 1.6,
            color: "#000",
            boxShadow: `inset 0 0 0 1px ${focused ? "#000" : APP.gray200}`,
            minHeight: 9 * 13 * 1.6,
            whiteSpace: "pre-wrap",
            opacity: approved > 0 ? 0.6 : 1,
          }}
        >
          {DRAFT.paragraphs[0]}
          {"\n\n"}
          {DRAFT.paragraphs[1]}
          {"\n\n"}
          {edit}
          {"\n\n"}
          {DRAFT.paragraphs[3]}
        </div>
      </Field>
      <div style={{ borderRadius: 8, backgroundColor: APP.gray50, padding: "8px 12px", boxShadow: "inset 0 0 0 1px rgba(229,231,235,0.7)", fontSize: 11, fontWeight: 500, color: APP.gray600, display: "flex", alignItems: "center", gap: 4 }}>
        <Icon.Mail size={10} />
        Evidence (2)
      </div>
    </div>
    <div style={{ borderTop: "1px solid rgba(0,0,0,0.05)", padding: "12px 16px", display: "flex", alignItems: "center", gap: 8, minHeight: 32 }}>
      {approved > 0 ? (
        <div
          style={{
            opacity: approved,
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            borderRadius: 999,
            backgroundColor: APP.emerald50,
            padding: "6px 12px",
            fontSize: 12,
            fontWeight: 500,
            color: APP.emerald800,
            boxShadow: `inset 0 0 0 1px ${APP.emerald200}`,
          }}
        >
          <Icon.Check size={11} />
          Approved — sending
        </div>
      ) : (
        <>
          <ApproveButton hover={approveHover} press={approvePress} />
          <Ghost>{dirty ? "Save changes" : "Saved"}</Ghost>
          <Ghost muted>
            <Icon.Refresh size={11} />
            Rewrite
          </Ghost>
          <Ghost muted>
            <Icon.X size={11} />
            Ignore
          </Ghost>
          <div style={{ marginLeft: "auto", fontSize: 11.5, color: APP.gray500 }}>Close</div>
        </>
      )}
    </div>
  </section>
);
