# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Search scholarly literature. OpenAlex by default; Semantic Scholar and PubMed opt-in.

Usage:
  uv run lit_search.py "<query>" [--source openalex|s2|pubmed]... [--limit N]
                       [--year-from Y] [--year-to Y] [--json]

Repeat --source to combine sources; results are deduped into canonical records by DOI.
"""

from __future__ import annotations

import argparse
import sys

import common
from common import Record


def search_openalex(query: str, limit: int, year_from: int | None, year_to: int | None) -> list[Record]:
    params: dict = {"search": query, "per-page": min(limit, 200)}
    filters = []
    if year_from:
        filters.append(f"from_publication_date:{year_from}-01-01")
    if year_to:
        filters.append(f"to_publication_date:{year_to}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    if common.polite_mailto():
        params["mailto"] = common.polite_mailto()
    data = common.get_json(f"{common.OPENALEX_API}/works", params)
    return [common.from_openalex(w) for w in data.get("results", [])[:limit]]


def search_s2(query: str, limit: int, year_from: int | None, year_to: int | None) -> list[Record]:
    params: dict = {
        "query": query,
        "limit": min(limit, 100),
        "fields": "title,authors,year,venue,externalIds,citationCount,abstract,openAccessPdf,tldr",
    }
    if year_from or year_to:
        params["year"] = f"{year_from or ''}-{year_to or ''}"
    headers = {"x-api-key": common.s2_api_key()} if common.s2_api_key() else None
    try:
        data = common.get_json(f"{common.S2_API}/paper/search", params, headers)
    except RuntimeError as e:
        common.warn(f"Semantic Scholar unavailable ({e}); fall back to --source openalex")
        return []
    return [common.from_s2(p) for p in data.get("data") or []][:limit]


def search_pubmed(query: str, limit: int, year_from: int | None, year_to: int | None) -> list[Record]:
    term = query
    if year_from or year_to:
        term += f" AND {year_from or 1800}:{year_to or 3000}[dp]"
    ids = common.get_json(
        f"{common.PUBMED_API}/esearch.fcgi",
        {"db": "pubmed", "term": term, "retmax": limit, "retmode": "json"},
    )["esearchresult"].get("idlist", [])
    if not ids:
        return []
    summaries = common.get_json(
        f"{common.PUBMED_API}/esummary.fcgi",
        {"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
    )["result"]
    return [common.from_pubmed_summary(summaries[uid]) for uid in ids if uid in summaries]


SEARCHERS = {"openalex": search_openalex, "s2": search_s2, "pubmed": search_pubmed}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query")
    ap.add_argument("--source", action="append", choices=sorted(SEARCHERS), default=None)
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--year-from", type=int)
    ap.add_argument("--year-to", type=int)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    records: list[Record] = []
    for source in args.source or ["openalex"]:
        records.extend(SEARCHERS[source](args.query, args.limit, args.year_from, args.year_to))
    records = common.dedupe(records)
    if not records:
        print("no results", file=sys.stderr)
        sys.exit(1)
    common.render(records, args.json)


if __name__ == "__main__":
    main()
