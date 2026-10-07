# Ubiquitous language

Shared vocabulary between specs, conversation, and code in this repo.
One entry per term, short and precise.

## Repo-wide

- **skill**: a plain-markdown procedure doc (`SKILL.md` with YAML frontmatter) in a folder under `skills/`, auto-discovered by the plugin loader. It may carry supporting scripts in a `scripts/` subfolder.

## design (skills/engineering/design)

- **deep module**: a module whose interface is narrow relative to the functionality it hides. It is the target shape for anything with callers. A **shallow module** has an interface about as complex as what it does, and a pass-through wrapper is the extreme case.
- **seam**: the point where a public boundary is crossed and behavior can be substituted without editing the code on the other side. A test attaches there.
- **necessary leak**: an implementation fact a caller needs to know, such as a rate limit. An **accidental leak** is a fact that escaped because nothing hid it.
- **error-condition elimination**: designing away the precondition that produces an error case instead of handling or propagating it.
- **architecture review**: a scan of a codebase that produces ranked, evidence-backed structural opportunities without changing the code.
- **deepening opportunity**: a proposed structural change that makes a shallow module deeper by narrowing its interface or hiding more implementation behind it.

## dep-upgrade (skills/engineering/dep-upgrade)

- **downstream project**: the project that declares or consumes the dependency being upgraded. Its suite verifies compatibility.
- **lockstep tag bump**: updating every intended git-sourced package from one internal repository to the same release tag before resolving.
- **lockfile discipline**: changing dependency declarations with uv and reviewing the resulting `uv.lock`, never editing the lockfile by hand.

## flake-hunt (skills/engineering/flake-hunt)

- **flake**: a test that produces different outcomes under equivalent inputs and environment.
- **quarantine**: a temporary state where a test runs outside the blocking result while its failures stay visible and tracked.

## tech-research (skills/engineering/tech-research)

- **primary source**: the source that directly answers a claim, ranked by the source hierarchy: the installed dependency's own source and tests, then official vendor docs for the pinned version, then specs and RFCs, then release notes and issue trackers. Blog posts and model recall are never primary sources.
- **confidence level**: the high, moderate, low, or unknown rating on every claim in a findings file, recording how directly a primary source backs it.

## perf (skills/engineering/perf)

- **baseline**: the first measurement taken on a harness before any change. Every later re-measurement is compared against it. A one-off shell timing that cannot be re-run unchanged does not qualify.
- **harness**: the reproducible, committed way of driving a workload under measurement or test, cheap enough to re-run on demand. `perf` builds one to benchmark a workload and `tdd` builds one to drive a seam under test.

## merge-conflict (skills/engineering/merge-conflict)

- **merge conflict**: overlapping changes that Git cannot combine automatically during a merge, rebase, or cherry-pick.
- **merge base**: the common ancestor Git uses to compare diverging histories and identify each side's changes.
- **semantic resolution**: choosing the resulting behavior from each change's intent and the integration contract, not from conflict-marker position.

## prototype (skills/engineering/prototype)

- **throwaway spike**: a disposable implementation that answers one design question. Its source is discarded and never merged into production.

## triage (skills/engineering/triage)

- **inbound item**: a GitHub issue or pull request being classified before work starts.
- **agent-ready brief**: a structured handoff with the objective, evidence, scope, acceptance criteria, verification, constraints, and references an agent needs to act.
- **disposition**: whether an inbound item is ready, needs information, duplicates existing work, is out of scope, is deferred, or is already resolved.
- **work type**: the action an agent takes for an inbound item: implement, review, investigate, answer, or close.

## spec (skills/engineering/spec, skills/engineering/spec-to-tickets)

- **work item**: one entry in a spec's "Work items" list, naming what it changes and the outcome that shows it is done, sized so one PR lands it. `spec-to-tickets` files each work item as at most one issue.

## lit-research (skills/research/lit-research)

- **canonical record**: the normalized paper representation all sources map into, keyed by DOI (source-native id when no DOI exists). The record dataclass in `scripts/common.py` implements it.
- **snowballing**: expanding a paper set by walking a seed paper's citation graph, backward through its references and forward through papers citing it, until new results stop appearing (saturation).
- **reference-check**: verifying a bibliography entry against Crossref: the DOI resolves, the metadata matches, and the work is not retracted. An entry that cannot be confidently matched is reported as *unverifiable* and never corrected by guess.
- **screening**: judging each candidate paper against the review's inclusion criteria. The agent does this step, not a script.
- **annotated bibliography**: the lit-review deliverable, the screened paper set with a short relevance note per paper, every entry sourced from script output.
