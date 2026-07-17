# Ubiquitous language

Shared vocabulary between specs, conversation, and code in this repo.
One entry per term; keep entries short and precise.

## Repo-wide

- **skill**: a self-contained, plain-markdown procedure doc (`SKILL.md` with YAML frontmatter) in a folder under `skills/`, auto-discovered by the plugin loader. May carry supporting scripts in a `scripts/` subfolder.

## lit-research (skills/research/lit-research)

- **canonical record**: the normalized paper representation all sources map into, keyed by DOI (source-native id when no DOI exists). Embodied by the record dataclass in `scripts/common.py`.
- **snowballing**: expanding a paper set by walking a seed paper's citation graph — backward through its references and forward through papers citing it — iterating until new results stop appearing (saturation).
- **reference-check**: verifying a bibliography entry against Crossref: the DOI resolves, the metadata matches, and the work is not retracted. An entry that cannot be confidently matched is reported *unverifiable*, never guessed.
- **screening**: judging each candidate paper against the review's inclusion criteria; a lit-review step performed by the agent, not a script.
- **annotated bibliography**: the lit-review deliverable — the screened paper set with a short relevance note per paper, every entry sourced from script output.
