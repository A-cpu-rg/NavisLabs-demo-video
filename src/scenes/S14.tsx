import { AbsoluteFill } from "remotion";
import { BEAT } from "../config/beats";
import { copy } from "../config/filmSpec";
import { DEMO, DEV, FILM, FONT } from "../config/navisBrand";
import { Camera } from "../components/Camera";
import { DeveloperShell } from "../ui/developer/DeveloperShell";
import { AccessDenied, PermissionPanel } from "../ui/developer/Permissions";
import { CUSTOMER, RESULT_ROWS } from "../ui/demoContent";
import { useSceneClock } from "../ui/kit";
import { FilmLabel } from "./shared";

// S14 · 59.8–63.4 s · V17 "Every request is checked against identity and
// permissions."
// The access model the Console states today (Policies: "Access is decided by
// the permissions on an agent's credential. The Core checks them server-side
// on every request"; central policy enforcement is "Not enabled yet", so no
// policy engine is shown). Credential → organization → granted scope:
// AUTHORIZED; a key from another organization reads only its own (the
// organization comes from the key, never a parameter — api-client
// credentials.ts): OWN SCOPE; a read-only key is DENIED with the exact
// refusal (mcp-server authorization/authorize.ts).

const CHAIN = ["Agent credential", `Organization · ${DEMO.org}`, "Granted scope · view_memory", "Decision"] as const;

export const S14: React.FC = () => {
  const { t, at, r } = useSceneClock("S14");
  const refusal = t >= at(BEAT.refusal);
  const chain = CHAIN.map((_, i) => r(BEAT.permIdentity + i * 0.12, BEAT.permIdentity + 0.25 + i * 0.12));
  const panels = [BEAT.permAuthorized, BEAT.permOwnScope, BEAT.permDenied].map((b) => r(b - 0.35, b - 0.1));
  const resolved = [BEAT.permAuthorized, BEAT.permOwnScope, BEAT.permDenied].map((b) => r(b, b + 0.2));
  const focus = [BEAT.permAuthorized, BEAT.permOwnScope, BEAT.permDenied].map((b, i, all) => r(b, b + 0.15) * (i < 2 ? 1 - r(all[i + 1], all[i + 1] + 0.15) : 1));
  const checked = r(BEAT.permIdentity + 0.5, BEAT.permIdentity + 0.8);
  return (
    <AbsoluteFill>
      <DeveloperShell lift={0}>
        {!refusal ? (
          <Camera keyframes={[{ f: 0, x: 0, y: -10, scale: 1.0, easing: "drift" }, { f: at(BEAT.refusal), x: 0, y: -4, scale: 1.02, easing: "drift" }]}>
            <div style={{ position: "absolute", left: 0, top: -300, translate: "-50% 0", display: "flex", alignItems: "center", gap: 14 }}>
              {CHAIN.map((c, i) => (
                <div key={c} style={{ display: "flex", alignItems: "center", gap: 14, opacity: chain[i] }}>
                  <div style={{ padding: "9px 16px", borderRadius: 10, border: "1px solid rgba(237,235,230,0.16)", backgroundColor: FILM.inkRaised, fontFamily: FONT.mono, fontSize: 15, letterSpacing: "0.04em", color: i === 3 ? FILM.onInk : DEV.termMuted, whiteSpace: "nowrap" }}>{c}</div>
                  {i < CHAIN.length - 1 ? <div style={{ width: 34, height: 1, backgroundColor: "rgba(237,235,230,0.3)" }} /> : null}
                </div>
              ))}
            </div>
            <div style={{ position: "absolute", left: -730, top: -200, opacity: panels[0], translate: `0 ${(1 - panels[0]) * 16}px` }}>
              <PermissionPanel org={DEMO.org} keyName="Agent key" permissions="view_memory" status="authorized" resolved={resolved[0]} lines={[`${RESULT_ROWS.length} facts · ${CUSTOMER.name}`, "Its own organization's data"]} width={460} height={300} focus={focus[0]} />
            </div>
            <div style={{ position: "absolute", left: -230, top: -200, opacity: panels[1], translate: `0 ${(1 - panels[1]) * 16}px` }}>
              <PermissionPanel org="Another organization" keyName="Their agent key" permissions="view_memory" status="own-scope" resolved={resolved[1]} lines={["Reads only its own organization.", "NavisLabs data is never returned."]} width={460} height={300} focus={focus[1]} />
            </div>
            <div style={{ position: "absolute", left: 270, top: -200, opacity: panels[2], translate: `0 ${(1 - panels[2]) * 16}px` }}>
              <PermissionPanel org={DEMO.org} keyName="Read-only key" permissions="— (no view_memory)" status={t >= at(BEAT.permDenied) ? "denied" : "restricted"} resolved={resolved[2]} lines={['requires the "view_memory" permission…']} width={460} height={300} focus={focus[2]} />
            </div>
          </Camera>
        ) : (
          <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
            <div style={{ scale: String(1 + (t - at(BEAT.refusal)) * 0.0005), translate: "0 -30px" }}>
              <AccessDenied reveal={r(BEAT.refusal, BEAT.refusal + 0.15)} keyLine={`${DEMO.org.toUpperCase()} · READ-ONLY KEY · DENIED`} />
            </div>
          </AbsoluteFill>
        )}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 70, display: "flex", justifyContent: "center", opacity: checked }}>
          <FilmLabel size={16} tracking={0.24} color={FILM.onInk}>
            {copy("checked")}
          </FilmLabel>
        </div>
      </DeveloperShell>
    </AbsoluteFill>
  );
};
