import { interpolate } from "remotion";
import { BEAT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { APP, DEMO, DEV, FILM, FONT, macPrompt } from "../config/navisBrand";
import { linePath, NavisLine } from "../components/BlueLine";
import { ApplicationShell } from "../ui/application/ApplicationShell";
import { GLANCE_HEIGHT, PriorityCard, TodayDashboard } from "../ui/application/TodayDashboard";
import { AGENT_TASK, COMPANY, CONTACT, CUSTOMER_CONTEXT, EMAIL, EVENT_FACT, EVENT_LABEL, PRIORITIES, RESULT_ROWS, WORKFLOW } from "../ui/demoContent";
import { AgentConversation, ShellLine } from "../ui/developer/AgentConversation";
import { ContextRequest } from "../ui/developer/Context";
import { BrandIcon } from "../ui/Integrations";
import { CLAMP, easeInOut } from "../ui/kit";
import { FilmLabel, Lockup } from "../scenes/shared";
import { CodeEditor, RENEWALS_AFTER } from "./CodeEditor";

// The core brand image. The Navis App (people) on the left, Navis
// Developer (developers + AI agents) on the right, NavisLabs between them.
// One business event leaves NavisLabs and arrives in both — the renewal the
// person replied about is the context the agent worked from. Then the proof,
// row by row: the same fact, the same source, the same freshness, as each
// product presents it. Then the thesis. World space (origin at frame centre).

const MINI = 0.43;
export const SPLIT_X = 540;
const Y = -110;
const ROW_Y = [270, 334, 398] as const;
const FILE = WORKFLOW.file.split("/").pop() ?? WORKFLOW.file;

const r = (T: number, a: number, b: number, e?: (x: number) => number) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

const Label: React.FC<{ readonly name: string; readonly audience: string; readonly reveal: number; readonly did: string; readonly didReveal: number; readonly emphasis?: number }> = ({ name, audience, reveal, did, didReveal, emphasis = 0 }) => (
  <div style={{ textAlign: "center", opacity: reveal, translate: `0 ${(1 - reveal) * 10}px`, scale: String(1 + 0.05 * emphasis) }}>
    <div style={{ display: "inline-block", fontFamily: FONT.display, fontSize: 30, fontWeight: 600, letterSpacing: "0.07em", color: FILM.onInk, whiteSpace: "nowrap", paddingBottom: 6, boxShadow: `inset 0 -${2 * emphasis}px 0 rgba(25,118,254,${0.9 * emphasis})` }}>{name}</div>
    <div style={{ marginTop: 10, fontFamily: FONT.mono, fontSize: 17, letterSpacing: "0.12em", color: FILM.onInkMuted, whiteSpace: "nowrap" }}>{audience}</div>
    <div style={{ marginTop: 14, opacity: didReveal, display: "inline-flex", alignItems: "center", gap: 8, fontFamily: FONT.mono, fontSize: 13, letterSpacing: "0.16em", textTransform: "uppercase", color: DEV.termGreen, whiteSpace: "nowrap" }}>
      <span style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: DEV.termGreen }} />
      {did}
    </div>
  </div>
);

/** The application side of a row: how a person sees it. */
const AppCell: React.FC<{ readonly children: React.ReactNode }> = ({ children }) => (
  <div style={{ display: "inline-flex", alignItems: "center", gap: 10, padding: "10px 18px", borderRadius: 12, backgroundColor: "#fff", fontFamily: FONT.app, fontSize: 19, fontWeight: 500, color: "#000", boxShadow: `inset 0 0 0 1px ${APP.ring}`, whiteSpace: "nowrap" }}>{children}</div>
);
/** The developer side: how the agent receives it. */
const DevCell: React.FC<{ readonly children: React.ReactNode }> = ({ children }) => (
  <div style={{ display: "inline-flex", alignItems: "center", padding: "10px 18px", borderRadius: 12, backgroundColor: FILM.inkRaised, border: "1px solid rgba(237,235,230,0.14)", fontFamily: FONT.mono, fontSize: 16.5, color: DEV.termText, whiteSpace: "nowrap" }}>{children}</div>
);
const k = (s: string) => <span style={{ color: "#9CDCFE" }}>{s}</span>;
const v = (s: string) => <span style={{ color: "#CE9178" }}>{s}</span>;

export const ProductSplit: React.FC<{ readonly T: number }> = ({ T }) => {
  const minis = r(T, BEAT.heroIn, BEAT.heroIn + 0.7, easeInOut);
  const hub = r(T, BEAT.heroIn + 0.2, BEAT.heroIn + 0.8);
  const labels = r(T, BEAT.heroIn + 0.5, BEAT.heroIn + 1.1);
  const line = r(T, BEAT.heroIn + 0.6, BEAT.sharedSignal, easeInOut);
  const travel = r(T, BEAT.sharedSignal, BEAT.sharedSignal + 1.0, easeInOut);
  const lit = r(T, BEAT.sharedSignal + 0.85, BEAT.sharedSignal + 1.3) * (1 - 0.5 * r(T, BEAT.sameFacts, BEAT.sameFacts + 0.5));
  const did = [r(T, BEAT.sharedSignal + 1.4, BEAT.sharedSignal + 1.8), r(T, BEAT.sharedSignal + 1.7, BEAT.sharedSignal + 2.1)];
  const rowsOut = r(T, BEAT.sharedUnderstanding - 0.45, BEAT.sharedUnderstanding - 0.1);
  const rows = [BEAT.sameFacts, BEAT.sameSources, BEAT.sameFreshness].map((b) => r(T, b, b + 0.45) * (1 - rowsOut));
  const thesis = [-0.6, 0, 1.0].map((d) => r(T, BEAT.sharedUnderstanding + d, BEAT.sharedUnderstanding + d + 0.5));
  const chipFade = 1 - r(T, BEAT.sharedSignal + 0.9, BEAT.sharedSignal + 1.2);
  // A thin cobalt outline marks where the event lands; no halo.
  const glow = (on: number) => `0 0 0 ${2 * on}px rgba(25,118,254,${0.85 * on})`;
  const peopleAgents = r(T, BEAT.peopleAgents, BEAT.peopleAgents + 0.4);
  // "Two ways in." — both product surfaces are marked at once: the same thin outline, the names underlined.
  const twoWays = r(T, BEAT.peopleAgents - 0.05, BEAT.peopleAgents + 0.3);
  const mark = Math.max(lit, twoWays);

  const chip = (dir: -1 | 1) => (
    <div
      key={dir}
      style={{
        position: "absolute",
        left: dir * (150 + travel * 270),
        top: Y + travel * 40,
        translate: "-50% -50%",
        opacity: travel > 0 ? chipFade : 0,
        padding: "9px 16px",
        borderRadius: 10,
        backgroundColor: FILM.ink,
        border: "1px solid rgba(25,118,254,0.8)",
        fontFamily: FONT.mono,
        fontSize: 14,
        letterSpacing: "0.14em",
        color: FILM.onInk,
        whiteSpace: "nowrap",
      }}
    >
      {EVENT_LABEL}
    </div>
  );

  const ROWS = [
    {
      label: copy("sameFact"),
      app: <AppCell>{EVENT_FACT}</AppCell>,
      dev: (
        <DevCell>
          {k('"text"')}: {v(`"${EVENT_FACT}"`)}
        </DevCell>
      ),
    },
    {
      label: copy("sameSource"),
      app: (
        <AppCell>
          <BrandIcon id="gmail" height={15} /> Gmail · {CONTACT.name} · {EMAIL.date}
        </AppCell>
      ),
      dev: (
        <DevCell>
          {k('"source"')}: {v('"gmail"')} · {k('"occurred_at"')}: {v(`"${EMAIL.date_iso}"`)}
        </DevCell>
      ),
    },
    {
      label: copy("sameFreshness"),
      app: <AppCell>Synced 2m ago · 09:42</AppCell>,
      dev: (
        <DevCell>
          {k('"last_success_at"')}: {v('"09:42"')} · {k('"as_of"')}: {v('"09:44"')}
        </DevCell>
      ),
    },
  ];

  return (
    <>
      {/* Navis App — people */}
      <div style={{ position: "absolute", left: -SPLIT_X, top: Y, width: 0, height: 0, scale: String(MINI), opacity: minis, translate: `${(1 - minis) * -60}px 0` }}>
        <ApplicationShell waiting={0} user={DEMO.user} email={DEMO.userEmail} scroll={GLANCE_HEIGHT}>
          <TodayDashboard primary={<PriorityCard item={PRIORITIES[0]} primary />} />
        </ApplicationShell>
        <div style={{ position: "absolute", left: -333, top: -66, width: 802, height: 386, borderRadius: 18, boxShadow: glow(mark) }} />
      </div>
      {/* Navis Developer — developers + AI agents */}
      <div style={{ position: "absolute", left: SPLIT_X, top: Y, width: 0, height: 0, scale: String(MINI), opacity: minis, translate: `${(1 - minis) * 60}px 0` }}>
        <CodeEditor
          width={1500}
          height={940}
          title={`${FILE} — ${DEMO.repo}`}
          file={FILE}
          lines={RENEWALS_AFTER}
          diff={1}
          terminalLabel="claude"
          splitAt={0.4}
          terminal={
            <AgentConversation>
              <ShellLine user={`${DEMO.macUser}@${DEMO.macHost}`} repo={DEMO.repo} command="claude" />
              <ContextRequest task={AGENT_TASK.replace(/\.$/, "")} status="ok">
                <span style={{ color: DEV.termMuted }}>count: {RESULT_ROWS.length} · sources: auth_state ok</span>
              </ContextRequest>
              <div style={{ marginTop: 10, borderRadius: 10, boxShadow: glow(mark), padding: "8px 10px" }}>
                {CUSTOMER_CONTEXT.slice(0, 3).map((f) => (
                  <div key={f.label} style={{ marginBottom: 6 }}>
                    <span style={{ color: DEV.termDim }}>{f.label.toUpperCase()} </span>
                    <span style={{ color: DEV.termText }}>{f.text}</span>
                  </div>
                ))}
              </div>
            </AgentConversation>
          }
        />
      </div>
      {line > 0 ? (
        <>
          <NavisLine d={linePath({ x: -SPLIT_X + 300, y: Y }, { x: -150, y: Y })} trim={[1 - line, 1]} width={2} />
          <NavisLine d={linePath({ x: 150, y: Y }, { x: SPLIT_X - 310, y: Y })} trim={[0, line]} width={2} />
        </>
      ) : null}
      {chip(-1)}
      {chip(1)}
      {/* One company; the shared layer between the two products — no container. */}
      <div style={{ position: "absolute", left: 0, top: Y - 260, translate: "-50% -50%", opacity: hub, display: "flex", alignItems: "center", gap: 14 }}>
        <FilmLabel size={14} tracking={0.3} color={FILM.onInkMuted}>
          {copy("oneCompany")}
        </FilmLabel>
        <span style={{ width: 4, height: 4, borderRadius: 2, backgroundColor: FILM.onInkDim }} />
        <span style={{ fontFamily: FONT.display, fontSize: 18, fontWeight: 600, color: FILM.onInk }}>{COMPANY.name}</span>
      </div>
      <div style={{ position: "absolute", left: 0, top: Y, translate: "-50% -50%", opacity: hub, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
        <Lockup size={46} />
        <FilmLabel size={11.5} tracking={0.22} color={FILM.onInkMuted}>
          {copy("layer")}
        </FilmLabel>
      </div>
      <div style={{ position: "absolute", left: -SPLIT_X, top: Y + 228, translate: "-50% 0" }}>
        <Label name={copy("product.application")} audience={copy("product.application.who")} reveal={labels} did="Reply sent · Gmail accepted" didReveal={did[0]} emphasis={twoWays} />
      </div>
      <div style={{ position: "absolute", left: SPLIT_X, top: Y + 228, translate: "-50% 0" }}>
        <Label name={copy("product.developer")} audience={copy("product.developer.who")} reveal={labels} did="Workflow updated · run on record" didReveal={did[1]} emphasis={twoWays} />
      </div>
      {ROWS.map((row, i) => (
        <div key={row.label} style={{ opacity: rows[i] }}>
          <div style={{ position: "absolute", left: -SPLIT_X, top: ROW_Y[i], width: 2 * SPLIT_X, height: 1, backgroundColor: "rgba(237,235,230,0.16)" }} />
          <div style={{ position: "absolute", left: -SPLIT_X, top: ROW_Y[i], translate: `-50% -50%`, scale: String(0.97 + 0.03 * rows[i]) }}>{row.app}</div>
          <div style={{ position: "absolute", left: SPLIT_X, top: ROW_Y[i], translate: `-50% -50%`, scale: String(0.97 + 0.03 * rows[i]) }}>{row.dev}</div>
          <div style={{ position: "absolute", left: 0, top: ROW_Y[i], translate: "-50% -50%", padding: "6px 14px", borderRadius: 999, backgroundColor: "#0E0D0A", border: `1px solid rgba(25,118,254,${0.6 * rows[i]})` }}>
            <FilmLabel size={14} tracking={0.26} color={FILM.onInk}>
              {row.label}
            </FilmLabel>
          </div>
        </div>
      ))}
      <div style={{ position: "absolute", left: 0, top: ROW_Y[1] + 74, translate: "-50% -50%", opacity: peopleAgents }}>
        <FilmLabel size={17} tracking={0.3} color={FILM.onInkMuted}>
          {copy("peopleAgents")}
        </FilmLabel>
      </div>
      <div style={{ position: "absolute", left: 0, top: ROW_Y[1], translate: "-50% -50%", display: "flex", gap: 30, whiteSpace: "nowrap" }}>
        {[copy("thesis1"), copy("thesis2"), copy("thesis3")].map((s, i) => (
          <div key={s} style={{ opacity: thesis[i], translate: `0 ${(1 - thesis[i]) * 12}px`, filter: thesis[i] < 1 ? `blur(${(1 - thesis[i]) * 5}px)` : undefined, fontFamily: FONT.display, fontSize: 54, fontWeight: 600, letterSpacing: "-0.015em", color: FILM.onInk }}>
            {s}
          </div>
        ))}
      </div>
    </>
  );
};

/** The prompt line used across the film (real Mac user and host). */
export const PROMPT = macPrompt(DEMO.repo);
