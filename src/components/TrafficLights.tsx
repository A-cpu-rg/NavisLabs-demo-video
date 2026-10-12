// macOS standard window controls, 12 px, desaturated to 60% (window_chrome).
const LIGHTS = ["#FF5F57", "#FEBC2E", "#28C840"];

export const TrafficLights: React.FC = () => (
  <div style={{ display: "flex", gap: 8, filter: "saturate(0.6)" }}>
    {LIGHTS.map((color) => (
      <div
        key={color}
        style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: color }}
      />
    ))}
  </div>
);
