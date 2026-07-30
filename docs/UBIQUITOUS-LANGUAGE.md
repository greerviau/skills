# Ubiquitous language

Shared vocabulary between specs, conversation, and code in this repo.
One entry per term; keep entries short and precise.

## Repo-wide

- **skill**: a self-contained, plain-markdown procedure doc (`SKILL.md` with YAML frontmatter) in a folder under `skills/`, auto-discovered by the plugin loader. May carry supporting scripts in a `scripts/` subfolder.

## design (skills/engineering/design)

- **deep module**: a module whose interface is narrow relative to the functionality it hides behind it; the target shape for anything with callers. The opposite is a **shallow module**, whose interface is about as complex as what it does — a pass-through wrapper is the shallow extreme.
- **seam**: the point where a public boundary is crossed and behavior can be substituted without editing the code on the other side of it; also the point where a test attaches.
- **load-bearing leak**: a fact about implementation a caller genuinely needs to know (e.g. a rate limit), as distinct from an **accidental leak** — one that escaped only because nothing hid it.
- **error-condition elimination**: designing away the precondition that produces an error case, rather than handling or propagating it.

## tech-research (skills/engineering/tech-research)

- **primary source**: the source that directly answers a claim, ranked by the source hierarchy — the installed dependency's own source and tests, then official vendor docs for the pinned version, then specs/RFCs, then release notes and issue trackers. Blog posts and model recall are never primary sources.
- **confidence level**: the high/moderate/low/unknown rating attached to every claim in a findings file, recording how directly a primary source backs it rather than smoothing uncertainty into an unqualified statement.

## lit-research (skills/research/lit-research)

- **canonical record**: the normalized paper representation all sources map into, keyed by DOI (source-native id when no DOI exists). Embodied by the record dataclass in `scripts/common.py`.
- **snowballing**: expanding a paper set by walking a seed paper's citation graph — backward through its references and forward through papers citing it — iterating until new results stop appearing (saturation).
- **reference-check**: verifying a bibliography entry against Crossref: the DOI resolves, the metadata matches, and the work is not retracted. An entry that cannot be confidently matched is reported *unverifiable*, never guessed.
- **screening**: judging each candidate paper against the review's inclusion criteria; a lit-review step performed by the agent, not a script.
- **annotated bibliography**: the lit-review deliverable — the screened paper set with a short relevance note per paper, every entry sourced from script output.
