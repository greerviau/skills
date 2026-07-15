# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///
"""Reference-check a bibliography against Crossref: DOIs resolve, metadata matches,
nothing is retracted. Entries that cannot be confidently matched are reported
unverifiable, never guessed.

Usage:
  uv run reference_check.py <file.bib|file.md|-> [--json]

.bib files are parsed entry-by-entry (doi, title, author, year fields).
Any other input is scanned line-by-line for DOIs. `-` reads stdin.
Exit code is non-zero when any entry is mismatched, not found, retracted,
or unverifiable.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

import common

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>{},;]+", re.IGNORECASE)
BIB_ENTRY_RE = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", re.DOTALL)
BIB_FIELD_RE = re.compile(r"(\w+)\s*=\s*[{\"](.*?)[}\"]\s*,?\s*\n", re.DOTALL)


def parse_entries(text: str, is_bib: bool) -> list[dict]:
    entries = []
    if is_bib:
        for m in BIB_ENTRY_RE.finditer(text):
            fields = {k.lower(): re.sub(r"\s+", " ", v).strip("{} ") for k, v in BIB_FIELD_RE.findall(m.group(3) + "\n")}
            doi_m = DOI_RE.search(fields.get("doi", ""))
            entries.append(
                {
                    "label": m.group(2),
                    "doi": common.normalize_doi(doi_m.group(0) if doi_m else None),
                    "title": fields.get("title"),
                    "year": fields.get("year"),
                }
            )
    else:
        for line in text.splitlines():
            m = DOI_RE.search(line)
            if m:
                entries.append({"label": line.strip()[:80], "doi": common.normalize_doi(m.group(0).rstrip(".")), "title": None, "year": None})
    return entries


def title_similarity(a: str, b: str) -> float:
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower())
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def check_entry(entry: dict) -> dict:
    result = {**entry, "status": "unverifiable", "detail": "", "retracted": False}
    params = {"mailto": common.polite_mailto()} if common.polite_mailto() else None
    if entry["doi"]:
        try:
            msg = common.get_json(f"{common.CROSSREF_API}/works/{entry['doi']}", params)["message"]
        except LookupError:
            result.update(status="not-found", detail="DOI does not resolve at Crossref")
            return result
        rec = common.from_crossref(msg)
        result["retracted"] = rec.retracted
        if entry["title"]:
            sim = title_similarity(entry["title"], rec.title)
            if sim < 0.8:
                result.update(status="mismatched", detail=f"title similarity {sim:.2f}: Crossref has {rec.title!r}")
                return result
        result.update(status="retracted" if rec.retracted else "ok", detail=rec.title)
        return result
    if entry["title"]:
        data = common.get_json(f"{common.CROSSREF_API}/works", {**(params or {}), "query.bibliographic": entry["title"], "rows": 1})
        items = data["message"].get("items", [])
        if items:
            rec = common.from_crossref(items[0])
            sim = title_similarity(entry["title"], rec.title)
            if sim >= 0.9:
                result["retracted"] = rec.retracted
                result.update(status="retracted" if rec.retracted else "ok", detail=f"matched doi:{rec.doi}")
                return result
            result["detail"] = f"best Crossref match only {sim:.2f} similar ({rec.title!r})"
            return result
    result["detail"] = result["detail"] or "no DOI and no confident title match"
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help=".bib or text/markdown file, or - for stdin")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text()
    entries = parse_entries(text, is_bib=args.path.endswith(".bib"))
    if not entries:
        print("no bibliography entries found", file=sys.stderr)
        sys.exit(1)

    results = [check_entry(e) for e in entries]
    failed = [r for r in results if r["status"] != "ok"]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"[{r['status'].upper():>12}] {r['label']}  {r['detail']}")
        print(f"\n{len(results) - len(failed)}/{len(results)} verified")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
