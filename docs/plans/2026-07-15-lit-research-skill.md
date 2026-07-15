# lit-research skill

Status: implemented — see `skills/lit-research/`.

## Summary

Add a single new skill, `lit-research`, to this repo.
It gives an agent reliable scientific-literature tooling: keyword search across scholarly APIs, citation-graph traversal (snowballing), bibliography verification (reference-check), and an orchestrated literature-review workflow that composes the first three.
API access is implemented as small Python CLIs under the skill's `scripts/` directory, run with `uv run` and inline script dependencies; the SKILL.md teaches when to use which script and how to compose them.

## Requirements

Gathered in the specing interview (2026-07-15):

- **Scope**: one skill folder, `skills/lit-research/`, covering the core lit family — search, citation graph, reference-check, lit-review orchestration.
- **Follow-ups, explicitly out of scope for this pass**: `paper-fetch` (DOI → open-access PDF + text extraction), `dataset-search` (Zenodo/Figshare/Dryad/HF), and writing/review skills (`paper-writing`, `peer-review`). Each gets its own future spec; this plan's design should leave room for them (see Approach).
- **Architecture**: Python scripts via `uv` (never plain `pip`), not prose-only curl instructions. Deterministic, low token cost, testable.
- **Sources**: OpenAlex (primary), Semantic Scholar, PubMed, Crossref. arXiv is not in scope.
- **Domain**: general/mixed research — OpenAlex-first, domain-neutral defaults; PubMed engaged only when the query is biomedical.
- **Success criteria**: an agent with this skill installed can (a) find relevant papers for a topic with real, resolvable identifiers; (b) expand from a seed paper through its citation graph; (c) verify a bibliography's entries against Crossref including retraction status; (d) run an end-to-end small literature review producing an annotated bibliography — all without hallucinating citations.

## Scope

- **Primary repo**: `skills` (this repo). No other repos affected.
- New files, all under `skills/lit-research/`:
  - `SKILL.md`
  - `scripts/lit_search.py`
  - `scripts/citation_graph.py`
  - `scripts/reference_check.py`
  - `scripts/common.py` (shared HTTP client, record normalization, output formatting)
- Repo docs touched: `docs/UBIQUITOUS-LANGUAGE.md` (created alongside this plan), `README.md` only if it enumerates skills (it currently doesn't — no change expected).

## Approach / design

### One skill, script-backed

The repo's plugin loader auto-discovers each folder under `skills/` as a skill, which makes sharing code across skill folders awkward.
So the whole lit family ships as one skill with one shared `scripts/` dir (decided in interview; the rejected alternative was four sibling skills with duplicated or hoisted scripts).
The lit-review workflow is prose in SKILL.md that composes the three scripts — it needs judgment (screening, synthesis), so it is not itself a script.

### Scripts, not prose API instructions

Each script is a self-contained Python CLI using [PEP 723 inline script metadata](https://peps.python.org/pep-0723/) so `uv run scripts/lit_search.py ...` works with no install step.
Dependencies stay minimal: `httpx` only (no heavy SDK wrappers).
Scripts print compact, agent-friendly output (one paper per block: title, authors, year, venue, DOI, OpenAlex/S2 ids, citation count, OA URL, abstract snippet) and support `--json` for machine consumption.

### Source strategy (general/mixed domain)

- **OpenAlex** is the default backend everywhere: broadest coverage, no key, exposes citations, OA locations, and retraction flags. Always send the polite-pool `mailto` param (read from `OPENALEX_MAILTO` env var, fall back to a documented placeholder that the SKILL.md tells the agent to ask the user for).
- **Semantic Scholar** is the relevance-search and TLDR backend: `lit_search.py --source s2` and citation contexts in `citation_graph.py`. Uses `S2_API_KEY` env var when present; degrades gracefully to unauthenticated rate limits when absent.
- **PubMed** (E-utilities) is opt-in via `lit_search.py --source pubmed` for biomedical queries; SKILL.md tells the agent when to reach for it.
- **Crossref** backs `reference_check.py`: DOI resolution, metadata match, and retraction status (Crossref now carries Retraction Watch data). Also sends a polite `mailto`.
- All sources normalize into one canonical record shape keyed by DOI (falling back to source-native id when no DOI exists), so dedup across sources is trivial.

### Room for follow-ups

The canonical record includes the best OA URL from OpenAlex/Unpaywall data, which is the seam the future `paper-fetch` skill will build on.
`common.py`'s client/normalization layer is written so a future skill can vendor or import it; no premature extraction into a shared package.

## Steps

1. **Scaffold the skill folder.** Create `skills/lit-research/` with a stub `SKILL.md` (frontmatter `name: lit-research` plus a trigger-rich `description:` matching the style of the existing skills' frontmatter) and empty `scripts/` dir.
2. **`scripts/common.py`.** Shared `httpx` client with retry/backoff and polite headers; the canonical paper-record dataclass and normalizers for OpenAlex, Semantic Scholar, PubMed, and Crossref payloads; text and `--json` renderers; env-var handling for `OPENALEX_MAILTO` and `S2_API_KEY`.
3. **`scripts/lit_search.py`.** CLI: `uv run lit_search.py "<query>" [--source openalex|s2|pubmed] [--limit N] [--year-from/--year-to] [--json]`. OpenAlex default; dedupes by DOI when multiple sources are combined via repeated `--source`.
4. **`scripts/citation_graph.py`.** CLI: `uv run citation_graph.py <doi-or-id> [--direction refs|cites|both] [--depth 1|2] [--limit N] [--json]`. Walks references and citing papers via OpenAlex (S2 fallback for citation contexts/TLDRs); ranks output by citation count and recency; flags likely-seminal works (highly cited references shared across the seed's neighborhood).
5. **`scripts/reference_check.py`.** CLI: `uv run reference_check.py <file.bib|file.md|-> [--json]`. Parses DOIs (and best-effort title/author/year for entries lacking one), resolves each against Crossref, reports per entry: resolved/mismatched/not-found and retraction status. Exit code non-zero when any entry fails, so it composes into checks.
6. **Write `SKILL.md`.** Procedure doc covering: when to trigger; the three scripts with usage examples; the snowballing recipe (search → pick seeds → citation-graph both directions → dedupe → iterate until saturation); the lit-review workflow (define inclusion criteria with the user → search + snowball → screen against criteria → produce annotated bibliography or synthesis matrix); the hard rule that every citation the agent emits must come from script output, never from model memory; env-var setup notes. Use the glossary's terms verbatim.
7. **Verify** (see below), then **doc-audit** pass over SKILL.md and this plan's assumptions.

## Testing & verification

The repo has no test harness; verification is E2E by hand, matching how a user hits it:

- Run each script directly against the live APIs: a known query (e.g. "attention is all you need transformer") must surface the expected paper with a correct DOI; `citation_graph.py` on that DOI must return real references/citers; `reference_check.py` against a small .bib containing one good DOI, one typo'd title, and one known-retracted paper must classify all three correctly.
- Install the skill into a scratch skills dir via `npx skills@latest add` (or symlink) and drive a fresh agent session through the lit-review workflow end-to-end on a small topic, confirming every emitted citation traces to script output.
- Scripts must run clean via `uv run` on a machine with no prior venv.

## Risks & open questions

- **API drift and rate limits**: unauthenticated Semantic Scholar is aggressively rate-limited; the skill must degrade to OpenAlex rather than hammer retries. Mitigated by backoff in `common.py` and SKILL.md guidance.
- **Reference parsing** from free-form markdown bibliographies is inherently fuzzy; v1 should be strict (DOI-first, conservative title matching) and report "unverifiable" rather than guess.
- **Depth-2 citation walks** can explode (thousands of works); `--limit` defaults must be conservative and documented.
- Open: whether `OPENALEX_MAILTO` should default to the user's email at install time or always prompt — decide during implementation.

## Follow-ups (each needs its own spec)

- `paper-fetch`: DOI → OA PDF (Unpaywall/OpenAlex locations) → text extraction for summarization.
- `dataset-search`: Zenodo, Figshare, Dryad, Hugging Face datasets.
- `paper-writing`: LaTeX/Quarto scaffolding, journal requirements, reporting checklists.
- `peer-review`: structured manuscript review, composing `lit-research` for missing-citation checks.
