# Research Administration Systems — EA Diagrams

Diagrams-as-data for UC Berkeley's research administration landscape. Edit four YAML files, run one script, get an interactive HTML page with three views: ownership aligned to the campus org tree, data flows, and touchpoints with central IT (bIT).

## Workflow

```
edit data/*.yaml  →  uv run python build.py  →  open docs/research-admin-diagrams.html
```

The script validates referential integrity (unknown ids, missing parents, cycles, bad kinds, self-referencing `uses`) and refuses to build on errors. Requires `pyyaml`.

## Concepts

The model uses a simplified ArchiMate-style taxonomy. A **service** is a business function people consume (the `category` field — "Compliance", "Proposal & Award"). A **component** is anything deployable, with three kinds: **platform** (shared tech others run on — VMware, Oracle DB, SharePoint), **system** (independently operated software — Phoebe, BFS, eProtocol), and **application** (a user-facing capability inside a system — PI Portfolio in Cal Answers, the IRB module in eProtocol). An **actor** is a human population (PIs, RAs) that can send or receive data.

Relationships: `part_of` nests an application in its system; `uses` declares a dependency on a platform or another system (Phoebe uses VMware and Oracle); flows in `flows.yaml` move data between components and/or actors.

Each component carries three distinct technical roles plus a business one: `provided_by` (vendor or in-house developer — Key Solutions), `run_by` (administrator orgs — bIT Oracle/Unix teams; this drives the central-IT view), `technical_owner` (the responsible person — Ken Geis), and `business_owner` (whose service it is — OPHS). Applications inherit `run_by`, `business_owner`, `uses`, and `provided_by` from their system when unset.

## Files

`data/orgs.yaml` — the org forest. Multiple roots allowed (UC Berkeley, UCOP, External Vendors). `central_it: true` marks the bIT subtree.

`data/components.yaml` — platforms, systems, applications. Field reference in the file header.

`data/flows.yaml` — data flows: `from`, `to`, `label`, optional `mode: manual` (👤 icon), `via: email` (✉ icon), endpoints may be actors.

`data/actors.yaml` — human actors (PIs, RAs, SPO officers...). Endpoints for flows and the "user" leg of lifecycle participations; file order = lane order in the lifecycle view.

`data/lifecycle.yaml` — the sponsored research lifecycle: ordered `phases` (from the [VCR grant life cycle](https://vcresearch.berkeley.edu/grant-life-cycle/overview)) and `participations`, the three-way relationship (component, actor, phase) with an `activity` label. A system→phase mapping alone would mislead — the same system serves different users differently per phase (Phoebe is an SPO submission tool pre-award and a CGA data source at setup), so the ternary relation is the unit of record.

## The three views

**Ownership** — org forest, toggled between *run by* and *business owner* attachment. Orgs with no components are hidden; applications nest under their system (italic); platforms are gray pills; click an org circle to collapse its branch.

**Lifecycle** — swimlane timeline: actor lanes × lifecycle phases. A bar spanning phases means that user community works in that system through those phases; hover shows the per-phase activity, click opens system details. Phase bands (Pre-Award / Award Set-Up / Post-Award) follow the VCR page. An empty column (Define Project) is honest: no admin system participates there yet.

**Data flows** — force graph with category filters; dashed = unverified; icons mark manual/email flows; actor nodes show 👤.

**Central IT touchpoints** — three touchpoint types, all shown: gold = run by bIT, green = runs on a bIT platform (dotted "uses" edges), blue = exchanges data with a bIT-run component, plus a table.

## Verification status

Items with `verified: false` (currently 42) render dashed with "?" — they contain Claude's guesses. Notable: the bIT internal team structure (Infrastructure/Oracle/Unix), platform operators, and most org placements outside RAC. Fix in YAML, flip the flag, rebuild.

## If we outgrow YAML

Triggers: multiple editors, ad-hoc queries ("everything that touches Oracle"), or ~150+ components. Candidates, in rough order of fit:

1. **LadybugDB** (KuzuDB successor, Ken's suggestion) — an embedded graph database whose Cypher `CREATE`/`MERGE` statements are themselves text-editable files, so the "edit text, regenerate" workflow survives intact, and relationship-heavy questions (uses chains, ternary participations) become one-line Cypher queries instead of bespoke JS.
2. **SQLite** — one file, DB Browser editing, mechanical migration; queries via SQL but graph traversals get clumsy.
3. **LikeC4 / Structurizr DSL** — standard C4 tooling for free, at the cost of remodeling and losing the ternary lifecycle relation, which C4 doesn't natively express.

The data is already shaped like a property graph (nodes: orgs/components/actors/phases; edges: parent, part_of, uses, run_by, flows, participations), so the LadybugDB migration would be mostly mechanical.

`docs/research-admin-diagrams.html` is regenerated on every build — never edit it by hand. It loads D3 and the Inter font from CDNs; everything else is self-contained.
