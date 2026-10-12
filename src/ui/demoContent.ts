import data from "../data/navislabs_v8_launch_state.json";
import type { AnyIntegrationId, IntegrationId } from "../config/navisBrand";

// Every entity the film shows comes from src/data/navislabs_v8_launch_state.json
// (the film-only launch-state configuration and demo data — the single source
// of truth); this module only phrases those entities for each screen. No TSX file names a person, company, customer, project or
// repository — they read the constants below. Provenance per entity:
// navislabs_entity_audit.json (REAL_AUTHORIZED / REAL_PUBLIC_PRODUCT /
// SYNTHETIC).
//
// LAUNCH STATE (V6): all thirteen systems are connected in the film
// (FILM_LAUNCH_INTEGRATIONS). Detailed evidence is shown only where the demo
// data holds a record (Salesforce, Notion, Jira, GitHub and the Google/Slack
// set); Microsoft 365, HubSpot and Zoom appear as connected infrastructure.

const person = (id: string) => {
  const p = data.people.find((x) => x.id === id);
  if (!p) throw new Error(`demo data: no person ${id}`);
  return p;
};

export const COMPANY = data.company;
export const USER = person("p_abhishek");
export const ENGINEER = person("p_arjun");
export const CONTACT = person("p_meera");
export const SOLO = person("p_solo");
export const CUSTOMER = data.customers[0];
export const PROJECT = data.projects.find((p) => p.id === "pr_sso")!;
const WORKFLOW_RAW = data.projects.find((p) => p.id === "pr_renewal_workflow")!;
export const WORKFLOW = { ...WORKFLOW_RAW, file: WORKFLOW_RAW.file ?? "" };
export const REPO = data.repositories.find((r) => r.id === "r_navislabs")!;
export const SOLO_REPO = data.repositories.find((r) => r.id === "r_riya")!;
export const DECISION = data.decisions[0];
export const COMMITMENT = data.commitments.find((c) => c.id === "m_revised_terms")!;
export const BOARD = data.commitments.find((c) => c.id === "m_board_metrics")!;
export const RENEWAL_CALL = data.meetings.find((m) => m.id === "mt_renewal_call")!;
/** The renewal call is upcoming (Thu, Oct 8): always shown with its weekday. */
export const RENEWAL_CALL_WHEN = `${RENEWAL_CALL.weekday ?? ""}${RENEWAL_CALL.weekday ? ", " : ""}${RENEWAL_CALL.date}`;
export const EMAIL = data.emails[0];
export const MOVED_ON = data.meetings.find((m) => m.id === "mt_renewal_call")?.moved_on ?? "";
const COMMITMENT_DATE = data.commitments.find((c) => c.id === "m_revised_terms")?.date ?? "";
const CHANNEL = data.commitments.find((c) => c.id === "m_revised_terms")?.channel ?? "";
export const ORDER_FORM = data.documents.find((d) => d.id === "doc_order_form")!;
export const ACCOUNT_PLAN = data.documents.find((d) => d.id === "doc_account_plan")!;
const PLAN_FACT = ACCOUNT_PLAN.fact ?? "";
export const SSO_SPEC = data.documents.find((d) => d.id === "doc_sso_spec")!;
export const AGENT = data.agents[0];
export const RUNS = data.runs;
export const RUN = data.runs[0];
export const DEV_WORKSPACE = data.developer_workspace;
export const SOLO_WORKSPACE = data.developer_workspace.solo;
export const APP_WORKSPACE = data.application_workspace;
export const INTEGRATION_SEMANTICS = data.integrations.semantics as Record<string, string>;
/** The film's launch-state connector set, in display order (all connected). */
export const LIVE_IDS = data.integrations.connected as readonly AnyIntegrationId[];
// V8: only six systems are live in the Navis backend; the other seven are UPCOMING and always
// labelled so on screen (demo configuration). Nothing is ever shown executed through them.
export const UPCOMING_IDS = new Set<string>(data.integrations.upcoming);
export const isUpcoming = (id: string) => UPCOMING_IDS.has(id);
const UPCOMING = "upcoming";
/** "Salesforce" → "Salesforce · upcoming" for upcoming systems; live systems unchanged. */
export const withStatus = (label: string, id: string) => (isUpcoming(id) ? `${label} · ${UPCOMING}` : label);
/** Nothing is shown as roadmap in the launch-state film. */
export const EXPANDING_IDS: readonly AnyIntegrationId[] = [];
export const LAUNCH_INTEGRATIONS = data.integrations.FILM_LAUNCH_INTEGRATIONS;
export const CRM = data.crm_records[0];
export const KNOWLEDGE = data.knowledge[0];
export const JIRA = data.engineering_context.issues[0];
export const CODE = data.engineering_context.code[0];

const C = CUSTOMER;
const firstOf = (name: string) => name.split(" ")[0];
/** The task Abhishek gives the agent; also the run's task. */
export const AGENT_TASK = RUN.task;
/** The one event both products act on. */
export const EVENT_LABEL = `${C.caps} · RENEWAL MOVED TO ${C.renewal_now.toUpperCase()}`;
export const EVENT_FACT = `${C.name}'s renewal moved to ${C.renewal_now}.`;

/**
 * S01, V01 "Your people and agents see different truths." The same customer
 * seen two ways: the person's inbox has the move to the new date; the agent's
 * workflow file still has the old one (the file the agent updates in S15).
 */
export const TWO_TRUTHS = {
  people: {
    source: "gmail" as IntegrationId,
    from: `${CONTACT.name} · ${EMAIL.date}`,
    subject: EMAIL.subject,
    text: EMAIL.ask,
    label: `${C.short} renewal`,
    value: C.renewal_now,
  },
  agents: {
    session: "Agent session",
    file: WORKFLOW.file,
    code: `renewsOn: "${C.renewal_was_iso}",`,
    label: `${C.short} renewal`,
    value: C.renewal_was,
  },
} as const;

/** V02 (P1): the truth, a piece in each system that holds one (S01). */
export const OPENING_SIGNALS: readonly { kind: string; text: string; source: AnyIntegrationId; when: string; at: "signalDecision" | "signalCustomer" | "signalCommitment" | "signalMeeting" | "signalContext" | "signalAccount" | "signalCrm" | "signalJira" | "signalKnowledge" }[] = [
  { kind: "Email", text: `${CONTACT.name}: ${EMAIL.ask.charAt(0).toLowerCase()}${EMAIL.ask.slice(1)}`, source: "gmail", when: `${C.name} · ${EMAIL.date}`, at: "signalDecision" },
  { kind: "Meeting", text: `${RENEWAL_CALL.title} moved to ${RENEWAL_CALL_WHEN}.`, source: "calendar", when: "Google Calendar", at: "signalCustomer" },
  { kind: "Commitment", text: `Revised terms promised by ${COMMITMENT.due}.`, source: "slack", when: CHANNEL, at: "signalCommitment" },
  { kind: "Document", text: `${ORDER_FORM.title}.`, source: "drive", when: "Google Drive", at: "signalMeeting" },
  { kind: "Decision", text: `${DECISION.short}.`, source: "meet", when: `${DECISION.made_in} · ${DECISION.date}`, at: "signalContext" },
  { kind: "Account", text: `${PLAN_FACT}.`, source: "docs", when: `${ACCOUNT_PLAN.title} · ${ACCOUNT_PLAN.date}`, at: "signalAccount" },
  { kind: "Opportunity", text: `${CRM.name} — closes ${CRM.close_date}.`, source: "salesforce", when: "Salesforce", at: "signalCrm" },
  { kind: "Issue", text: `${JIRA.key} · ${JIRA.title}.`, source: "jira", when: "Jira", at: "signalJira" },
  { kind: "Policy", text: `${KNOWLEDGE.title}: annual plans renew on current terms.`, source: "notion", when: `Notion · ${KNOWLEDGE.date}`, at: "signalKnowledge" },
];

/** S02: what a person copies by hand from four systems. */
export const HAND_COPIES: readonly { id: IntegrationId; text: string }[] = [
  { id: "gmail", text: `${firstOf(CONTACT.name)}: move our renewal to ${C.renewal_now}?` },
  { id: "slack", text: `Revised terms promised by ${COMMITMENT.due}.` },
  { id: "drive", text: "Order form: annual plan, current terms." },
  { id: "meet", text: "Annual plans keep current terms." },
];
export const HAND_NOTE_TITLE = `${C.short} renewal — notes, rebuilt by hand`;

export const MORNING = {
  greeting: `Good morning, ${USER.first}.`,
  headline: `${C.name}'s renewal moved, and a reply is waiting on you.`,
  date: APP_WORKSPACE.date,
  synced: APP_WORKSPACE.synced,
} as const;

/**
 * "Today at a glance" (Navis-AI CountStrip.tsx): the six real tiles, their
 * tones and empty labels. Counts are demo data — except Updates, which the
 * product always reports as 0 ("Navis has no temporal diff to count").
 */
const G = APP_WORKSPACE.glance;
export const GLANCE: readonly { label: string; count: number; tone: "violet" | "rose" | "emerald" | "amber" | "sky"; icon: "sparkles" | "alert" | "check" | "calendar" | "inbox"; emptyLabel: string }[] = [
  { label: "Decisions", count: G.decisions, tone: "violet", icon: "sparkles", emptyLabel: "Nothing waiting" },
  { label: "Risks", count: G.risks, tone: "rose", icon: "alert", emptyLabel: "All clear" },
  { label: "Actions today", count: G.actions, tone: "emerald", icon: "check", emptyLabel: "Nothing to do" },
  { label: "Meetings", count: G.meetings, tone: "amber", icon: "calendar", emptyLabel: "Empty calendar" },
  { label: "Waiting on you", count: G.waiting, tone: "sky", icon: "inbox", emptyLabel: "Inbox zero" },
  { label: "Updates", count: G.updates, tone: "sky", icon: "sparkles", emptyLabel: "No changes" },
];

export type Priority = {
  readonly tag: string; // the backend's kind_label, founder language
  readonly tone: "risk" | "watch";
  readonly title: string;
  readonly detail: string;
  readonly owner: string;
  readonly chips: readonly { label: string; value: string }[];
};

export const PRIORITIES: readonly Priority[] = [
  {
    tag: "Revenue at risk",
    tone: "risk",
    title: `${C.name}'s renewal moved — terms not yet confirmed`,
    detail: `${CONTACT.name} asked to move the renewal to ${C.renewal_now} and confirm the annual terms. Revised terms were promised by ${COMMITMENT.due}.`,
    owner: "You",
    chips: [
      { label: "Gmail", value: "Renewal moved" },
      { label: withStatus("Salesforce", "salesforce"), value: `Opportunity · closes ${CRM.close_date}` },
      { label: "Calendar", value: `Renewal call · ${RENEWAL_CALL_WHEN}` },
    ],
  },
  {
    tag: "Delivery blocked",
    tone: "watch",
    title: `${C.short}'s ${PROJECT.name} is blocked on review`,
    detail: `${PROJECT.ticket} has waited three days for review; ${C.short}'s renewal call is ${RENEWAL_CALL_WHEN}.`,
    owner: ENGINEER.name,
    // Engineering context: the issue tracker and the spec doc.
    chips: [
      { label: withStatus("Jira", "jira"), value: `${JIRA.key} · ${JIRA.status}` },
      { label: "Docs", value: SSO_SPEC.title },
    ],
  },
  {
    tag: "Commitment due",
    tone: "watch",
    title: BOARD.text,
    detail: `Committed ${BOARD.days_ago} days ago in the ${BOARD.made_in}. The board deck hasn't been touched since.`,
    owner: "You",
    chips: [{ label: "Meet", value: "Q3 review notes" }],
  },
];

/** The one verified change the What changed section may show ('learning' only). */
export const JUST_LEARNED = {
  tag: "Just learned",
  title: `${C.name}'s renewal moved to ${C.renewal_now}`,
  detail: `Observed in ${CONTACT.name}'s email on ${EMAIL.date}. The annual terms still need confirming.`,
  chip: { label: "Gmail", value: `${CONTACT.name} · ${EMAIL.date}` },
} as const;

export const CUSTOMER_NEXT = `Confirm ${C.renewal_now} and the annual terms with ${CONTACT.first}.`;

/** The signals behind the finding (WhyThisDrawer "What supports this"); upcoming systems are labelled so. */
export type Signal = {
  readonly field: string;
  readonly label: string;
  readonly value: string;
  readonly source: AnyIntegrationId;
  readonly sourceLabel: string;
  readonly when: string; // timeline
  readonly synced: string; // freshness: connector last success
};

export const CUSTOMER_SIGNALS: readonly Signal[] = [
  { field: "email", label: "Email", value: `${CONTACT.name} asked to move the renewal to ${C.renewal_now} and confirm terms.`, source: "gmail", sourceLabel: "Gmail", when: EMAIL.date, synced: "synced 2m ago" },
  { field: "meeting", label: "Meeting", value: `${RENEWAL_CALL.title} moved to ${RENEWAL_CALL_WHEN}.`, source: "calendar", sourceLabel: "Google Calendar", when: MOVED_ON, synced: "synced 2m ago" },
  { field: "decision", label: "Decision", value: `${DECISION.short} (${DECISION.made_in.toLowerCase()}).`, source: "meet", sourceLabel: "Google Meet", when: DECISION.date, synced: "synced 4m ago" },
  { field: "document", label: "Document", value: `${C.short} order form — annual plan on current terms.`, source: "drive", sourceLabel: "Google Drive", when: ORDER_FORM.date, synced: "synced 6m ago" },
  { field: "account", label: "Account", value: `${PLAN_FACT}.`, source: "docs", sourceLabel: "Google Docs", when: ACCOUNT_PLAN.date, synced: "synced 8m ago" },
  { field: "commitment", label: "Commitment", value: `Revised terms promised to ${C.short} by ${COMMITMENT.due} — not sent.`, source: "slack", sourceLabel: `Slack · ${CHANNEL}`, when: COMMITMENT_DATE, synced: "synced 1m ago" },
  { field: "opportunity", label: "Opportunity", value: `${CRM.name} still closes ${CRM.close_date} in the CRM.`, source: "salesforce", sourceLabel: withStatus("Salesforce", "salesforce"), when: EMAIL.date, synced: "synced 3m ago" },
];

/** The reply the person reviews, edits and approves. */
export const CUSTOMER_DRAFT = {
  reason: `${CONTACT.first} asked on ${EMAIL.date} to move the renewal and confirm the annual terms.`,
  to: CONTACT.email,
  from: `${CONTACT.name} · ${C.name}`,
  subject: `Re: ${EMAIL.subject}`,
  paragraphs: [
    `Hi ${CONTACT.first},`,
    `Thanks — ${C.renewal_now} works for the renewal. Your annual plan keeps its current terms; usage-based pricing applies to new accounts only.`,
    "",
    `Best,\n${USER.first}`,
  ],
  replaced: "I'll send the revised order form this week.",
} as const;

/** What Navis Developer returns to the agent about the same customer. */
export type ContextFact = {
  readonly label: string;
  readonly kind: string;
  readonly text: string;
  readonly source: AnyIntegrationId;
  readonly sourceLabel: string;
  readonly occurredAt: string;
  readonly lastSuccessAt: string;
};

export const CUSTOMER_CONTEXT: readonly ContextFact[] = [
  { label: "Renewal date", kind: "fact", text: `${C.name}'s renewal moved to ${C.renewal_now} (was ${C.renewal_was}).`, source: "gmail", sourceLabel: `Gmail · ${CONTACT.name}`, occurredAt: EMAIL.date_iso, lastSuccessAt: "09:42" },
  { label: "Owner", kind: "fact", text: `${PLAN_FACT}.`, source: "docs", sourceLabel: `Docs · ${ACCOUNT_PLAN.title}`, occurredAt: "2026-09-09", lastSuccessAt: "09:36" },
  { label: "Relevant decision", kind: "decision", text: DECISION.text, source: "meet", sourceLabel: `Meet · ${DECISION.made_in}`, occurredAt: DECISION.date_iso, lastSuccessAt: "09:40" },
  { label: "Open commitment", kind: "commitment", text: COMMITMENT.text, source: "slack", sourceLabel: `Slack · ${CHANNEL}`, occurredAt: "2026-09-30", lastSuccessAt: "09:41" },
  { label: "Renewal call", kind: "fact", text: `${RENEWAL_CALL.title} moved to ${RENEWAL_CALL_WHEN}.`, source: "calendar", sourceLabel: `Calendar · ${C.short} renewal`, occurredAt: EMAIL.date_iso, lastSuccessAt: "09:42" },
];

/** The MCP tool result as Claude Code prints it (S12): compact rows. */
export const RESULT_ROWS: readonly { fact: string; source: string; fresh: string }[] = [
  { fact: `Renewal moved to ${C.renewal_now}`, source: `gmail · ${EMAIL.date}`, fresh: "ok · 09:42" },
  { fact: `Owner: ${USER.name}`, source: `docs · ${ACCOUNT_PLAN.date}`, fresh: "ok · 09:36" },
  { fact: "Annual plans keep their terms", source: `meet · ${DECISION.date}`, fresh: "ok · 09:40" },
  { fact: `Revised terms promised by ${COMMITMENT.due}`, source: `slack · ${COMMITMENT_DATE}`, fresh: "ok · 09:41" },
  { fact: `${CONTACT.first}: "${EMAIL.ask.replace("our renewal ", "")}"`, source: `gmail · ${EMAIL.date}`, fresh: "ok · 09:42" },
  { fact: `Opportunity still closes ${CRM.close_date}`, source: `salesforce · ${UPCOMING}`, fresh: "ok · 09:43" },
];

/** The agent's lines in the Claude Code transcript (S10–S15). */
export const AGENT_LINES = {
  read: WORKFLOW.file,
  needs: `This depends on what changed with ${C.name}'s renewal and which terms apply. Asking Navis Developer for company context.`,
  reason: [`Using Navis context: renewal moved to ${C.renewal_now} `, `(gmail, ${EMAIL.date})`, `; annual plans keep their terms `, `(meet, ${DECISION.date})`, ". Updating the workflow."] as const,
  done: `${C.name} now renews ${C.renewal_now} (${CONTACT.name}, Gmail, ${EMAIL.date}) on its current annual terms (${DECISION.made_in.toLowerCase()}, ${DECISION.date}). Still open: revised terms owed to ${C.short} by ${COMMITMENT.due} — owner: ${USER.name}.`,
} as const;

/** Evidence opened out (S07): every system that holds a piece resolves into one customer state. */
export const SYSTEM_FACTS: readonly { id: AnyIntegrationId; role: string; fact: string; when: string; conflict?: string }[] = [
  // The chain, left column first: customer communication → CRM state → meeting context → decision;
  // then documents, commitment and engineering context. The CRM alone does not hold the whole truth.
  { id: "gmail", role: "Customer email", fact: `${CONTACT.first}: can we move to ${C.renewal_now}?`, when: EMAIL.date },
  { id: "salesforce", role: withStatus("CRM", "salesforce"), fact: `Closes ${CRM.close_date} · owner ${USER.name}`, when: EMAIL.date, conflict: `CRM ${CRM.close_date} ≠ email ${C.renewal_now}` },
  { id: "calendar", role: "Meeting", fact: `Renewal call moved to ${RENEWAL_CALL_WHEN}`, when: MOVED_ON },
  { id: "meet", role: "Decision", fact: DECISION.short, when: DECISION.date },
  { id: "drive", role: "Document", fact: "Order form: annual plan", when: ORDER_FORM.date },
  { id: "docs", role: "Account plan", fact: PLAN_FACT, when: ACCOUNT_PLAN.date },
  { id: "slack", role: "Commitment", fact: COMMITMENT.short, when: COMMITMENT_DATE },
  { id: "jira", role: withStatus("Engineering", "jira"), fact: `${JIRA.key} · ${JIRA.title}`, when: JIRA.date },
];

/** The resolved state of the customer, entity by entity (S07). */
export const CUSTOMER_STATE: readonly { entity: string; value: string; was?: string; now?: string }[] = [
  { entity: "Customer", value: `${C.name} · renews ${C.renewal_now}` },
  { entity: "People", value: `${CONTACT.name} · ${USER.name}` },
  { entity: "Decision", value: DECISION.short },
  { entity: "Commitment", value: `Revised terms by ${COMMITMENT.due}` },
  { entity: "Meeting", value: `Renewal call · ${RENEWAL_CALL_WHEN} (upcoming)` },
  { entity: "Opportunity", value: `Closes ${CRM.close_date} → move to ${C.renewal_now}`, was: CRM.close_date, now: C.renewal_now },
  { entity: "Next", value: `Reply to ${CONTACT.first}; then the CRM` },
];

/** S04: the kinds of signal, each from the system that emits it. */
export const FLOW_SIGNALS: readonly { label: string; from: AnyIntegrationId; live: boolean }[] = [
  { label: "Customer response", from: "gmail", live: true },
  { label: "Meeting", from: "calendar", live: true },
  { label: "Discussion", from: "meet", live: true },
  { label: "Team signal", from: "slack", live: true },
  { label: "Project document", from: "drive", live: true },
  { label: "Account context", from: "docs", live: true },
  { label: withStatus("Opportunity", "salesforce"), from: "salesforce", live: false },
  { label: withStatus("Company knowledge", "notion"), from: "notion", live: false },
  { label: withStatus("Engineering issue", "jira"), from: "jira", live: false },
];

/** The solo developer's workspace (S16). */
export const SOLO_STATE = {
  workspace: SOLO_WORKSPACE.name,
  repo: SOLO_REPO.name,
  branch: SOLO_REPO.branch,
  task: SOLO_WORKSPACE.task,
  decision: SOLO_WORKSPACE.decision,
  open: SOLO_WORKSPACE.open,
  user: SOLO.first,
  email: SOLO.email,
} as const;

/** The NavisLabs team in the Developer Console (S11). */
export const TEAM = DEV_WORKSPACE.members.map((m) => {
  const p = person(m.person);
  return { name: p.name, email: p.email, applicationRole: m.application_role, developerRole: m.developer_role, state: m.state };
});

/**
 * S09, after "Then the company acts.": the same event as the company's other
 * systems hold it. Navis does not update them itself — it shows where the
 * event still has to land and who owns that next step.
 */
export const ACROSS_SYSTEMS: readonly { id: AnyIntegrationId; system: string; state: string; status: "done" | "next" | "related"; owner: string; upcoming: boolean }[] = [
  { id: "gmail", system: "Gmail", state: "Reply sent · Gmail accepted", status: "done", owner: USER.name, upcoming: isUpcoming("gmail") },
  { id: "salesforce", system: "Salesforce", state: `Opportunity closes ${CRM.close_date} → ${C.renewal_now}`, status: "next", owner: USER.name, upcoming: isUpcoming("salesforce") },
  { id: "github", system: "GitHub", state: `${CODE.path.split("/").pop()} still renews ${C.renewal_was}`, status: "next", owner: "Engineering · agent", upcoming: isUpcoming("github") },
  { id: "jira", system: "Jira", state: `${JIRA.key} · ${JIRA.title}`, status: "related", owner: ENGINEER.name, upcoming: isUpcoming("jira") },
];

/** The team's work state that carries into the next session (S16, P5). */
export const TEAM_STATE = {
  repo: REPO.name,
  branch: REPO.branch,
  task: data.team_workstate.task,
  decision: data.team_workstate.decision,
  open: data.team_workstate.open,
  user: USER.first,
} as const;
