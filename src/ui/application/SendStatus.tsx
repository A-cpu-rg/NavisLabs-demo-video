import { APP, DEMO, FONT } from "../../config/navisBrand";
import { Icon } from "../kit";
import { BrandIcon } from "../Integrations";
import { CUSTOMER_DRAFT } from "../demoContent";

// SendStatus -> Navis-AI/src/components/navis/actions/DraftReviewPanel.tsx
// (SendStatus, lines ~555-700). Every state is a backend-recorded fact:
//   sending: Loader2 + "Sending…" + "Navis has approved this and Gmail is
//            being called. This usually takes a few seconds."
//   sent:    Check + "Reply sent" + "Gmail accepted the message." + To /
//            Subject list + "Open source thread" (emerald-50/60, ring-emerald-200)
// "Reply sent" appears only for an executed row carrying a real provider
// receipt; there is no branch that infers success.

const Card: React.FC<{ readonly tone: "sending" | "sent"; readonly children: React.ReactNode; readonly style?: React.CSSProperties }> = ({ tone, children, style }) => (
  <section
    style={{
      borderRadius: 16,
      padding: 16,
      fontFamily: FONT.app,
      backgroundColor: tone === "sent" ? "rgba(236,253,245,0.6)" : "#fff",
      boxShadow: `inset 0 0 0 1px ${tone === "sent" ? APP.emerald200 : "rgba(0,0,0,0.06)"}`,
      ...style,
    }}
  >
    {children}
  </section>
);

export const SendingState: React.FC<{ readonly spin: number; readonly style?: React.CSSProperties }> = ({ spin, style }) => (
  <Card tone="sending" style={style}>
    <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
      <Icon.Loader size={14} color={APP.gray500} rotation={spin} style={{ marginTop: 2 }} />
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, color: "#000" }}>Sending…</div>
        <div style={{ marginTop: 4, fontSize: 11.5, lineHeight: 1.5, color: APP.gray600 }}>
          Navis has approved this and Gmail is being called. This usually takes a few seconds.
        </div>
      </div>
    </div>
  </Card>
);

export const SentState: React.FC<{ readonly style?: React.CSSProperties }> = ({ style }) => (
  <Card tone="sent" style={style}>
    <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
      <Icon.Check size={14} color={APP.emerald700} style={{ marginTop: 2 }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: "#000" }}>Reply sent</div>
        <div style={{ marginTop: 4, fontSize: 11.5, lineHeight: 1.5, color: APP.gray600 }}>Gmail accepted the message.</div>
        <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "max-content 1fr", columnGap: 12, rowGap: 4 }}>
          <div style={{ fontSize: 10.5, color: APP.gray500 }}>To</div>
          <div style={{ fontSize: 11.5, color: APP.gray800 }}>{DEMO.contactEmail}</div>
          <div style={{ fontSize: 10.5, color: APP.gray500 }}>Subject</div>
          <div style={{ fontSize: 11.5, color: APP.gray800 }}>{CUSTOMER_DRAFT.subject}</div>
        </div>
        <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, borderRadius: 999, backgroundColor: "#fff", padding: "6px 12px", fontSize: 12, color: APP.gray700, boxShadow: `inset 0 0 0 1px ${APP.gray200}` }}>
            <Icon.External size={11} />
            Open source thread
          </div>
          <div style={{ marginLeft: "auto", fontSize: 11.5, color: APP.gray500 }}>Close</div>
        </div>
      </div>
    </div>
  </Card>
);

/**
 * The provider step of the send: Gmail's acceptance, as the product records
 * it. A plain receipt row, not Gmail's own interface.
 */
export const GmailConfirmation: React.FC<{ readonly accepted: number; readonly style?: React.CSSProperties }> = ({ accepted, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      padding: "10px 16px",
      borderRadius: 12,
      backgroundColor: "#fff",
      boxShadow: `inset 0 0 0 1px ${accepted > 0.5 ? APP.emerald200 : APP.gray200}, 0 12px 30px -14px rgba(15,23,42,0.18)`,
      fontFamily: FONT.app,
      fontSize: 13,
      color: APP.gray700,
      ...style,
    }}
  >
    <BrandIcon id="gmail" height={13} />
    <span style={{ fontWeight: 600, color: "#000" }}>Gmail</span>
    <span style={{ color: APP.gray300 }}>·</span>
    <span style={{ color: accepted > 0.5 ? APP.emerald800 : APP.gray500 }}>{accepted > 0.5 ? "accepted the message" : "being called…"}</span>
    {accepted > 0.5 ? <Icon.Check size={13} color={APP.emerald700} /> : null}
  </div>
);
