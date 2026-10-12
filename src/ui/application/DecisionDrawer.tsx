import { APP, DEMO } from "../../config/navisBrand";
import { CUSTOMER_DRAFT, CUSTOMER_NEXT, PRIORITIES } from "../demoContent";
import { Icon } from "../kit";

// DecisionDrawer -> Navis-AI/src/components/navis/DecisionDrawer.tsx:
// overlay bg-black/60, bottom sheet "max-h-[80vh] bg-white rounded-t-2xl",
// header (kind label 10px .22em + text-lg headline + X), "Why Navis flagged
// this", "Next", "Evidence" grid [130px_1fr], and the full-width black
// button whose label is 'Review draft' when a draft exists and
// 'Preparing draft…' while it resolves. The draft panel mounts below it.

export const DecisionDrawer: React.FC<{
  /** 0 closed .. 1 open (slide + overlay). */
  readonly open: number;
  /** null once the draft panel is open (the drawer hides the button then). */
  readonly buttonLabel: "Review draft" | "Preparing draft…" | null;
  readonly buttonPress?: number;
  readonly windowHeight: number;
  /** Scroll of the sheet's content (px). */
  readonly scroll?: number;
  readonly children?: React.ReactNode;
}> = ({ open, buttonLabel, buttonPress = 0, windowHeight, scroll = 0, children }) => {
  const sheetH = Math.round(windowHeight * 0.8);
  if (open <= 0) return null;
  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div style={{ position: "absolute", inset: 0, backgroundColor: `rgba(0,0,0,${0.6 * open})` }} />
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: sheetH,
          translate: `0 ${(1 - open) * sheetH}px`,
          backgroundColor: "#fff",
          borderRadius: "16px 16px 0 0",
          overflow: "hidden",
          fontFamily: "inherit",
        }}
      >
        <div style={{ padding: "24px 24px", translate: `0 ${-scroll}px`, display: "flex", flexDirection: "column", gap: 24 }}>
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
            <div>
              <div style={{ marginBottom: 4, fontSize: 10, fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray500 }}>{PRIORITIES[0].tag}</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: APP.text }}>{PRIORITIES[0].title}</div>
            </div>
            <Icon.X size={20} color={APP.text} />
          </div>
          <div>
            <div style={{ marginBottom: 4, fontSize: 12, color: APP.gray400 }}>Why Navis flagged this</div>
            <div style={{ fontSize: 14, lineHeight: 1.6, color: "#000" }}>
              {PRIORITIES[0].detail}
            </div>
          </div>
          <div>
            <div style={{ marginBottom: 4, fontSize: 12, color: APP.gray400 }}>Next</div>
            <div style={{ fontSize: 14, lineHeight: 1.6, color: "#000" }}>{CUSTOMER_NEXT}</div>
          </div>
          <div>
            <div style={{ marginBottom: 8, fontSize: 12, color: APP.gray400 }}>Evidence</div>
            <div style={{ display: "grid", gridTemplateColumns: "130px 1fr", rowGap: 6, columnGap: 12 }}>
              <div style={{ fontSize: 12, color: APP.gray400 }}>Thread</div>
              <div style={{ fontSize: 14, color: APP.gray700 }}>{CUSTOMER_DRAFT.subject}</div>
              <div style={{ fontSize: 12, color: APP.gray400 }}>From</div>
              <div style={{ fontSize: 14, color: APP.gray700 }}>
                {DEMO.contact} · {DEMO.customer}
              </div>
            </div>
          </div>
          {buttonLabel === null ? null : (
          <div
            style={{
              width: "100%",
              height: 48,
              borderRadius: 8,
              backgroundColor: "#000",
              color: "#fff",
              fontSize: 14,
              fontWeight: 500,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
              opacity: buttonLabel === "Preparing draft…" ? 0.6 : 1,
              scale: String(1 - 0.015 * buttonPress),
            }}
          >
            {buttonLabel === "Preparing draft…" ? <Icon.Loader size={14} color="#fff" /> : null}
            {buttonLabel}
          </div>
          )}
          {children}
        </div>
      </div>
    </div>
  );
};
