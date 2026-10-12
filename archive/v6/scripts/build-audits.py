#!/usr/bin/env python3
"""Writes the picture-lock audits from the demo data and a static read of src/:

  navislabs_entity_audit.json        every entity on screen, its provenance and authorization
  navislabs_entity_consistency.json  the same facts across Application, Developer and the hero
  developer_capability_audit.json    MCP / API / SDK / CLI / Console / Runs: what is real
  team_permission_audit.json         invite, roles, organization, personal workspace, keys, scope

V6: the data is the film-only launch state (src/data/navislabs_v6_launch_state.json); the 13 connectors are
CONNECTED in the film's launch configuration, and each row records the public website's and the local source's status.
Run after scripts/build-film-data-v6.py (npm run data:build). Reads only; Devtool and Navis-AI are cited by path
(read-only research), never modified.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import film_analysis as fa  # noqa: E402

ROOT = fa.ROOT
data = fa.demo_data()
ent_scenes, _ = fa.entity_scenes()
integ = data["integrations"]
integ_scenes = fa.integration_scenes(integ["connected"], [])
APP_SCENES = {"S05", "S06", "S07", "S08", "S09"}
DEV_SCENES = {"S10", "S11", "S12", "S13", "S14", "S15", "S16"}
HERO_SCENES = {"S17"}
SRC = "src/data/navislabs_v6_launch_state.json"

AUTH = {
    "REAL_AUTHORIZED": True,
    "REAL_PUBLIC_PRODUCT": True,
    "SYNTHETIC": True,
}
KIND = {"p": "person", "c": "customer", "pr": "project", "d": "decision", "m": "commitment", "mt": "meeting",
        "e": "email", "doc": "document", "r": "repository", "a": "agent", "t": "team", "w": "workspace", "org": "organization",
        "crm": "crm_record", "kn": "knowledge", "eng": "issue", "code": "code"}


def kind_of(eid):
    return KIND.get(eid.split("_")[0], "entity")


def row(entity, value, source, prov, scenes, replacement=None, note=None, authorized=None):
    r = {
        "entity": entity,
        "value": value,
        "source": source,
        "real_or_synthetic": prov,
        "authorized_for_public_video": AUTH.get(prov, False) if authorized is None else authorized,
        "scenes": scenes,
        "replacement_if_needed": replacement,
    }
    if note:
        r["note"] = note
    return r


entities = []
c = data["company"]
entities.append(row(f"organization:{c['id']}", c["name"], f"{SRC}#company", c["provenance"], ent_scenes.get(c["id"], []),
                    note="The company itself, shown using its own products. Brand name from navislabs.in."))
entities.append(row("organization:website", c["website"], f"{SRC}#company.website", "REAL_AUTHORIZED", ["S18"], note="End-card URL."))
for p in data["people"]:
    sc = ent_scenes.get(p["id"], [])
    real = p["provenance"] == "REAL_AUTHORIZED"
    entities.append(row(f"person:{p['id']}", p["name"], f"{SRC}#people/{p['id']}", p["provenance"], sc,
                        replacement=None if real else ("Mulayam Kumar (CTO) — only with written approval" if p["id"] == "p_sam" else None),
                        note=p.get("note")))
    entities.append(row(f"person:{p['id']}.email", p["email"], f"{SRC}#people/{p['id']}.email", p["provenance"], sc,
                        replacement="remove the address from screen if not approved for public release" if real else None,
                        note="The founder's own work address, shown at the founder's request." if real else "Reserved example domain (RFC 2606); routes nowhere."))
    if p.get("mac_user"):
        entities.append(row(f"person:{p['id']}.mac", f"{p['mac_user']}@{p['mac_host']}", f"{SRC}#people/{p['id']}.mac_user/mac_host", p["provenance"],
                            [s for s in sc if s in DEV_SCENES], replacement="a neutral prompt such as 'abhishek@navislabs'",
                            note="The real macOS user and host on the founder's machine, shown in terminal prompts at the founder's request."))
for coll in ("teams", "customers", "projects", "decisions", "commitments", "meetings", "emails", "documents", "repositories"):
    for x in data[coll]:
        value = x.get("name") or x.get("title") or x.get("subject") or x.get("text")
        entities.append(row(f"{kind_of(x['id'])}:{x['id']}", value, f"{SRC}#{coll}/{x['id']}", x["provenance"], ent_scenes.get(x["id"], []), note=x.get("note")))
for a in data["agents"]:
    entities.append(row(f"agent:{a['id']}", f"{a['name']} ({a['client']})", f"{SRC}#agents/{a['id']}", a["provenance"], ent_scenes.get(a["id"], []), note=a.get("note")))
for rn in data["runs"]:
    entities.append(row(f"run:{rn['id']}", rn["task"], f"{SRC}#runs/{rn['id']}", rn.get("provenance", "SYNTHETIC"), ent_scenes.get(f"run_{rn['id']}", []),
                        note="Demo run; economics columns show '—' (not recorded)."))
solo = data["developer_workspace"]["solo"]
entities.append(row(f"workspace:{solo['id']}", solo["name"], f"{SRC}#developer_workspace.solo", solo["provenance"], ent_scenes.get(solo["id"], [])))
for x in data["crm_records"]:
    entities.append(row(f"crm_record:{x['id']}", f"{x['object']} · {x['name']} · closes {x['close_date']}", f"{SRC}#crm_records/{x['id']}", x["provenance"],
                        ent_scenes.get(x["id"], []), note=x.get("note")))
for x in data["knowledge"]:
    entities.append(row(f"knowledge:{x['id']}", f"{x['title']} — {x['fact']}", f"{SRC}#knowledge/{x['id']}", x["provenance"], ent_scenes.get(x["id"], []),
                        note="FILM DEMO RECORD in Notion (launch state)."))
for x in data["engineering_context"]["issues"]:
    entities.append(row(f"issue:{x['id']}", f"{x['key']} · {x['title']} · {x['status']}", f"{SRC}#engineering_context.issues/{x['id']}", x["provenance"],
                        ent_scenes.get(x["id"], []), note="FILM DEMO RECORD in Jira (launch state)."))
for x in data["engineering_context"]["code"]:
    entities.append(row(f"code:{x['id']}", f"{x['path']} ({x['fact']} → {x['after']})", f"{SRC}#engineering_context.code/{x['id']}", x["provenance"],
                        ent_scenes.get(x["id"], []), note=x.get("note")))
tw = data["team_workstate"]
entities.append(row("workstate:team", f"{tw['task']} / {tw['decision']} / {tw['open']}", f"{SRC}#team_workstate", tw["provenance"],
                    sorted(set(ent_scenes.get("r_navislabs", [])) & {"S16"}), note="The company's checkpoint restored in the next session (S16)."))
for x in integ["FILM_LAUNCH_INTEGRATIONS"]:
    entities.append(row(f"integration:{x['id']}", x["label"], f"{SRC}#integrations.FILM_LAUNCH_INTEGRATIONS/{x['id']}; mark: navis-labs-website/public/logo",
                        "REAL_PUBLIC_PRODUCT", integ_scenes.get(x["id"], []),
                        note=f"FILM STATUS: {x['film_status']}. PUBLIC WEBSITE STATUS: currently shown as '{x['public_website_status']}'. "
                        f"LOCAL SOURCE: {x['local_source_status']}. In the film: {x['in_film']}. "
                        "Vendor mark used nominatively to name a connector; no partnership implied."))
for name, status, icon in [("Claude Code", "LIVE VERIFIED", True), ("Cursor", "CONFIG VERIFIED", False), ("Codex", "CONFIG VERIFIED", False), ("VS Code", "CONFIG VERIFIED", False)]:
    entities.append(row(f"mcp_client:{name}", name, "Devtool/docs/mcp/CLIENTS.md", "REAL_PUBLIC_PRODUCT", ["S18"] + (["S11"] if name == "Claude Code" else []),
                        note=f"{status}. " + ("Icon from the installed Claude.app (public/images/clients/claude.png); nominative use." if icon else "Text only; no recreated mark.")))
restricted = [
    row("restricted:Mulayam Kumar", "Mulayam Kumar", "founder brief", "REAL_PERSON", [], authorized=False,
        replacement="Sam Rivera (SYNTHETIC) stands in until written approval", note="Not shown anywhere in the film (validator: entity)."),
    row("restricted:Digantara", "Digantara", "founder brief", "REAL_COMPANY", [], authorized=False,
        replacement="Acme Corp (SYNTHETIC)", note="Not shown anywhere in the film; no customer relationship is implied."),
]
entities += restricted

entity_audit = {
    "about": "Every entity the V6 review cut can put on screen, where it comes from, whether it is real or synthetic, and whether it is cleared for a public video. scenes = scenes whose source reads the entity (static analysis, scripts/film_analysis.py).",
    "provenance_legend": {
        "REAL_AUTHORIZED": "NavisLabs' own identity (company, founder), used at the founder's request",
        "REAL_PUBLIC_PRODUCT": "a real public product named nominatively (an integration, an MCP client)",
        "SYNTHETIC": "invented demo data; reserved example domains; no real person or company",
        "REAL_PERSON / REAL_COMPANY": "restricted names: not shown without written authorization",
    },
    "summary": {
        "entities": len(entities),
        "real_authorized": sum(e["real_or_synthetic"] == "REAL_AUTHORIZED" for e in entities),
        "real_public_product": sum(e["real_or_synthetic"] == "REAL_PUBLIC_PRODUCT" for e in entities),
        "synthetic": sum(e["real_or_synthetic"] == "SYNTHETIC" for e in entities),
        "restricted_not_shown": [e["value"] for e in restricted],
        "confirm_before_public_release": [e["value"] for e in entities if e["replacement_if_needed"] and e["real_or_synthetic"] == "REAL_AUTHORIZED"],
    },
    "entities": entities,
}

# ---- consistency: one company, one customer state, two products -------
cust = data["customers"][0]
email = data["emails"][0]
dec = data["decisions"][0]
com = next(x for x in data["commitments"] if x["id"] == "m_revised_terms")
run = data["runs"][0]
wf = next(x for x in data["projects"] if x["id"] == "pr_renewal_workflow")


def spans(eid):
    s = set(ent_scenes.get(eid, []))
    return {"application": sorted(s & APP_SCENES), "developer": sorted(s & DEV_SCENES), "hero": sorted(s & HERO_SCENES)}


shared = []
for eid, fact, value in [
    ("c_acme", "customer", cust["name"]),
    ("c_acme", "renewal moved to", cust["renewal_now"]),
    ("p_jordan", "customer contact", next(p["name"] for p in data["people"] if p["id"] == "p_jordan")),
    ("e_move_renewal", "the email", email["subject"]),
    ("d_annual_terms", "the decision", dec["short"]),
    ("m_revised_terms", "the commitment", com["short"]),
    ("p_abhishek", "the person / key owner", next(p["name"] for p in data["people"] if p["id"] == "p_abhishek")),
    ("org_navislabs", "the organization", data["company"]["name"]),
]:
    sp = spans(eid)
    shared.append({"entity": eid, "fact": fact, "value": value, "source": SRC, **sp,
                   "in_both_products": bool(sp["application"]) and bool(sp["developer"])})
consistency = {
    "about": "The same company, customer, email, decision and commitment in the Navis App and Navis Developer, read from one record each (src/data/navislabs_v6_launch_state.json → src/ui/demoContent.ts). No scene writes these values itself (validator: data_consistency).",
    "single_source_of_truth": SRC,
    "shared_across_products": shared,
    "developer_only": [
        {"entity": f"run_{run['id']}", "fact": "the agent run", "value": f"{run['id']} · {run['task']} · {run['status']} · {run['duration']}", "scenes": ent_scenes.get(f"run_{run['id']}", [])},
        {"entity": wf["id"], "fact": "the file the agent edits", "value": wf["file"], "scenes": ent_scenes.get(wf["id"], [])},
        {"entity": solo["id"], "fact": "the solo developer's personal workspace", "value": solo["name"], "scenes": ent_scenes.get(solo["id"], [])},
        {"entity": "team_workstate", "fact": "the team's checkpoint (next session)", "value": f"{tw['decision']} Next: {tw['open']}", "scenes": ["S16"]},
    ],
    "launch_state_bridge": [
        {"entity": x["id"], "system": x["system"], "value": v, "scenes": ent_scenes.get(x["id"], [])}
        for x, v in [(data["crm_records"][0], f"Opportunity closes {data['crm_records'][0]['close_date']} (the email moves it to {cust['renewal_now']})"),
                     (data["knowledge"][0], data["knowledge"][0]["fact"]),
                     (data["engineering_context"]["issues"][0], f"{data['engineering_context']['issues'][0]['key']} · {data['engineering_context']['issues'][0]['title']}"),
                     (data["engineering_context"]["code"][0], f"{data['engineering_context']['code'][0]['path']}: {data['engineering_context']['code'][0]['fact']} → {data['engineering_context']['code'][0]['after']}")]
    ],
    "checks": {
        "customer_in_both_products": shared[0]["in_both_products"],
        "decision_in_both_products": next(s for s in shared if s["entity"] == "d_annual_terms")["in_both_products"],
        "commitment_in_both_products": next(s for s in shared if s["entity"] == "m_revised_terms")["in_both_products"],
        "run_steps_cite_only_systems_with_demo_records": all(
            all(x not in st["what"].lower() for x in ("hubspot", "microsoft 365", "zoom")) for st in run.get("steps", [])
        ),
        "crm_close_date_is_the_old_renewal_date": data["crm_records"][0]["close_date"] == cust["renewal_was"],
        "run_window": f"{run['steps'][0]['at']} → {run['steps'][-1]['at']} ({run['duration']})",
        "updates_tile_is_zero": data["application_workspace"]["glance"]["updates"] == 0,
    },
}

# ---- developer capabilities -------------------------------------------------
cap = {
    "about": "What each Navis Developer surface shown in the film is, in fact. implemented = in the Devtool source; private_preview = implemented, not publicly released; published = available from a public registry or host; working = how it was verified. Sources are read-only research paths (~/Desktop/Devtool).",
    "surfaces": [
        {"surface": "MCP server", "implemented": True, "private_preview": True, "published": False,
         "working": "Claude Code LIVE VERIFIED 2026-09-08 (stdio, tools/list, navis_me, a correct permission refusal); Cursor / Codex / VS Code CONFIG VERIFIED only",
         "safe_to_show": True, "shown_as": "S11: claude mcp add navis --env NAVIS_API_KEY=navis_<prefix>_<secret> -- node ./services/mcp-server/dist/stdio.js → claude mcp list → ✓ Connected",
         "secrets": "placeholder key only (navis_<prefix>_<secret>)", "source": ["Devtool/services/mcp-server", "Devtool/docs/mcp/CLIENTS.md", "Devtool/apps/dashboard/src/features/connect/data/surfaces.ts"]},
        {"surface": "Developer API", "implemented": True, "private_preview": True, "published": False,
         "working": "implemented in source; not publicly hosted, so the film uses $NAVIS_BASE_URL",
         "safe_to_show": True, "shown_as": "S13: curl -s \"$NAVIS_BASE_URL/developer/context\" -H \"X-API-Key: $NAVIS_API_KEY\" → items · sources · freshness (demo values, real field names)",
         "secrets": "$NAVIS_API_KEY placeholder; the organization comes from the key, never a parameter", "source": ["Devtool/packages/api-client/src/credentials.ts", "Devtool/services/mcp-server/src/tools/register.ts"]},
        {"surface": "TypeScript SDK (@navis/sdk 0.1.0)", "implemented": True, "private_preview": True, "published": False,
         "working": "local tarball install (npm install ./navis-sdk-0.1.0.tgz)", "safe_to_show": True,
         "shown_as": "S13: npm install ./navis-sdk-0.1.0.tgz · '# @navis/sdk 0.1.0 · local package · not on npm yet'", "secrets": "process.env.NAVIS_API_KEY",
         "source": ["Devtool/apps/dashboard/src/features/connect/data/surfaces.ts (SDK_PACKAGES)"]},
        {"surface": "Python SDK (navis-sdk wheel)", "implemented": True, "private_preview": True, "published": False, "working": "wheel built locally", "safe_to_show": True,
         "shown_as": "named on the Connect page only", "source": ["surfaces.ts SDK_PACKAGES"]},
        {"surface": "CLI (navis)", "implemented": True, "private_preview": True, "published": False, "working": "built from packages/cli; not on npm", "safe_to_show": True,
         "shown_as": "S16: navis workstate checkpoint → next session: NAVIS WORK CONTINUITY restored", "source": ["Devtool/packages/cli/src/commands/workstate.ts", "Devtool/packages/cli/src/workstate/restore.ts"]},
        {"surface": "Console › Connect", "implemented": True, "private_preview": True, "published": False, "working": "dashboard app source", "safe_to_show": True,
         "shown_as": "S11: MCP · API · SDK · CLI cards", "source": ["Devtool/apps/dashboard/src/features/connect"]},
        {"surface": "Console › Runs / Run detail", "implemented": True, "private_preview": True, "published": False,
         "working": "designed and implemented; rows are demo data", "safe_to_show": True,
         "shown_as": "S15: one run (7c2e91a0) with a 5-step timeline; Outcome 'Not judged'; Model/Tokens/Cost/Latency shown as '—'",
         "source": ["Devtool/apps/dashboard/src/features/runs/RunsPanel.tsx", "RunDetailPanel.tsx", "Devtool/packages/types/src/run.ts"]},
        {"surface": "Console › Projects", "implemented": False, "private_preview": False, "published": False, "working": "not a Console concept", "safe_to_show": False,
         "shown_as": "not shown", "source": ["Devtool/apps/dashboard/src/lib/navigation.ts (no Projects entry)"]},
        {"surface": "Central policy engine", "implemented": False, "private_preview": False, "published": False, "working": "'Not enabled yet' in the product", "safe_to_show": False,
         "shown_as": "not shown as live; S14 shows only per-credential permission checks", "source": ["Devtool/apps/dashboard/src/features/policies/PoliciesPanel.tsx"]},
        {"surface": "Model use", "implemented": True, "private_preview": True, "published": False, "working": "Navis calls no generative model", "safe_to_show": True,
         "shown_as": "S13: 'No model is called · Navis grounds · your agent reasons'", "source": ["Devtool/services/mcp-server/src/tools/register.ts"]},
    ],
    "claims_avoided": ["no npm install @navis/sdk shown as working", "no public base URL", "no real key", "no economics numbers", "no outcome judgement", "no Cursor/Codex/VS Code shown as live"],
}

team = {
    "about": "Team and permission behaviour shown in the film, against the Devtool source (read-only).",
    "items": [
        {"capability": "Invite a member", "implemented": True, "shown": "S11 Members: 'Add a member' → 'Add member' → row shows 'Invited'",
         "source": "Devtool/apps/dashboard/src/features/settings/InviteMemberForm.tsx L119, L190; MembersPanel.tsx L179"},
        {"capability": "Member list (Application role · Developer access)", "implemented": True, "shown": "S11: Abhishek Meena (Founder · owner · Active), Sam Rivera (Member · developer · Invited); S16: the company's Members as the team",
         "source": "MembersPanel.tsx L146", "data": "SYNTHETIC except the founder"},
        {"capability": "Developer roles", "implemented": True, "values": ["owner", "admin", "developer", "viewer"], "shown": "owner, developer",
         "source": "Devtool/packages/types/src/auth.ts L160 DEVELOPER_ROLES"},
        {"capability": "Developer access is explicit, never inherited", "implemented": True, "shown": "not stated on screen", "source": "MembersPanel.tsx L198"},
        {"capability": "Organization (company workspace)", "implemented": True, "shown": "S11 Members; S17 'One company · NavisLabs'", "source": "OrganizationPanel.tsx"},
        {"capability": "Personal workspace (sign-up 'For myself')", "implemented": True, "shown": "S16: 'For myself' at sign-up → Workspace 'Personal', Workspace ownership 'Owner' (Navis Developer without the Navis App)",
         "source": "Devtool/apps/dashboard/src/features/auth/SignUpForm.tsx; MembersPanel.tsx L241; lib/format.ts"},
        {"capability": "API key", "implemented": True, "shown": "placeholders only (navis_<prefix>_<secret>, $NAVIS_API_KEY)", "source": "Devtool/packages/api-client/src/credentials.ts"},
        {"capability": "Agent credential permissions", "implemented": True, "values": ["view_memory", "view_state", "…"], "shown": "S14: key with view_memory → authorized; key without → exact refusal",
         "source": "Devtool/packages/types/src/auth.ts NAVIS_PERMISSIONS; services/mcp-server authorization/authorize.ts"},
        {"capability": "Organization scope", "implemented": True, "shown": "S14 'OWN SCOPE': a key reads only its own organization", "source": "credentials.ts (organization from the key)"},
        {"capability": "Central policy enforcement", "implemented": False, "shown": "not shown", "status": "Not enabled yet", "source": "PoliciesPanel.tsx L219"},
        {"capability": "Projects", "implemented": False, "shown": "not shown (not a Console concept)", "source": "lib/navigation.ts"},
    ],
}

for name, obj in [("navislabs_entity_audit.json", entity_audit), ("navislabs_entity_consistency.json", consistency),
                  ("developer_capability_audit.json", cap), ("team_permission_audit.json", team)]:
    with open(os.path.join(ROOT, name), "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")
print(f"entities {len(entities)} · shared facts {len(shared)} · surfaces {len(cap['surfaces'])} · team items {len(team['items'])}")
