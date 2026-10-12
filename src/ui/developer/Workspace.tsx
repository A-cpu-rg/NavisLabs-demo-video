import { DEV, FONT } from "../../config/navisBrand";
import { TrafficLights } from "../../components/TrafficLights";

// The developer's own environment around the agent: a code editor pane on
// the repository the agent is changing. Generic editor chrome (no vendor
// branding); the file and code are demo content.

export type CodeLine = { readonly text: string; readonly change?: "add" | "remove" };

export const RENEWAL_BEFORE: readonly CodeLine[] = [
  { text: "import { addDays } from \"../lib/time\";" },
  { text: "import { notify } from \"../lib/notify\";" },
  { text: "" },
  { text: "export async function scheduleRenewal(account: Account) {" },
  { text: "  const reminder = addDays(account.renewalDate, -14);" },
  { text: "  await notify(account.billingContact, {" },
  { text: "    at: reminder," },
  { text: "    template: \"renewal-price-update\"," },
  { text: "  });" },
  { text: "}" },
];

export const RENEWAL_AFTER: readonly CodeLine[] = [
  { text: "import { addDays } from \"../lib/time\";" },
  { text: "import { notify } from \"../lib/notify\";" },
  { text: "" },
  { text: "export async function scheduleRenewal(account: Account) {" },
  { text: "  const reminder = addDays(account.renewalDate, -14);", change: "remove" },
  { text: "  const reminder = addDays(account.renewalDate, -30);", change: "add" },
  { text: "  await notify(account.billingContact, {", change: "remove" },
  { text: "  await notify(account.owner, {", change: "add" },
  { text: "    at: reminder," },
  { text: "    template: \"renewal-terms\",", change: "add" },
  { text: "    // existing annual plans keep their current terms", change: "add" },
  { text: "    terms: account.annualTerms,", change: "add" },
  { text: "  });" },
  { text: "}" },
];

export const EditorPane: React.FC<{
  readonly width: number;
  readonly height: number;
  readonly file: string;
  readonly lines: readonly CodeLine[];
  /** 0..1 how strongly the diff colours show. */
  readonly diff?: number;
  readonly dim?: number;
}> = ({ width, height, file, lines, diff = 0, dim = 0 }) => (
  <div
    style={{
      width,
      height,
      borderRadius: 14,
      backgroundColor: "#181713",
      boxShadow: "0 0 0 1px rgba(237,235,230,0.08), 0 40px 120px -30px rgba(0,0,0,0.7)",
      overflow: "hidden",
      position: "relative",
      fontFamily: FONT.mono,
    }}
  >
    <div style={{ height: 38, display: "flex", alignItems: "center", gap: 18, padding: "0 16px", backgroundColor: "#1F1E1A", borderBottom: "1px solid rgba(237,235,230,0.06)" }}>
      <TrafficLights />
      <div style={{ fontSize: 13, color: DEV.termMuted, padding: "6px 12px", borderRadius: 6, backgroundColor: "rgba(237,235,230,0.05)" }}>{file}</div>
    </div>
    <div style={{ padding: "18px 0", fontSize: 15, lineHeight: "26px" }}>
      {lines.map((l, i) => {
        const bg = l.change === "add" ? `rgba(127,178,142,${0.16 * diff})` : l.change === "remove" ? `rgba(224,122,107,${0.14 * diff})` : "transparent";
        const mark = l.change === "add" ? "+" : l.change === "remove" ? "−" : " ";
        return (
          <div key={i} style={{ display: "flex", backgroundColor: bg, opacity: l.change === "remove" ? 1 - 0.45 * diff : 1 }}>
            <span style={{ width: 52, textAlign: "right", paddingRight: 16, color: DEV.termDim }}>{i + 1}</span>
            <span style={{ width: 18, color: l.change === "add" ? DEV.termGreen : l.change === "remove" ? DEV.termRed : "transparent", opacity: diff }}>{mark}</span>
            <span style={{ color: l.text.trim().startsWith("//") ? DEV.termDim : DEV.termText, whiteSpace: "pre", textDecoration: l.change === "remove" && diff > 0.5 ? "line-through" : "none" }}>{l.text}</span>
          </div>
        );
      })}
    </div>
    {dim > 0 ? <div style={{ position: "absolute", inset: 0, backgroundColor: "#14130F", opacity: dim * 0.7 }} /> : null}
  </div>
);
