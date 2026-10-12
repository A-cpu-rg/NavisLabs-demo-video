import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";

type Props = {
  // Pointer tip position in the parent's px. Scenes resolve the spec's named
  // targets ("'Approve & send' button center") against the real recording.
  readonly x: number;
  readonly y: number;
  readonly clickFrames?: readonly number[];
  readonly tone: "light" | "dark";
  readonly opacity?: number;
  /** Frame to evaluate clicks against (defaults to the sequence frame). */
  readonly frame?: number;
};

// visual_system.cursor: macOS arrow, black fill, 1.5 px white outline, 32 px.
// Click: pointer 1 -> 0.92 -> 1 over 120 ms. No ring (V4: no decorative circles).
// Never used in terminal scenes (keyboard only).
export const Cursor: React.FC<Props> = ({ x, y, clickFrames = [], opacity = 1, frame: frameOverride }) => {
  const sequenceFrame = useCurrentFrame();
  const frame = frameOverride ?? sequenceFrame;
  const { fps } = useVideoConfig();
  const pressFrames = Math.round(0.12 * fps);

  // Press feedback only (no click ring): the pointer dips to 0.92 and back.
  const activeClick = clickFrames.find((f) => frame >= f && frame <= f + pressFrames);
  const pointerScale =
    activeClick === undefined
      ? 1
      : interpolate(
          frame,
          [activeClick, activeClick + pressFrames / 2, activeClick + pressFrames],
          [1, 0.92, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );

  if (opacity <= 0) return null;
  return (
    <div style={{ position: "absolute", inset: 0, opacity, pointerEvents: "none" }}>
      {/* No click ring: the press is shown by the pointer itself. */}
      <svg
        width={23}
        height={32}
        viewBox="0 0 23 32"
        style={{
          position: "absolute",
          left: x,
          top: y,
          transformOrigin: "0 0",
          scale: String(pointerScale),
          overflow: "visible",
        }}
      >
        <path
          d="M1.5 1.5 L1.5 26 L7.6 20.2 L11.6 29.6 L15.6 27.9 L11.7 18.7 L20 18.7 Z"
          fill="#000"
          stroke="#fff"
          strokeWidth={1.5}
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
};
