# Ubiquitous language

Shared vocabulary between specs, conversation, and code in this repo.
One entry per term, short and precise.

## Repo-wide

- **skill**: a plain-markdown procedure doc (`SKILL.md` with YAML frontmatter) in a folder under `skills/`, auto-discovered by the plugin loader. It may carry supporting scripts in a `scripts/` subfolder.

## review (skills/engineering/review)

- **deep module**: a module whose interface is narrow relative to the functionality it hides. It is the target shape for anything with callers. A **shallow module** has an interface about as complex as what it does, and a pass-through wrapper is the extreme case.
- **seam**: the point where a public boundary is crossed and behavior can be substituted without editing the code on the other side. A test attaches there.
- **necessary leak**: an implementation fact a caller needs to know, such as a rate limit. An **accidental leak** is a fact that escaped because nothing hid it.
- **error-condition elimination**: designing away the precondition that produces an error case instead of handling or propagating it.

## merge-conflict (skills/engineering/merge-conflict)

- **merge conflict**: overlapping changes that Git cannot combine automatically during a merge, rebase, or cherry-pick.
- **merge base**: the common ancestor Git uses to compare diverging histories and identify each side's changes.
- **semantic resolution**: choosing the resulting behavior from each change's intent and the integration contract, not from conflict-marker position.

## prototype (skills/engineering/prototype)

- **throwaway spike**: a disposable implementation that answers one design question. Its source is discarded and never merged into production.

## spec (skills/engineering/spec, skills/engineering/spec-to-tickets)

- **work item**: one entry in a spec's "Work items" list, naming what it changes and the outcome that shows it is done, sized so one PR lands it. `spec-to-tickets` files each work item as at most one issue.

## lit-research (skills/general/lit-research)

- **canonical record**: the normalized paper representation all sources map into, keyed by DOI (source-native id when no DOI exists). The record dataclass in `scripts/common.py` implements it.
- **snowballing**: expanding a paper set by walking a seed paper's citation graph, backward through its references and forward through papers citing it, until new results stop appearing (saturation).
- **reference-check**: verifying a bibliography entry against Crossref: the DOI resolves, the metadata matches, and the work is not retracted. An entry that cannot be confidently matched is reported as *unverifiable* and never corrected by guess.
- **screening**: judging each candidate paper against the review's inclusion criteria. The agent does this step, not a script.
- **annotated bibliography**: the lit-review deliverable, the screened paper set with a short relevance note per paper, every entry sourced from script output.
