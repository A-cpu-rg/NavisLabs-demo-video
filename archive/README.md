# Archive — superseded film data (read by nothing)

History only. Nothing in `src/`, `scripts/` or `package.json` reads these files; the film's
sources of truth are `src/data/navislabs_v6_copy.json` (every word) and
`src/data/navislabs_v6_launch_state.json` (every entity and the film's launch-state
integrations), built into the `navislabs_v6_*.json` files in the project root by
`npm run data:build`.

- `v5/` — the V5 narrative update: its built data and audits (`navislabs_v5_*`), its copy and
  demo data (`src-data/`), captions and the V5 versions of the build / audit / validator
  scripts (`scripts/`). Replaced by V6 (the founder's final voice as the master clock, 125 s).

- `v4/` — the V4 picture-lock data, its audits, the V4 audio production pack and the V4
  44-section audit generator (`scripts/build-final-audit.py`). Replaced by the V5 narrative
  update (same picture timings, new script and copy).
- `v3-and-earlier/` — V3 and earlier specs, maps and research notes.

These files contain the old narrative wording ("Navis Application", "One organization.",
"Your company keeps its history.", …) on purpose: they are the record of what changed. See
`navislabs_v5_narrative_product_audit.md` § 17 for the stale-copy search.

Not archived: `navis_master_cinematic_launch_spec.json`, `navis_launch_production_blueprint.json`
and `navis_code_audit.json` — protected source material that the code still reads for design
tokens and legacy schema checks (no narrative copy from them reaches the screen).
