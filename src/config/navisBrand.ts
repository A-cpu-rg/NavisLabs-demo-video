import { Easing } from "remotion";
import demoData from "../data/navislabs_v8_launch_state.json";

// Brand lock and the three design systems the film draws from. Every value
// here is copied from a real source (path in the comment), never invented.
//
//   NavisLabs            -> the company (never "Navis" on its own)
//   Navis App            -> product for people
//   Navis Developer      -> product for developers and AI agents
// (names as navis-labs-website/components/site/home.tsx PRODUCTS states them)
//
// Real product UI keeps its own strings ("Today · Navis",
// "NAVIS WORK CONTINUITY …") because those are evidence.

export const BRAND = {
  company: "NavisLabs",
  developer: "Navis Developer",
  application: "Navis App",
  developerCaps: "NAVIS DEVELOPER",
  applicationCaps: "NAVIS APP",
  // Website badge for Navis Developer: "Private preview" (nothing hosted,
  // packages unpublished).
  developerStatus: "Private preview",
  url: "navislabs.in",
  // The website's headline (navislabs.in hero).
  tagline: "The shared understanding for your organization.",
  logo: "images/navislabs-logo.png", // copy of navis-labs-website/public/navis-logo.png (dark tile)
  // The same artwork cut out of its black tile (scripts: luminance key of
  // navis-logo.png). dark = white strokes for dark grounds; light = the
  // strokes in ink for light grounds (the website notes a light-ground
  // lockup needs inverted strokes). Cobalt arcs unchanged in both.
  mark: { dark: "images/brand/navislabs-mark-dark.png", light: "images/brand/navislabs-mark-light.png" },
  disclosure: "Interfaces recreated from the Navis source. Demo company data. Some waits shortened.",
} as const;

// navis-labs-website/app/globals.css — "NO BRAND COLOUR": graphite and ink.
export const SITE = {
  canvas: "#F7F6F3",
  surface: "#FFFFFF",
  surfaceAlt: "#F0EEEA",
  surfaceSunk: "#E9E6E1",
  inkGround: "#14130F",
  text: "#14130F",
  text2: "#66625B",
  onDark: "#FFFFFF",
  onDark2: "#A8A49C",
  graphite: "#2E2A24",
  border: "rgba(28,25,20,0.10)",
  borderStrong: "rgba(28,25,20,0.18)",
  ease: Easing.bezier(0.22, 1, 0.36, 1),
} as const;

// Devtool/apps/dashboard/src/app/globals.css (Navis Developer console).
export const DEV = {
  canvas: "#f7f6f3",
  ink: "#14130f",
  graphite: "#2e2a24",
  line: "#e5e2dc",
  inkMuted: "#514d45",
  subtle: "#6f6a61",
  positive: "#3d6350",
  // Terminal (film): the dark world the agent lives in.
  term: "#14130F",
  termRaised: "#1C1B17",
  termText: "#EDEBE6",
  termMuted: "#A8A49C",
  termDim: "#6F6A61",
  termGreen: "#7FB28E",
  termAmber: "#D9A55B",
  termRed: "#E07A6B",
  termBlue: "#6FA8FF",
} as const;

// Navis-AI/src/app/globals.css + Tailwind classes used on the Today page,
// DecisionDrawer and DraftReviewPanel (gray scale = Tailwind gray).
export const APP = {
  bg: "#FBFAF7",
  card: "#FFFFFF",
  ring: "rgba(0,0,0,0.06)",
  ring5: "rgba(0,0,0,0.05)",
  hair: "rgba(0,0,0,0.06)",
  black: "#000000",
  text: "#111827",
  gray800: "#1F2937",
  gray700: "#374151",
  gray600: "#4B5563",
  gray500: "#6B7280",
  gray400: "#9CA3AF",
  gray300: "#D1D5DB",
  gray200: "#E5E7EB",
  gray100: "#F3F4F6",
  gray50: "#F9FAFB",
  emerald50: "#ECFDF5",
  emerald200: "#A7F3D0",
  emerald700: "#047857",
  emerald800: "#065F46",
  amber50: "#FFFBEB",
  amber200: "#FDE68A",
  amber500: "#F59E0B",
  amber800: "#92400E",
  red: "#DC2626",
  cardShadow: "0 1px 2px rgba(15,23,42,0.04), 0 8px 24px -12px rgba(15,23,42,0.12)",
  ease: Easing.bezier(0.2, 0.8, 0.2, 1),
} as const;

// Film-only: the cobalt of the logo arcs, used for the line and the logo only.
export const FILM = {
  ink: "#14130F",
  inkRaised: "#1C1B17",
  onInk: "#EDEBE6",
  onInkMuted: "#A8A49C",
  onInkDim: "#6F6A61",
  canvas: "#F7F6F3",
  textMuted: "#514D45",
  textSubtle: "#6F6A61",
  cobalt: "#1976FE",
  cobaltGlow: "rgba(25,118,254,0.45)",
} as const;

export const FONT = {
  // Website + Developer console.
  display: '"Geist Sans", "Geist", system-ui, -apple-system, sans-serif',
  mono: '"Geist Mono", ui-monospace, "SF Mono", Menlo, monospace',
  // Navis App UI font is Inter. Inter is not bundled with this
  // project, so the macOS system UI face (SF Pro) stands in for it.
  app: 'Inter, -apple-system, "SF Pro Text", system-ui, sans-serif',
  // Navis App editorial serif (font-editorial): Charter.
  editorial: 'Charter, "Bitstream Charter", Georgia, serif',
} as const;

// Supported systems, exactly as navis-labs-website/components/site/logos.tsx
// marks them (status "supported"); the vendor marks are the website's own
// /public/logo assets, copied to public/images/integrations. The roadmap
// systems on that page are "soon": see ROADMAP_INTEGRATIONS.
export const INTEGRATIONS = [
  { id: "gmail", label: "Gmail", src: "images/integrations/gmail.svg", aspect: 256 / 193 },
  { id: "calendar", label: "Google Calendar", src: "images/integrations/google-calendar.svg", aspect: 1 },
  { id: "meet", label: "Google Meet", src: "images/integrations/google-meet.svg", aspect: 256 / 211 },
  { id: "drive", label: "Google Drive", src: "images/integrations/google-drive.svg", aspect: 256 / 229 },
  { id: "docs", label: "Google Docs", src: "images/integrations/google-docs.svg", aspect: 1 },
  { id: "slack", label: "Slack", src: "images/integrations/slack.svg", aspect: 512 / 321 },
] as const;
export type IntegrationId = (typeof INTEGRATIONS)[number]["id"];
/** Connected today (website logos.tsx status "supported"). */
export const LIVE_CURRENT = INTEGRATIONS;

// The seven systems the public website still lists as "Coming soon"
// (logos.tsx status "soon"). The V6 film shows them CONNECTED: it represents
// the founder-supplied launch state (src/data/navislabs_v8_launch_state.json
// FILM_LAUNCH_INTEGRATIONS); the website status may lag the film.
export const ROADMAP_INTEGRATIONS = [
  { id: "hubspot", label: "HubSpot", src: "images/integrations/hubspot.svg", aspect: 489 / 511.8 },
  { id: "salesforce", label: "Salesforce", src: "images/integrations/salesforce.svg", aspect: 256 / 180 },
  { id: "jira", label: "Jira", src: "images/integrations/jira.svg", aspect: 1 },
  { id: "github", label: "GitHub", src: "images/integrations/github.png", aspect: 1 },
  { id: "notion", label: "Notion", src: "images/integrations/notion.svg", aspect: 1 },
  { id: "zoom", label: "Zoom", src: "images/integrations/zoom.svg", aspect: 1 },
  { id: "microsoft365", label: "Microsoft 365", src: "images/integrations/microsoft-365.svg", aspect: 1 },
] as const;
export type RoadmapIntegrationId = (typeof ROADMAP_INTEGRATIONS)[number]["id"];
/**
 * Website "soon" set (brand registry only). In the V6 film these appear as
 * connected launch-state systems; the film's connector set and every status
 * live in src/data/navislabs_v8_launch_state.json and
 * navislabs_v8_product_surface_map.json.
 */
export const FUTURE_CONNECTED = ROADMAP_INTEGRATIONS;
export const isLiveSystem = (id: string) => LIVE_CURRENT.some((m) => m.id === id);
export type AnyIntegrationId = IntegrationId | RoadmapIntegrationId;

// One company story. NavisLabs runs on its own products: Abhishek (founder)
// works in the Navis App and, through Claude Code, in Navis Developer.
// The Mac user and host are the real ones on this machine (`whoami`,
// `hostname -s`). Kaveri Freightworks, Meera Iyer and every fact about them are DEMO
// DATA, in the website's Morning Intelligence vocabulary.
export const DEMO = {
  org: demoData.company.name,
  repo: demoData.repositories[0].name,
  macUser: demoData.people[0].mac_user ?? "",
  macHost: demoData.people[0].mac_host ?? "",
  user: demoData.people[0].name,
  userFirst: demoData.people[0].first,
  userEmail: demoData.people[0].email,
  customer: demoData.customers[0].name,
  contact: demoData.people[2].name,
  contactEmail: demoData.people[2].email,
  owner: demoData.people[0].name,
} as const;

/** zsh's default prompt on this Mac, in a given folder. */
export const macPrompt = (dir: string) => `${DEMO.macUser}@${DEMO.macHost} ${dir} %`;

// MCP clients and their verification state (Devtool docs/mcp/CLIENTS.md).
// Only Claude Code has a logo file on this machine (the installed Claude.app
// icon); the others are shown as text rather than as recreated marks.
export const CLIENTS = [
  { name: "Claude Code", status: "live verified", icon: "images/clients/claude.png" },
  { name: "Cursor", status: "config verified", icon: null },
  { name: "Codex", status: "config verified", icon: null },
  { name: "VS Code", status: "config verified", icon: null },
  { name: "Any MCP client", status: "Streamable HTTP", icon: null },
] as const;
