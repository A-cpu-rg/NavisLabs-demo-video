import { interpolate } from "remotion";
import { BEAT } from "../config/beats";
import { FILM, FONT } from "../config/navisBrand";
import { BrandTile } from "../ui/Integrations";
import { copy } from "../config/filmSpec";
import { COMMITMENT, COMPANY, CUSTOMER, ENGINEER, LIVE_IDS, PROJECT, USER } from "../ui/demoContent";
import { CLAMP, easeOut } from "../ui/kit";
import { FilmLabel, NavisMark } from "../scenes/shared";
import data from "../data/navislabs_v8_launch_state.json";

// S05 opening, V07 "Inside a company, the Navis App is for people." The
// company (NavisLabs, using its own product) → its teams → its people → the
// customers, projects and commitments they carry → the systems where that work
// already lives → the Navis App. Mirrors the App's own sidebar (Organization:
// People, Projects, Customers). People and teams are demo data (entity audit).

const r = (T: number, a: number, b: number) => interpolate(T, [a, b], [0, 1], { ...CLAMP, easing: easeOut });

const Row: React.FC<{ readonly label: string; readonly reveal: number; readonly children: React.ReactNode }> = ({ label, reveal, children }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 28, opacity: reveal, translate: `0 ${(1 - reveal) * 10}px` }}>
    <div style={{ width: 230, textAlign: "right" }}>
      <FilmLabel size={13} tracking={0.26} color={FILM.textSubtle}>
        {label}
      </FilmLabel>
    </div>
    <div style={{ display: "flex", gap: 12, alignItems: "center" }}>{children}</div>
  </div>
);

const Pill: React.FC<{ readonly children: React.ReactNode; readonly strong?: boolean }> = ({ children, strong }) => (
  <div style={{ padding: "8px 14px", borderRadius: 10, backgroundColor: "#FFFFFF", border: `1px solid rgba(28,25,20,${strong ? 0.22 : 0.1})`, fontFamily: FONT.app, fontSize: 17, fontWeight: strong ? 600 : 500, color: "#111827", whiteSpace: "nowrap" }}>{children}</div>
);

export const OrgIntro: React.FC<{ readonly T: number }> = ({ T }) => {
  const s = (i: number) => r(T, BEAT.orgIn + 0.05 + i * 0.16, BEAT.orgIn + 0.3 + i * 0.16);
  const teams = data.teams.map((t) => t.name);
  return (
    <div style={{ position: "absolute", left: 0, top: 0, width: 1920, height: 1080, display: "flex", flexDirection: "column", justifyContent: "center", gap: 30, paddingLeft: 330, boxSizing: "border-box" }}>
      <Row label="Company" reveal={s(0)}>
        <NavisMark size={40} tone="light" />
        <div style={{ fontFamily: FONT.display, fontSize: 30, fontWeight: 600, color: FILM.ink }}>{COMPANY.name}</div>
      </Row>
      <Row label="Teams" reveal={s(1)}>
        {teams.map((t) => (
          <Pill key={t}>{t}</Pill>
        ))}
      </Row>
      <Row label="People" reveal={s(2)}>
        <Pill strong>
          {USER.name} · {USER.title}
        </Pill>
        <Pill>
          {ENGINEER.name} · {ENGINEER.title}
        </Pill>
      </Row>
      <Row label="Customers · projects · commitments" reveal={s(3)}>
        <Pill>
          {CUSTOMER.name} <span style={{ opacity: 0.6, fontWeight: 400 }}>· {copy("fictionalOrg")}</span>
        </Pill>
        <Pill>{PROJECT.name}</Pill>
        <Pill>Revised terms · {COMMITMENT.due}</Pill>
      </Row>
      <Row label="Where the work lives" reveal={s(4)}>
        {LIVE_IDS.map((id) => (
          <BrandTile key={id} id={id} size={44} />
        ))}
      </Row>
    </div>
  );
};
