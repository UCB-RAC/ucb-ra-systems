#!/usr/bin/env python3
"""Validate data/*.yaml and render docs/research-admin-diagrams.html.

Usage:  python3 build.py   (or: uv run python build.py)
Requires: pyyaml
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
DATA = ROOT / "data"
OUT = ROOT / "docs" / "research-admin-diagrams.html"
TEMPLATE = ROOT / "templates" / "viewer.html"

KINDS = {"platform", "system", "application"}


def load(name):
    with open(DATA / name) as f:
        return yaml.safe_load(f) or []


def fail(errors):
    print("VALIDATION FAILED:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(1)


def validate(orgs, comps, flows, actors):
    errors = []
    org_ids = [o["id"] for o in orgs]
    comp_ids = [c["id"] for c in comps]
    actor_ids = [a["id"] for a in actors]
    endpoint_ids = comp_ids + actor_ids

    for label, ids in (("org", org_ids), ("component", comp_ids), ("actor", actor_ids)):
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            errors.append(f"duplicate {label} ids: {sorted(dupes)}")
    overlap = set(comp_ids) & set(actor_ids)
    if overlap:
        errors.append(f"ids used as both component and actor: {sorted(overlap)}")

    org_set, comp_set = set(org_ids), set(comp_ids)
    by_id = {o["id"]: o for o in orgs}
    by_comp = {c["id"]: c for c in comps}

    roots = sum(1 for o in orgs if o.get("parent") is None)
    if roots < 1:
        errors.append("no root orgs (parent: null) found")
    for o in orgs:
        p = o.get("parent")
        if p is not None and p not in org_set:
            errors.append(f"org '{o['id']}' has unknown parent '{p}'")
        seen, cur = set(), o["id"]
        while cur is not None:
            if cur in seen:
                errors.append(f"org parent cycle involving '{o['id']}'")
                break
            seen.add(cur)
            cur = by_id.get(cur, {}).get("parent")

    for c in comps:
        kind = c.get("kind")
        if kind not in KINDS:
            errors.append(f"component '{c['id']}' kind '{kind}' not in {sorted(KINDS)}")
        po = c.get("part_of")
        if po is not None:
            if po not in comp_set:
                errors.append(f"component '{c['id']}' part_of '{po}' not found")
            elif kind != "application":
                errors.append(f"component '{c['id']}' has part_of but kind is '{kind}' (only applications nest)")
            elif by_comp[po].get("kind") == "application":
                errors.append(f"component '{c['id']}' part_of '{po}' is itself an application")
        for u in c.get("uses") or []:
            if u not in comp_set:
                errors.append(f"component '{c['id']}' uses unknown component '{u}'")
            elif u == c["id"]:
                errors.append(f"component '{c['id']}' uses itself")
        if not c.get("run_by") and not c.get("part_of"):
            errors.append(f"component '{c['id']}' missing run_by (required unless part_of is set)")
        for field in ("run_by", "business_owner"):
            v = c.get(field) or []
            for ref in v if isinstance(v, list) else [v]:
                if ref not in org_set:
                    errors.append(f"component '{c['id']}' {field} '{ref}' not in orgs.yaml")
        if not c.get("business_owner") and not c.get("part_of") and kind != "platform":
            errors.append(f"component '{c['id']}' missing business_owner (required unless part_of is set or kind is platform)")

    for i, fl in enumerate(flows):
        for end in ("from", "to"):
            if fl.get(end) not in endpoint_ids:
                errors.append(f"flow #{i + 1} {end} '{fl.get(end)}' not in components.yaml or actors.yaml")
        if not fl.get("label"):
            errors.append(f"flow #{i + 1} ({fl.get('from')}->{fl.get('to')}) missing label")
        if fl.get("mode", "automated") not in ("automated", "manual"):
            errors.append(f"flow #{i + 1} mode must be automated|manual")

    if errors:
        fail(errors)


def main():
    orgs = load("orgs.yaml")
    comps = load("components.yaml")
    flows = load("flows.yaml")
    actors = load("actors.yaml")
    validate(orgs, comps, flows, actors)

    by_comp = {c["id"]: c for c in comps}
    for c in comps:
        # normalize lists, defaults; applications inherit from their system
        parent = by_comp.get(c.get("part_of") or "")
        for field in ("run_by", "business_owner", "uses"):
            v = c.get(field)
            if v is None and parent is not None:
                v = parent.get(field)
                c[field + "_inherited"] = v is not None
            c[field] = (v if isinstance(v, list) else [v]) if v else []
        if not c.get("provided_by") and parent is not None:
            c["provided_by"] = parent.get("provided_by")
        c.setdefault("verified", True)
        c.setdefault("status", "active")
    for o in orgs:
        o.setdefault("verified", True)
    for f in flows:
        f.setdefault("verified", False)
        f.setdefault("mode", "automated")

    data = {"orgs": orgs, "components": comps, "flows": flows, "actors": actors}
    html = TEMPLATE.read_text().replace(
        "/*__DATA__*/", "const DATA = " + json.dumps(data, indent=1) + ";"
    )
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)

    unverified = sum(1 for x in orgs + comps + flows if not x.get("verified", True))
    kinds = {k: sum(1 for c in comps if c["kind"] == k) for k in sorted(KINDS)}
    print(f"OK: {len(orgs)} orgs, {len(comps)} components ({kinds}), "
          f"{len(flows)} flows, {len(actors)} actors ({unverified} items unverified)")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
