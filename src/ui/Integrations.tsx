import { Img, staticFile } from "remotion";
import { INTEGRATIONS, ROADMAP_INTEGRATIONS, type AnyIntegrationId } from "../config/navisBrand";

// The six supported systems, drawn with the vendor marks the NavisLabs
// website itself ships (navis-labs-website/public/logo, listed as
// "supported" in components/site/logos.tsx). Full brand colour, never
// recoloured; height is fixed and width follows each mark's aspect ratio,
// as the website's <BrandIcon> does.

export const integration = (id: AnyIntegrationId) => {
  const m = [...INTEGRATIONS, ...ROADMAP_INTEGRATIONS].find((x) => x.id === id);
  if (!m) throw new Error(`Unknown integration ${id}`);
  return m;
};

export const BrandIcon: React.FC<{ readonly id: AnyIntegrationId; readonly height: number; readonly style?: React.CSSProperties }> = ({ id, height, style }) => {
  const m = integration(id);
  return <Img src={staticFile(m.src)} style={{ height, width: height * m.aspect, display: "block", flexShrink: 0, ...style }} />;
};

/** A mark on a white app-tile, for use on dark or busy grounds. */
export const BrandTile: React.FC<{ readonly id: AnyIntegrationId; readonly size: number; readonly style?: React.CSSProperties }> = ({ id, size, style }) => {
  const m = integration(id);
  // Wide marks (Slack's logo is 16:10) fill the tile's width; square-ish
  // marks fill about half of it.
  const h = m.aspect > 1.4 ? (size * 0.74) / m.aspect : size * 0.52;
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: size * 0.26,
        backgroundColor: "#FFFFFF",
        boxShadow: "0 1px 0 rgba(255,255,255,0.6) inset, 0 10px 30px -12px rgba(20,19,15,0.35), 0 0 0 1px rgba(28,25,20,0.08)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        ...style,
      }}
    >
      <BrandIcon id={id} height={h} />
    </div>
  );
};
