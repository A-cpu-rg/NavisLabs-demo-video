import { APP, FONT } from "../../config/navisBrand";
import { CUSTOMER_NEXT, CONTACT, EMAIL, GLANCE, JUST_LEARNED, MORNING, PRIORITIES, type Priority } from "../demoContent";
import { Icon } from "../kit";

// The Today page of the Navis App.
//   Masthead      -> components/navis/_shared/PageMasthead.tsx ("Today · Navis",
//                    long-form date, 10px uppercase .28em, border-b black/8%)
//   Hero          -> components/navis/dashboard/DailyBriefHero.tsx (Charter
//                    greeting, headline, "Synced …" strip, "Start my day" /
//                    "Refresh workspace" pills)
//   SectionHeader -> components/navis/_shared/SectionHeader.tsx
//   CountStrip    -> components/navis/dashboard/CountStrip.tsx (tiles, tones,
//                    empty labels, h-[104px] rounded-xl ring-black/5)
//   Sections      -> app/dashboard/page.tsx SECTION_META ("Your attention",
//                    "What changed")
//   PriorityCard  -> components/navis/dashboard/NarrativeCard.tsx: eyebrow is
//                    the backend's kind_label (eyebrowFor), urgency dot
//                    (URGENCY_DOT critical red-500 / high amber-500) and word,
//                    evidence chips, "Next" rule, subject link, the canExecute
//                    line, and actions from lib/briefingComposer.ts.
// Content follows the website's Morning Intelligence preview.

export const SectionHeader: React.FC<{ readonly label: string; readonly hint?: string }> = ({ label, hint }) => (
  <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", borderBottom: "1px solid rgba(0,0,0,0.06)", paddingBottom: 8 }}>
    <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray500 }}>{label}</div>
    {hint ? <div style={{ fontSize: 11, fontStyle: "italic", color: APP.gray400 }}>{hint}</div> : null}
  </div>
);

export const Pill: React.FC<{ readonly dark?: boolean; readonly children: React.ReactNode; readonly style?: React.CSSProperties }> = ({ dark, children, style }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      borderRadius: 999,
      padding: "8px 16px",
      fontSize: 12,
      fontWeight: 500,
      whiteSpace: "nowrap",
      backgroundColor: dark ? "#000" : "#fff",
      color: dark ? "#fff" : APP.gray700,
      boxShadow: dark ? "0 1px 2px rgba(0,0,0,0.15)" : `inset 0 0 0 1px ${APP.gray200}`,
      ...style,
    }}
  >
    {children}
  </div>
);

const Chip: React.FC<{ readonly label: string; readonly value: string }> = ({ label, value }) => (
  <div style={{ display: "inline-flex", alignItems: "center", gap: 6, borderRadius: 999, backgroundColor: "rgba(243,244,246,0.8)", padding: "4px 10px", fontSize: 10.5, color: APP.gray600 }}>
    <span style={{ fontFamily: FONT.mono, fontSize: 9.5, letterSpacing: "0.05em", textTransform: "uppercase", color: APP.gray400 }}>{label}</span>
    <span>{value}</span>
  </div>
);

const URGENCY = { risk: { dot: "#EF4444", word: "critical" }, watch: { dot: APP.amber500, word: "high" } } as const;

/** One priority as a NarrativeCard. `primary` is the anchor card of the brief. */
export const PriorityCard: React.FC<{
  readonly item: Priority;
  readonly primary?: boolean;
  readonly lift?: number;
  readonly hover?: { readonly review?: number; readonly why?: number };
  readonly press?: { readonly review?: number; readonly why?: number };
}> = ({ item, primary = false, lift = 0, hover = {}, press = {} }) => {
  const u = URGENCY[item.tone];
  return (
    <div
      style={{
        borderRadius: 16,
        backgroundColor: "#fff",
        padding: primary ? "28px 32px" : "22px 26px",
        boxShadow: primary
          ? `${APP.cardShadow}, inset 0 0 0 1px ${APP.ring}, 0 ${20 * lift}px ${50 * lift}px -20px rgba(15,23,42,${0.2 * lift})`
          : "0 1px 2px rgba(15,23,42,0.04), 0 2px 6px -2px rgba(15,23,42,0.06)",
        translate: `0 ${-4 * lift}px`,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: u.dot }} />
          <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray500 }}>{item.tag}</div>
        </div>
        <div style={{ fontFamily: FONT.mono, fontSize: 9.5, letterSpacing: "0.08em", textTransform: "uppercase", color: APP.gray400 }}>{u.word}</div>
      </div>
      <div style={{ marginTop: 12, fontSize: primary ? 24 : 17.5, fontWeight: 600, lineHeight: 1.25, letterSpacing: "-0.01em", color: "#000" }}>{item.title}</div>
      <div style={{ marginTop: primary ? 12 : 8, fontSize: primary ? 14.5 : 13.5, lineHeight: 1.55, color: APP.gray700, maxWidth: 672 }}>{item.detail}</div>
      <div style={{ marginTop: primary ? 16 : 12, display: "flex", flexWrap: "wrap", gap: 6 }}>
        {item.chips.map((c) => (
          <Chip key={c.value} label={c.label} value={c.value} />
        ))}
      </div>
      {primary ? (
        <>
          <div style={{ marginTop: 16, borderLeft: "2px solid #000", paddingLeft: 12 }}>
            <div style={{ fontSize: 9.5, fontWeight: 600, letterSpacing: "0.2em", textTransform: "uppercase", color: APP.gray500 }}>Next</div>
            <div style={{ marginTop: 2, fontSize: 13, lineHeight: 1.5, color: "#000" }}>{CUSTOMER_NEXT}</div>
          </div>
          <div style={{ marginTop: 12, display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, fontWeight: 500, color: APP.gray600 }}>
            <Icon.User size={11} color={APP.gray400} />
            {item.owner}
            <Icon.ArrowUpRight size={11} color={APP.gray400} />
          </div>
          <div style={{ marginTop: 14, fontSize: 11.5, lineHeight: 1.5, color: APP.gray500 }}>
            Navis can prepare this for you — you review and approve before anything is sent.
          </div>
          <div style={{ marginTop: 14, paddingTop: 14, borderTop: `1px solid ${APP.gray100}`, display: "flex", alignItems: "center", gap: 8 }}>
            <Pill
              dark
              style={{
                padding: "6px 14px",
                scale: String(1 - 0.04 * (press.review ?? 0)),
                backgroundColor: (hover.review ?? 0) > 0 ? `rgb(${31 * (hover.review ?? 0)},${41 * (hover.review ?? 0)},${55 * (hover.review ?? 0)})` : "#000",
              }}
            >
              Review &amp; reply
            </Pill>
            <Pill style={{ padding: "6px 14px" }}>Mark decided</Pill>
            <Pill style={{ padding: "6px 14px" }}>Ask Navis</Pill>
            <Pill style={{ padding: "6px 14px" }}>Snooze</Pill>
            <div
              style={{
                marginLeft: "auto",
                fontSize: 12,
                color: (hover.why ?? 0) > 0.5 ? "#000" : APP.gray500,
                textDecoration: (hover.why ?? 0) > 0.5 ? "underline" : "none",
                scale: String(1 - 0.04 * (press.why ?? 0)),
              }}
            >
              Why this matters
            </div>
          </div>
        </>
      ) : (
        <div style={{ marginTop: 12, display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, fontWeight: 500, color: APP.gray600 }}>
          <Icon.User size={11} color={APP.gray400} />
          {item.owner}
        </div>
      )}
    </div>
  );
};

/** A 'learning' narrative: the only thing What changed may show (page.tsx SECTION_META.changed). */
export const JustLearnedCard: React.FC = () => (
  <div style={{ borderRadius: 16, backgroundColor: "#fff", padding: "22px 26px", boxShadow: "0 1px 2px rgba(15,23,42,0.04), 0 2px 6px -2px rgba(15,23,42,0.06)" }}>
    <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray500 }}>{JUST_LEARNED.tag}</div>
    <div style={{ marginTop: 10, fontSize: 17.5, fontWeight: 600, lineHeight: 1.3, letterSpacing: "-0.01em", color: "#000" }}>{JUST_LEARNED.title}</div>
    <div style={{ marginTop: 8, fontSize: 13.5, lineHeight: 1.55, color: APP.gray700 }}>{JUST_LEARNED.detail}</div>
    <div style={{ marginTop: 12, display: "flex", gap: 6 }}>
      <Chip label="Gmail" value={`${CONTACT.name} · ${EMAIL.date}`} />
    </div>
  </div>
);

/** ObligationsPanel ("Waiting on you"), copy from lib/obligations.ts + lib/signalTypes.ts. */
export const WaitingPanel: React.FC = () => (
  <div style={{ borderRadius: 16, backgroundColor: "#fff", padding: "16px 20px", boxShadow: `0 1px 2px rgba(15,23,42,0.03), inset 0 0 0 1px ${APP.ring5}`, display: "flex", gap: 12 }}>
    <div style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: APP.gray100, color: APP.gray500, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
      <Icon.Inbox size={14} />
    </div>
    <div>
      <div style={{ fontSize: 15, fontWeight: 600, color: "#000" }}>1 thing is waiting on you</div>
      <div style={{ marginTop: 10, display: "flex", alignItems: "baseline", gap: 8, fontSize: 13, color: APP.gray700 }}>
        <span style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: APP.gray300, translate: "0 -3px" }} />
        1 person is waiting on your reply
      </div>
      <div style={{ marginTop: 12, fontSize: 12, fontWeight: 500, color: APP.gray500 }}>↓ See the 1 Navis surfaced</div>
    </div>
  </div>
);

/** CountStrip.tsx — "Today at a glance": six tiles, each linking to its section. */
const TONE = {
  rose: { icon: "#E11D48", bg: "#FFF1F2", ring: "#FFE4E6", number: "#4C0519" },
  amber: { icon: "#D97706", bg: "#FFFBEB", ring: "#FEF3C7", number: "#451A03" },
  violet: { icon: "#7C3AED", bg: "#F5F3FF", ring: "#EDE9FE", number: "#2E1065" },
  sky: { icon: "#0284C7", bg: "#F0F9FF", ring: "#E0F2FE", number: "#082F49" },
  emerald: { icon: "#059669", bg: "#ECFDF5", ring: "#D1FAE5", number: "#022C22" },
  muted: { icon: APP.gray400, bg: APP.gray50, ring: APP.gray100, number: APP.gray400 },
} as const;

const TILE_ICON = { sparkles: Icon.Sparkles, alert: Icon.Alert, check: Icon.CheckSquare, calendar: Icon.Calendar, inbox: Icon.Inbox } as const;

/** Height the strip adds above "Your attention" (margin + two 104 px rows + gap). */
export const GLANCE_HEIGHT = 28 + 104 * 2 + 12;

export const CountStrip: React.FC<{ readonly focus?: readonly number[] }> = ({ focus = [] }) => (
  <div aria-label="Today at a glance" style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
    {GLANCE.map((t, i) => {
      const live = t.count > 0;
      const f = live ? (focus[i] ?? 0) : 0;
      const tone = live ? TONE[t.tone] : TONE.muted;
      const Glyph = TILE_ICON[t.icon];
      return (
        <div
          key={t.label}
          style={{
            boxSizing: "border-box",
            height: 104,
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            borderRadius: 12,
            backgroundColor: "#fff",
            padding: "14px 16px",
            opacity: live ? 1 : 0.8,
            boxShadow: `0 ${1 + f}px ${2 + 4 * f}px rgba(15,23,42,${0.03 + 0.05 * f}), inset 0 0 0 1px rgba(0,0,0,${0.05 + 0.35 * f})`,
            translate: `0 ${-2 * f}px`,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ width: 28, height: 28, borderRadius: 8, backgroundColor: tone.bg, boxShadow: `inset 0 0 0 1px ${tone.ring}`, display: "inline-flex", alignItems: "center", justifyContent: "center" }}>
              <Glyph size={14} color={tone.icon} />
            </span>
            <span style={{ fontFamily: FONT.editorial, fontSize: 28, fontWeight: 600, lineHeight: 1, fontVariantNumeric: "tabular-nums", color: tone.number }}>{t.count}</span>
          </div>
          <div>
            <div style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: "0.14em", textTransform: "uppercase", color: APP.gray500 }}>{t.label}</div>
            <div style={{ marginTop: 2, fontSize: 11, color: live ? APP.gray500 : APP.gray400, fontStyle: live ? "normal" : "italic" }}>{live ? (t.count === 1 ? "1 item" : `${t.count} items`) : t.emptyLabel}</div>
          </div>
        </div>
      );
    })}
  </div>
);

/** The Today page: masthead, greeting, Today at a glance, Your attention, What changed, Waiting on you. */
export const TodayDashboard: React.FC<{ readonly primary: React.ReactNode; readonly reveal?: readonly number[]; readonly glanceFocus?: readonly number[] }> = ({ primary, reveal = [1, 1], glanceFocus }) => (
  <div>
    <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", borderBottom: "1px solid rgba(0,0,0,0.08)", paddingBottom: 12 }}>
      <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: "0.28em", textTransform: "uppercase", color: APP.gray500 }}>Today · Navis</div>
      <div style={{ fontSize: 10, fontWeight: 500, letterSpacing: "0.22em", textTransform: "uppercase", color: APP.gray400 }}>{MORNING.date}</div>
    </div>
    <div style={{ marginTop: 24, fontFamily: FONT.editorial, fontSize: 42, fontWeight: 600, lineHeight: 1.15, letterSpacing: "-0.01em", color: "#000" }}>{MORNING.greeting}</div>
    <div style={{ marginTop: 14, maxWidth: 672, fontSize: 17, lineHeight: 1.6, color: APP.gray700 }}>{MORNING.headline}</div>
    <div style={{ marginTop: 10, fontFamily: FONT.mono, fontSize: 10.5, color: APP.gray500 }}>
      Synced <span style={{ color: APP.gray700 }}>{MORNING.synced}</span>
    </div>
    <div style={{ marginTop: 24, display: "flex", gap: 8 }}>
      <Pill dark>
        <Icon.Play size={12} color="#fff" />
        Start my day
      </Pill>
      <Pill>
        <Icon.Refresh size={12} />
        Refresh workspace
      </Pill>
    </div>
    <div style={{ marginTop: 28 }}>
      <CountStrip focus={glanceFocus} />
    </div>
    <div style={{ marginTop: 40 }}>
      <SectionHeader label="Your attention" hint="Decisions, risks, and people waiting on you" />
      <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 14 }}>
        <div style={{ opacity: reveal[0], translate: `0 ${(1 - reveal[0]) * 16}px` }}>{primary}</div>
        {PRIORITIES.slice(1).map((p, i) => (
          <div key={p.tag} style={{ opacity: reveal[i + 1] ?? 1, translate: `0 ${(1 - (reveal[i + 1] ?? 1)) * 16}px` }}>
            <PriorityCard item={p} />
          </div>
        ))}
      </div>
    </div>
    <div style={{ marginTop: 40 }}>
      <SectionHeader label="What changed" hint="Verified shifts only" />
      <div style={{ marginTop: 16 }}>
        <JustLearnedCard />
      </div>
    </div>
    <div style={{ marginTop: 40 }}>
      <SectionHeader label="Waiting on you" hint="What needs your response" />
      <div style={{ marginTop: 12 }}>
        <WaitingPanel />
      </div>
    </div>
  </div>
);
