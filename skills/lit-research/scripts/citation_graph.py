# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Walk a paper's citation graph via OpenAlex — the traversal step of snowballing.

Usage:
  uv run citation_graph.py <doi-or-openalex-id> [--direction refs|cites|both]
                           [--depth 1|2] [--limit N] [--json]

`refs` walks backward through the seed's references; `cites` walks forward through
papers citing it. --limit caps results per work per direction (default 25).
Works appearing as a reference of two or more distinct works in the traversal are
flagged [seminal?]. Output is ranked by citation count.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import asdict

import common
from common import Record


def resolve_seed(ident: str) -> dict:
    ident = ident.strip()
    doi = common.normalize_doi(ident) if not ident.upper().startswith("W") else None
    path = f"doi:{doi}" if doi and "/" in doi else ident.upper()
    params = {"mailto": common.polite_mailto()} if common.polite_mailto() else None
    return common.get_json(f"{common.OPENALEX_API}/works/{path}", params)


def fetch_batch(openalex_ids: list[str]) -> list[Record]:
    records: list[Record] = []
    for i in range(0, len(openalex_ids), 50):
        chunk = "|".join(w.rsplit("/", 1)[-1] for w in openalex_ids[i : i + 50])
        params: dict = {"filter": f"openalex:{chunk}", "per-page": 50}
        if common.polite_mailto():
            params["mailto"] = common.polite_mailto()
        data = common.get_json(f"{common.OPENALEX_API}/works", params)
        records.extend(common.from_openalex(w) for w in data.get("results", []))
    return records


def fetch_citers(openalex_id: str, limit: int) -> list[Record]:
    params: dict = {"filter": f"cites:{openalex_id}", "per-page": min(limit, 200), "sort": "cited_by_count:desc"}
    if common.polite_mailto():
        params["mailto"] = common.polite_mailto()
    data = common.get_json(f"{common.OPENALEX_API}/works", params)
    return [common.from_openalex(w) for w in data.get("results", [])[:limit]]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("seed", help="DOI or OpenAlex work id (W...)")
    ap.add_argument("--direction", choices=["refs", "cites", "both"], default="both")
    ap.add_argument("--depth", type=int, choices=[1, 2], default=1)
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        seed_work = resolve_seed(args.seed)
    except LookupError:
        print(f"seed not found: {args.seed}", file=sys.stderr)
        sys.exit(1)
    seed = common.from_openalex(seed_work)
    print(f"# seed: {seed.title} ({seed.year}) doi:{seed.doi} openalex:{seed.openalex_id}\n", file=sys.stderr)

    ref_counts: Counter[str] = Counter()
    collected: list[Record] = []
    frontier = [(seed_work, 1)]
    while frontier:
        work, level = frontier.pop(0)
        if args.direction in ("refs", "both"):
            ref_ids = (work.get("referenced_works") or [])[: args.limit]
            refs = fetch_batch(ref_ids)
            for r in refs:
                ref_counts[r.key] += 1
            collected.extend(refs)
            if level < args.depth:
                seminal = sorted(refs, key=lambda r: r.citation_count or 0, reverse=True)[:5]
                frontier.extend((resolve_seed(r.openalex_id), level + 1) for r in seminal if r.openalex_id)
        if args.direction in ("cites", "both") and work.get("id"):
            citers = fetch_citers(work["id"].rsplit("/", 1)[-1], args.limit)
            collected.extend(citers)
            if level < args.depth:
                frontier.extend(
                    (resolve_seed(c.openalex_id), level + 1)
                    for c in citers[:5]
                    if c.openalex_id
                )

    records = [r for r in common.dedupe(collected) if r.key != seed.key]
    records.sort(key=lambda r: r.citation_count or 0, reverse=True)
    if args.json:
        import json

        out = []
        for r in records:
            d = asdict(r)
            d["seminal"] = ref_counts[r.key] >= 2
            out.append(d)
        print(json.dumps(out, indent=2))
        return
    for r in records:
        if ref_counts[r.key] >= 2:
            print("[seminal?]", end=" ")
        common.render([r], as_json=False)


if __name__ == "__main__":
    main()
