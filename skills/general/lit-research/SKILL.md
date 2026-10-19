---
name: lit-research
description: Use for scientific-literature searches, citation-graph expansion, bibliography verification, and literature reviews. Grounds every citation in script output from OpenAlex, Semantic Scholar, PubMed, or Crossref.
---

# lit-research

Tooling for scientific-literature work: search, citation-graph traversal (snowballing), reference checking, and an orchestrated literature-review workflow.

Every citation you emit must come from script output, never from model memory.
If you remember a relevant paper, confirm it exists with `lit_search.py` before citing it. If the scripts cannot surface it, say so instead of citing it.

## Setup

Scripts are in `scripts/` next to this file and run with `uv run` (inline dependencies, no install step).
Run them from the `scripts/` directory so the `common.py` import resolves.
The only prerequisite is [uv](https://docs.astral.sh/uv/). If it is missing, install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Environment variables, both optional but recommended:

- `OPENALEX_MAILTO`: an email for OpenAlex's and Crossref's polite pools, which have better rate limits. If unset, ask the user for one once and export it for the session.
- `S2_API_KEY`: a free Semantic Scholar key. Without it S2 is heavily rate-limited and the scripts fall back to OpenAlex.

## The scripts

### lit_search.py: find papers

```bash
uv run lit_search.py "sparse autoencoders interpretability" --limit 10
uv run lit_search.py "gut microbiome depression" --source pubmed --source openalex --year-from 2020
uv run lit_search.py "..." --source s2 --json
```

- The default source is OpenAlex, which has the broadest coverage across general and mixed domains.
- Use `--source s2` when relevance ranking or TLDRs matter, and `--source pubmed` for biomedical queries where MeSH-indexed search helps.
- Repeated `--source` flags combine sources and dedupe into canonical records by DOI.

### citation_graph.py: snowball from a seed

```bash
uv run citation_graph.py 10.18653/v1/2021.emnlp-main.132 --direction both --limit 25
uv run citation_graph.py W3199258042 --direction cites --depth 2 --json
```

- `refs` walks backward (what the seed builds on), `cites` walks forward (what builds on the seed), and `both` is the default.
- Output is ranked by citation count. Works referenced by two or more distinct works in the traversal are flagged `[seminal?]`.
- Depth 2 fans out quickly. Keep `--limit` low (default 25), and prefer a second depth-1 run from a chosen paper to a blind depth-2 crawl.

### reference_check.py: verify a bibliography

```bash
uv run reference_check.py refs.bib
uv run reference_check.py manuscript.md
echo "10.1038/s41586-020-2649-2" | uv run reference_check.py -
```

- Checks each entry against Crossref: the DOI resolves, the metadata matches, and the work is not retracted.
- Statuses: `ok`, `mismatched`, `not-found`, `retracted`, `unverifiable`. Unverifiable means the entry could not be confidently matched. Report it and do not guess a correction.
- Exits non-zero when any entry fails, so it works in pre-submission checks.

## Snowballing recipe

1. Search the topic with `lit_search.py` and pick 1-3 strong seed papers with the user, or by relevance and citation count.
2. Run `citation_graph.py --direction both` on each seed.
3. Dedupe across runs (records share DOI keys) and note `[seminal?]` flags.
4. Promote newly found high-relevance papers to seeds and repeat.
5. Stop at saturation, when a round surfaces no new relevant papers.

## Literature-review workflow

1. Define inclusion criteria with the user before searching: topic boundaries, date range, study types, and what is out of scope.
2. Search and snowball per the recipe, using `--json` output to track a large candidate set.
3. Screen each candidate against the inclusion criteria. This is your judgment, not a script's. Record why borderline papers were included or excluded.
4. Run the final citation list through `reference_check.py`.
5. Deliver an annotated bibliography, or a synthesis matrix (themes by papers) if the user wants one. For each paper, give the full citation with DOI and a short relevance note based on the record's abstract or TLDR.

The repo glossary, `docs/UBIQUITOUS-LANGUAGE.md`, defines the terms used here (canonical record, snowballing, reference-check, screening, annotated bibliography).
