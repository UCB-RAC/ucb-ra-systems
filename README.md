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

`data/actors.yaml` — human endpoints for flows.

## The three views

**Ownership** — org forest, toggled between *run by* and *business owner* attachment. Orgs with no components are hidden; applications nest under their system (italic); platforms are gray pills; click an org circle to collapse its branch.

**Data flows** — force graph with category filters; dashed = unverified; icons mark manual/email flows; actor nodes show 👤.

**Central IT touchpoints** — three touchpoint types, all shown: gold = run by bIT, green = runs on a bIT platform (dotted "uses" edges), blue = exchanges data with a bIT-run component, plus a table.

## Verification status

Items with `verified: false` (currently 42) render dashed with "?" — they contain Claude's guesses. Notable: the bIT internal team structure (Infrastructure/Oracle/Unix), platform operators, and most org placements outside RAC. Fix in YAML, flip the flag, rebuild.

## If we outgrow YAML

Triggers: multiple editors, ad-hoc queries ("everything that touches Oracle"), or ~150+ components. Plan: migrate to SQLite (still one file, editable with DB Browser, build script barely changes); the alternative is adopting LikeC4/Structurizr DSL for standard C4 tooling at the cost of remodeling.

`docs/research-admin-diagrams.html` is regenerated on every build — never edit it by hand. It loads D3 and the Inter font from CDNs; everything else is self-contained.
