import { DEV, FILM, FONT, type IntegrationId } from "../config/navisBrand";
import { BrandIcon } from "../ui/Integrations";

// Where a fact came from: the system's real mark (website asset) on a white
// tile, plus a short label. Used on dark film surfaces.

export const SourceBadge: React.FC<{ readonly source: IntegrationId; readonly label: string; readonly sub?: string; readonly tone?: "dark" | "light"; readonly size?: number }> = ({
  source,
  label,
  sub,
  tone = "dark",
  size = 26,
}) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
    <div style={{ width: size, height: size, borderRadius: size * 0.27, backgroundColor: "#fff", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, boxShadow: tone === "light" ? "0 0 0 1px rgba(28,25,20,0.1)" : undefined }}>
      <BrandIcon id={source} height={source === "slack" ? size * 0.46 : size * 0.56} />
    </div>
    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <div style={{ fontFamily: FONT.mono, fontSize: 12, color: tone === "dark" ? DEV.termText : FILM.ink, whiteSpace: "nowrap" }}>{label}</div>
      {sub ? <div style={{ fontFamily: FONT.mono, fontSize: 10.5, color: tone === "dark" ? FILM.onInkMuted : FILM.textSubtle, whiteSpace: "nowrap" }}>{sub}</div> : null}
    </div>
  </div>
);
