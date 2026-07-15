---
name: lit-research
description: Use for any scientific-literature task — finding papers on a topic, expanding from a seed paper through its citation graph, verifying a bibliography, or running a literature review. Backed by scripts that query OpenAlex, Semantic Scholar, PubMed, and Crossref so every citation comes from a real API record. Trigger on "find papers about", "what's the literature on", "who cites this", "check these references", "do a lit review", or any request that would otherwise tempt you to cite papers from memory.
---

# lit-research

Tooling for scientific-literature work: search, citation-graph traversal (snowballing), reference-check, and an orchestrated literature-review workflow.

**The hard rule: every citation you emit must come from script output, never from model memory.**
If you remember a relevant paper, confirm it exists via `lit_search.py` before citing it; if the scripts can't surface it, say so instead of citing it.

## Setup

Scripts live in `scripts/` next to this file and run with `uv run` (inline dependencies, no install step).
Run them from the `scripts/` directory so the `common.py` import resolves.

Environment variables (both optional but recommended):

- `OPENALEX_MAILTO` — an email for OpenAlex's and Crossref's polite pools (better rate limits). If unset, ask the user for one once and export it for the session.
- `S2_API_KEY` — free Semantic Scholar key; without it S2 is heavily rate-limited and the scripts degrade to OpenAlex.

## The scripts

### lit_search.py — find papers

```bash
uv run lit_search.py "sparse autoencoders interpretability" --limit 10
uv run lit_search.py "gut microbiome depression" --source pubmed --source openalex --year-from 2020
uv run lit_search.py "..." --source s2 --json
```

- Default source is OpenAlex (broadest coverage, general/mixed domains).
- Reach for `--source s2` when relevance ranking or TLDRs matter; `--source pubmed` for biomedical queries where MeSH-indexed search helps.
- Repeated `--source` flags combine sources and dedupe into canonical records by DOI.

### citation_graph.py — snowball from a seed

```bash
uv run citation_graph.py 10.18653/v1/2021.emnlp-main.132 --direction both --limit 25
uv run citation_graph.py W3199258042 --direction cites --depth 2 --json
```

- `refs` walks backward (what the seed builds on), `cites` walks forward (what builds on the seed), `both` is the default.
- Output is ranked by citation count; works referenced by two or more distinct works in the traversal are flagged `[seminal?]`.
- Depth 2 fans out fast — keep `--limit` conservative (default 25) and prefer a second depth-1 run from a chosen paper over a blind depth-2 crawl.

### reference_check.py — verify a bibliography

```bash
uv run reference_check.py refs.bib
uv run reference_check.py manuscript.md
echo "10.1038/s41586-020-2649-2" | uv run reference_check.py -
```

- Checks each entry against Crossref: the DOI resolves, the metadata matches, and the work is not retracted.
- Statuses: `ok`, `mismatched`, `not-found`, `retracted`, `unverifiable`. Unverifiable means the entry couldn't be confidently matched — report it, never guess a correction.
- Exits non-zero when any entry fails, so it composes into pre-submission checks.

## Snowballing recipe

1. Search the topic with `lit_search.py`; pick 1-3 strong seed papers with the user (or by relevance + citation count).
2. Run `citation_graph.py --direction both` on each seed.
3. Dedupe across runs (records share DOI keys) and note `[seminal?]` flags.
4. Promote newly found high-relevance papers to seeds and repeat.
5. Stop at saturation — when a round surfaces no new relevant papers.

## Literature-review workflow

1. **Define inclusion criteria with the user** before searching: topic boundaries, date range, study types, what's explicitly out of scope.
2. **Search and snowball** per the recipe above, using `--json` output when you need to track a large candidate set.
3. **Screening**: judge each candidate against the inclusion criteria — your judgment, not a script. Record why borderline papers were included or excluded.
4. **Verify**: run the final citation list through `reference_check.py`.
5. **Deliver an annotated bibliography** (or a synthesis matrix if the user wants themes × papers): per paper, full citation with DOI plus a short relevance note grounded in the record's abstract/TLDR.

Terms in this doc (canonical record, snowballing, reference-check, screening, annotated bibliography) are defined in the repo glossary, `docs/UBIQUITOUS-LANGUAGE.md`.
