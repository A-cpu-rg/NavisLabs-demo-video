import { linePath, NavisLine } from "../components/BlueLine";
import { Lockup } from "../scenes/shared";

// The NavisLabs lockup (website treatment: logo tile + "NavisLabs") with the
// cobalt line drawing beneath it from the centre out. Centered on its parent.

export const LogoReveal: React.FC<{
  readonly size: number;
  readonly tile: number;
  readonly word: number;
  readonly line: number;
  readonly lineHalf?: number;
  readonly lineGap?: number;
}> = ({ size, tile, word, line, lineHalf = 460, lineGap = 110 }) => (
  <div style={{ position: "relative", display: "flex", flexDirection: "column", alignItems: "center" }}>
    <Lockup size={size} tile={tile} word={word} glow={tile * (1 - word * 0.7)} />
    <div style={{ position: "absolute", left: "50%", top: size / 2 + lineGap, width: 0, height: 0 }}>
      <NavisLine d={linePath({ x: -lineHalf, y: 0 }, { x: lineHalf, y: 0 })} trim={[0.5 - line / 2, 0.5 + line / 2]} />
    </div>
  </div>
);
