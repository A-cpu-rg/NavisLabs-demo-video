// One place that knows where every asset lives. Scenes ask for an asset id;
// they never spell a file path. Dropping a file into public/ at the manifest
// path is all it takes for the film to start using it.
import { getStaticFiles, staticFile } from "remotion";
import { blueprint } from "./loadBlueprint";

type ManifestEntry = (typeof blueprint.asset_manifest)[number];

const manifest = new Map<string, ManifestEntry>(
  blueprint.asset_manifest.map((a) => [a.asset_id, a]),
);

const publicPath = (filePath: string) => filePath.replace(/^public\//, "");

export const assetEntry = (id: string): ManifestEntry => {
  const entry = manifest.get(id);
  if (!entry) throw new Error(`Asset ${id} is not in the blueprint asset_manifest`);
  return entry;
};

const staticNames = (): Set<string> => new Set(getStaticFiles().map((f) => f.name));

// Recordings may arrive as the ProRes master (.mov, per the manifest) or as a
// high-bitrate H.264 export (.mp4); either is picked up.
const candidates = (id: string): string[] => {
  const path = assetEntry(id).file_path;
  if (!path) return [];
  const rel = publicPath(path);
  if (rel.endsWith("/")) return [];
  return id.startsWith("REC_") ? [rel.replace(/\.mov$/, ".mp4"), rel] : [rel];
};

// Folder-style entries (music stems) count as present when the folder holds a file.
const folderHasFiles = (id: string, names: Set<string>): boolean => {
  const path = assetEntry(id).file_path;
  if (!path?.endsWith("/")) return false;
  const prefix = publicPath(path);
  return [...names].some((n) => n.startsWith(prefix) && !n.split("/").pop()?.startsWith("."));
};

/** Public-relative file name of the asset if it exists, else null. */
export const assetFile = (id: string): string | null => {
  const names = staticNames();
  return candidates(id).find((c) => names.has(c)) ?? null;
};

export const hasAsset = (id: string): boolean => {
  const names = staticNames();
  return candidates(id).some((c) => names.has(c)) || folderHasFiles(id, names);
};

export const assetSrc = (id: string): string | null => {
  const file = assetFile(id);
  return file ? staticFile(file) : null;
};

/** Required assets with a file path that are not in public/ yet. */
export const missingRequiredAssets = (): string[] =>
  blueprint.asset_manifest
    .filter((a) => a.required && a.file_path !== null && !hasAsset(a.asset_id))
    .map((a) => `${a.asset_id} (${a.file_path})`);

export const recordingAssetId = (rid: string) => `REC_${rid}`;
