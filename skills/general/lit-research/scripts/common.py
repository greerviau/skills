"""Shared HTTP client, canonical record, and renderers for the lit-research scripts.

Not a CLI. The scripts import this module; run them via `uv run` from this directory
so the sibling import resolves.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field

import httpx

OPENALEX_API = "https://api.openalex.org"
S2_API = "https://api.semanticscholar.org/graph/v1"
PUBMED_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CROSSREF_API = "https://api.crossref.org"

USER_AGENT = "lit-research-skill/1.0 (https://github.com/greerviau/skills)"


def polite_mailto() -> str | None:
    return os.environ.get("OPENALEX_MAILTO") or None


def s2_api_key() -> str | None:
    return os.environ.get("S2_API_KEY") or None


def get_json(url: str, params: dict | None = None, headers: dict | None = None, retries: int = 4) -> dict:
    """GET a JSON endpoint with backoff on 429/5xx. Exits with a message on hard failure."""
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    delay = 2.0
    last = ""
    for attempt in range(retries):
        try:
            resp = httpx.get(url, params=params, headers=hdrs, timeout=30, follow_redirects=True)
        except httpx.HTTPError as e:
            last = str(e)
            time.sleep(delay)
            delay *= 2
            continue
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            raise LookupError(f"not found: {url}")
        if resp.status_code == 429 or resp.status_code >= 500:
            last = f"HTTP {resp.status_code}"
            time.sleep(delay)
            delay *= 2
            continue
        raise RuntimeError(f"HTTP {resp.status_code} from {url}: {resp.text[:200]}")
    raise RuntimeError(f"giving up on {url} after {retries} attempts ({last})")


@dataclass
class Record:
    """Canonical record: the normalized paper representation all sources map into.

    Keyed by DOI; `key` falls back to a source-native id when no DOI exists.
    """

    title: str
    doi: str | None = None
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    openalex_id: str | None = None
    s2_id: str | None = None
    pmid: str | None = None
    citation_count: int | None = None
    oa_url: str | None = None
    abstract: str | None = None
    tldr: str | None = None
    retracted: bool = False
    source: str = ""

    @property
    def key(self) -> str:
        return (self.doi or self.openalex_id or self.s2_id or self.pmid or self.title).lower()


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:", "DOI:"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi.lower() or None


def _openalex_abstract(inv: dict | None) -> str | None:
    if not inv:
        return None
    positions: dict[int, str] = {}
    for word, idxs in inv.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def from_openalex(work: dict) -> Record:
    loc = work.get("best_oa_location") or {}
    return Record(
        title=work.get("display_name") or "(untitled)",
        doi=normalize_doi(work.get("doi")),
        authors=[a.get("author", {}).get("display_name", "?") for a in work.get("authorships", [])],
        year=work.get("publication_year"),
        venue=(work.get("primary_location") or {}).get("source", {}).get("display_name")
        if (work.get("primary_location") or {}).get("source")
        else None,
        openalex_id=(work.get("id") or "").rsplit("/", 1)[-1] or None,
        pmid=(work.get("ids", {}).get("pmid") or "").rsplit("/", 1)[-1] or None,
        citation_count=work.get("cited_by_count"),
        oa_url=loc.get("pdf_url") or loc.get("landing_page_url"),
        abstract=_openalex_abstract(work.get("abstract_inverted_index")),
        retracted=bool(work.get("is_retracted")),
        source="openalex",
    )


def from_s2(paper: dict) -> Record:
    ext = paper.get("externalIds") or {}
    return Record(
        title=paper.get("title") or "(untitled)",
        doi=normalize_doi(ext.get("DOI")),
        authors=[a.get("name", "?") for a in paper.get("authors") or []],
        year=paper.get("year"),
        venue=paper.get("venue") or None,
        s2_id=paper.get("paperId"),
        pmid=ext.get("PubMed"),
        citation_count=paper.get("citationCount"),
        oa_url=(paper.get("openAccessPdf") or {}).get("url"),
        abstract=paper.get("abstract"),
        tldr=(paper.get("tldr") or {}).get("text"),
        source="s2",
    )


def from_pubmed_summary(doc: dict) -> Record:
    doi = None
    for aid in doc.get("articleids", []):
        if aid.get("idtype") == "doi":
            doi = aid.get("value")
    return Record(
        title=doc.get("title") or "(untitled)",
        doi=normalize_doi(doi),
        authors=[a.get("name", "?") for a in doc.get("authors", [])],
        year=int(doc["pubdate"][:4]) if doc.get("pubdate", "")[:4].isdigit() else None,
        venue=doc.get("fulljournalname") or doc.get("source"),
        pmid=str(doc.get("uid", "")) or None,
        source="pubmed",
    )


def from_crossref(msg: dict) -> Record:
    # A retracted work carries the retraction notice in `updated-by`
    # (sourced from Retraction Watch); `update-to` appears on the notice itself.
    updates = (msg.get("updated-by") or []) + (msg.get("update-to") or [])
    retracted = any((u.get("type") or "").lower().startswith("retract") for u in updates)
    year = None
    parts = (msg.get("issued") or {}).get("date-parts") or [[None]]
    if parts and parts[0] and parts[0][0]:
        year = parts[0][0]
    return Record(
        title=(msg.get("title") or ["(untitled)"])[0],
        doi=normalize_doi(msg.get("DOI")),
        authors=[f"{a.get('given', '')} {a.get('family', '')}".strip() for a in msg.get("author", [])],
        year=year,
        venue=(msg.get("container-title") or [None])[0],
        citation_count=msg.get("is-referenced-by-count"),
        retracted=retracted,
        source="crossref",
    )


def dedupe(records: list[Record]) -> list[Record]:
    seen: dict[str, Record] = {}
    for r in records:
        if r.key not in seen:
            seen[r.key] = r
    return list(seen.values())


def render(records: list[Record], as_json: bool) -> None:
    if as_json:
        print(json.dumps([asdict(r) for r in records], indent=2))
        return
    for r in records:
        authors = ", ".join(r.authors[:3]) + (" et al." if len(r.authors) > 3 else "")
        print(f"## {r.title}")
        line2 = " | ".join(
            s
            for s in [
                authors or None,
                str(r.year) if r.year else None,
                r.venue,
                f"cited by {r.citation_count}" if r.citation_count is not None else None,
            ]
            if s
        )
        if line2:
            print(line2)
        ids = " | ".join(
            s
            for s in [
                f"doi:{r.doi}" if r.doi else None,
                f"openalex:{r.openalex_id}" if r.openalex_id else None,
                f"s2:{r.s2_id}" if r.s2_id else None,
                f"pmid:{r.pmid}" if r.pmid else None,
            ]
            if s
        )
        if ids:
            print(ids)
        if r.oa_url:
            print(f"oa: {r.oa_url}")
        if r.retracted:
            print("** RETRACTED **")
        snippet = r.tldr or r.abstract
        if snippet:
            print(snippet[:400].replace("\n", " "))
        print()


def warn(msg: str) -> None:
    print(f"warning: {msg}", file=sys.stderr)
