import { AbsoluteFill } from "remotion";
import { BEAT, TYPING, sec } from "../config/beats";
import { copy } from "../config/filmSpec";
import { FILM } from "../config/navisBrand";
import { Camera } from "../components/Camera";
import { DeveloperShell } from "../ui/developer/DeveloperShell";
import { ApiPane, SdkPane } from "../ui/developer/SdkApi";
import { typedCount, useSceneClock } from "../ui/kit";
import { FilmLabel } from "./shared";

// S13 · 55.9–58.8 s · V16 "Navis isn't the model. It supplies the company's
// truth."
// Left, the TypeScript SDK installed the way it installs today (a local
// tarball — not on npm) and its own example. Right, the Developer API call
// behind the MCP tool (X-API-Key) and its answer: items, sources, freshness. No generative model
// is called on this route (contracts/openapi/developer.json: "No model was
// called … the CALLER's model does the reasoning").
export const S13: React.FC = () => {
  const { at, r, T, end } = useSceneClock("S13");
  const sdk = r(BEAT.sdkIn - 0.05, BEAT.sdkIn + 0.2);
  const install = TYPING.sdkInstall;
  const typed = install.text.slice(0, typedCount(install.text, sec(T), sec(install.start), install.cps));
  const installed = r(BEAT.sdkInstalled, BEAT.sdkInstalled + 0.15);
  const code = [0, 1, 2, 3].map((i) => r(BEAT.sdkCode + i * 0.12, BEAT.sdkCode + 0.2 + i * 0.12));
  const api = r(BEAT.apiIn, BEAT.apiIn + 0.25);
  const response = r(BEAT.apiResponse, BEAT.apiResponse + 0.25);
  const emphasis = r(BEAT.modelNeutral - 0.2, BEAT.modelNeutral + 0.1);
  const caption = r(BEAT.modelNeutral, BEAT.modelNeutral + 0.3);
  return (
    <AbsoluteFill>
      <DeveloperShell lift={0}>
        <Camera
          keyframes={[
            { f: 0, x: -430, y: -10, scale: 1.3, easing: "drift" },
            // V7: a clean cut from the SDK pane to the API pane (a 1,000 px whip smeared in V6).
            { f: at(BEAT.apiIn) - 1, x: -420, y: -6, scale: 1.32, easing: "drift" },
            { f: at(BEAT.apiIn), x: 410, y: 0, scale: 1.3, easing: "drift", note: "cut: the API" },
            { f: at(end), x: 412, y: 2, scale: 1.32, easing: "drift" },
          ]}
        >
          <div style={{ position: "absolute", left: -860, top: -200 }}>
            <SdkPane reveal={sdk} typed={typed} installed={installed} code={code} />
          </div>
          <div style={{ position: "absolute", left: -20, top: -200 }}>
            <ApiPane reveal={api} response={response} emphasis={emphasis} />
          </div>
        </Camera>
        {caption > 0 ? (
          <div style={{ position: "absolute", left: 0, right: 0, bottom: 70, display: "flex", justifyContent: "center", opacity: caption }}>
            <FilmLabel size={16} tracking={0.24} color={FILM.onInk}>
              {copy("noModel")}
            </FilmLabel>
          </div>
        ) : null}
      </DeveloperShell>
    </AbsoluteFill>
  );
};
