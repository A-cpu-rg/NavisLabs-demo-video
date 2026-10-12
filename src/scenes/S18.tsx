import { AbsoluteFill, Img, interpolate, staticFile } from "remotion";
import { BEAT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { CLIENTS, DEV, FILM, FONT } from "../config/navisBrand";
import { linePath, NavisLine } from "../components/BlueLine";
import { Grain } from "../components/World";
import { CinematicText } from "../film/CinematicText";
import { EndCard } from "../film/EndCard";
import { COMPANY, CUSTOMER, RESULT_ROWS } from "../ui/demoContent";
import { CLAMP, easeInOut, easeOut, useSceneClock } from "../ui/kit";
import { FilmLabel, NavisMark } from "./shared";

// S18 · 84.0–100 s · what stays yours; the name. End: less motion, less sound, the brand, silence.
//   V23 "Models change. Agents change. Tools change."
//   V24 "What it knows stays yours."
//   V25 "Company-owned. Model-neutral. Shared by people and agents."
//   V26 "NavisLabs. The shared understanding for your organization."
// Agent clients keep changing (Claude Code: live verified, the installed
// Claude.app icon; Cursor, Codex, VS Code: config verified, text only —
// Devtool docs/mcp/CLIENTS.md). What Navis knows — the same facts, each with
// its source and freshness (demo data) — stays in one company-owned record.
// No compounding or learning claim, no "only", no superiority. End card: mark +
// wordmark, the website's headline, both products, navislabs.in.

const r = (T: number, a: number, b: number, e: (x: number) => number = easeOut) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: e });

const CLIENT_X = 1010;
const clientY = (i: number) => 360 + i * 66;
const NODE = { x: 1640, y: clientY(2) };
/** The company's record (V24), left of the clients; the pair is centred once the record is in. */
const RECORD = { x: 350, y: 318, w: 720 };
const RECORD_ROWS = RESULT_ROWS.slice(0, 4);
const RECORD_PORT = { x: RECORD.x + RECORD.w + 14, y: clientY(2) };
/** How far the client list glides right as the record arrives (one move, then still). */
const CLIENT_SHIFT = 200;

export const S18: React.FC = () => {
  const { T, end } = useSceneClock("S18");
  const sayOut = r(T, BEAT.staysYours - 0.35, BEAT.staysYours - 0.05);
  const says = [BEAT.modelsChange, BEAT.agentsChange, BEAT.toolsChange].map((b) => r(T, b, b + 0.35) * (1 - sayOut));
  // Everything except the end card clears just before the lockup.
  const endOut = r(T, BEAT.endLockup - 0.4, BEAT.endLockup - 0.1);
  const clients = r(T, BEAT.clientsIn, BEAT.clientsIn + 0.35) * (1 - endOut);
  // The clients keep changing, through V24 and V25.
  const active = T < BEAT.clientsIn ? 0 : Math.floor((T - BEAT.clientsIn) / 0.6) % CLIENTS.length;
  const record = r(T, BEAT.recordIn, BEAT.recordIn + 0.45) * (1 - endOut);
  const rows = RECORD_ROWS.map((_, i) => r(T, BEAT.recordIn + 0.25 + i * 0.15, BEAT.recordIn + 0.6 + i * 0.15) * (1 - endOut));
  const node = 1 - r(T, BEAT.recordIn - 0.1, BEAT.recordIn + 0.3);
  const cx = CLIENT_X + CLIENT_SHIFT * r(T, BEAT.recordIn - 0.1, BEAT.recordIn + 0.5, easeInOut);
  const yours = r(T, BEAT.staysYours, BEAT.staysYours + 0.35) * (1 - endOut);
  const pillarsOut = r(T, BEAT.endLockup - 0.35, BEAT.endLockup - 0.05);
  const pillars = [0, 1.0, 2.1].map((d) => r(T, BEAT.pillars + d, BEAT.pillars + d + 0.35) * (1 - pillarsOut));
  const black = r(T, BEAT.fadeOut, end);
  const pillarWords = [copy("pillar1"), copy("pillar2"), copy("pillar3")];
  return (
    <AbsoluteFill style={{ backgroundColor: "#0E0D0A" }}>
      {/* Models change. Agents change. Tools change. */}
      <div style={{ position: "absolute", left: 220, top: 330, display: "flex", flexDirection: "column", gap: 26 }}>
        {[copy("modelsChange"), copy("agentsChange"), copy("toolsChange")].map((s, i) => (
          <div key={s} style={{ opacity: says[i], fontFamily: FONT.display, fontSize: 64, fontWeight: 500, letterSpacing: "-0.015em", color: FILM.onInk, whiteSpace: "nowrap" }}>
            {s}
          </div>
        ))}
      </div>
      {clients > 0 ? (
        <div style={{ opacity: clients }}>
          <div style={{ position: "absolute", left: cx, top: clientY(0) - 64 }}>
            <FilmLabel size={13} tracking={0.26} color={FILM.onInkDim}>
              Agent clients · over MCP
            </FilmLabel>
          </div>
          {CLIENTS.map((c, i) => {
            const on = i === active ? 1 : 0;
            return (
              <div key={c.name}>
                {/* Before V24 the clients reach the NavisLabs node; from V24 they reach the company's record. */}
                {node > 0 ? (
                  <div style={{ position: "absolute", left: 0, top: 0, opacity: node * (0.2 + 0.8 * on) }}>
                    <NavisLine d={linePath({ x: cx + 380, y: clientY(i) }, { x: NODE.x - 60, y: NODE.y })} width={on ? 1.6 : 1} ignite={on} bounds={{ x: 0, y: 0, w: 1920, h: 1080 }} />
                  </div>
                ) : null}
                {record > 0 ? (
                  <div style={{ position: "absolute", left: 0, top: 0, opacity: record * (0.2 + 0.8 * on) }}>
                    <NavisLine d={linePath({ x: cx - 10, y: clientY(i) }, RECORD_PORT)} width={on ? 1.6 : 1} ignite={on} bounds={{ x: 0, y: 0, w: 1920, h: 1080 }} />
                  </div>
                ) : null}
                <div style={{ position: "absolute", left: cx, top: clientY(i), translate: "0 -50%", width: 360, display: "flex", alignItems: "center", gap: 12, padding: "9px 14px", borderRadius: 10, border: `1px solid rgba(237,235,230,${0.08 + 0.2 * on})`, backgroundColor: on ? FILM.inkRaised : "transparent", boxSizing: "border-box" }}>
                  {c.icon ? <Img src={staticFile(c.icon)} style={{ width: 24, height: 24, borderRadius: 6 }} /> : <span style={{ width: 24, height: 24 }} />}
                  <span style={{ flex: 1, fontFamily: FONT.display, fontSize: 20, fontWeight: 500, color: on ? FILM.onInk : FILM.onInkMuted }}>{c.name}</span>
                  <span style={{ fontFamily: FONT.mono, fontSize: 12, letterSpacing: "0.06em", color: c.status === "live verified" ? DEV.termGreen : FILM.onInkDim }}>{c.status}</span>
                </div>
              </div>
            );
          })}
          {node > 0 ? (
            <div style={{ position: "absolute", left: NODE.x, top: NODE.y, translate: "-50% -50%", display: "flex", flexDirection: "column", alignItems: "center", gap: 12, opacity: node }}>
              <NavisMark size={64} tone="dark" />
              <FilmLabel size={12} tracking={0.24} color={FILM.onInkMuted}>
                NavisLabs
              </FilmLabel>
            </div>
          ) : null}
        </div>
      ) : null}
      {/* What it knows stays yours: the company's record, unchanged while the clients change. */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 210, display: "flex", justifyContent: "center" }}>
        <CinematicText text={copy("staysYours")} reveal={yours} size={60} />
      </div>
      {record > 0 ? (
        <div
          style={{
            position: "absolute",
            left: RECORD.x,
            top: RECORD.y,
            width: RECORD.w,
            opacity: record,
            translate: `0 ${(1 - record) * 12}px`,
            padding: "22px 26px",
            borderRadius: 16,
            backgroundColor: FILM.inkRaised,
            border: "1px solid rgba(237,235,230,0.12)",
            boxShadow: "0 30px 70px -30px rgba(0,0,0,0.8)",
            boxSizing: "border-box",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <NavisMark size={26} tone="dark" />
            <FilmLabel size={13} tracking={0.24} color={FILM.onInk}>
              {copy("whatItKnows")}
            </FilmLabel>
            <span style={{ marginLeft: "auto", fontFamily: FONT.mono, fontSize: 13, color: FILM.onInkDim }}>
              {COMPANY.name} · {CUSTOMER.caps}
            </span>
          </div>
          <div style={{ marginTop: 16 }}>
            {RECORD_ROWS.map((row, i) => (
              <div key={row.fact} style={{ opacity: rows[i], display: "grid", gridTemplateColumns: "1fr 170px 110px", alignItems: "baseline", gap: 12, padding: "13px 0", borderTop: "1px solid rgba(237,235,230,0.08)" }}>
                <span style={{ fontFamily: FONT.display, fontSize: 21, fontWeight: 500, color: FILM.onInk }}>{row.fact}</span>
                <span style={{ fontFamily: FONT.mono, fontSize: 13, color: FILM.onInkMuted }}>{row.source}</span>
                <span style={{ fontFamily: FONT.mono, fontSize: 13, color: DEV.termGreen, textAlign: "right" }}>{row.fresh}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {/* Company-owned · Model-neutral · Shared by people + agents */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 930, translate: "0 -50%", display: "flex", justifyContent: "center", alignItems: "center", gap: 40 }}>
        {pillarWords.map((w, i) => (
          <div key={w} style={{ display: "flex", alignItems: "center", gap: 40, opacity: pillars[i] }}>
            {i > 0 ? <div style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: FILM.cobalt }} /> : null}
            <div style={{ fontFamily: FONT.display, fontSize: 44, fontWeight: 600, letterSpacing: "-0.01em", color: FILM.onInk, whiteSpace: "nowrap" }}>{w}</div>
          </div>
        ))}
      </div>
      <EndCard
        tile={r(T, BEAT.endLockup, BEAT.endLockup + 0.4)}
        word={r(T, BEAT.endLockup + 0.2, BEAT.endLockup + 0.6)}
        tagline={r(T, BEAT.endTagline, BEAT.endTagline + 0.5)}
        products={r(T, BEAT.endProducts, BEAT.endProducts + 0.45)}
        cta={r(T, BEAT.endUrl, BEAT.endUrl + 0.45)}
        disclosure={r(T, BEAT.endUrl + 0.2, BEAT.endUrl + 0.7)}
      />
      <Grain opacity={0.02} />
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: black }} />
    </AbsoluteFill>
  );
};
