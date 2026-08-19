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

## dep-upgrade (skills/engineering/dep-upgrade)

- **downstream project**: the project that declares or consumes the dependency being upgraded; its suite verifies compatibility.
- **lockstep tag bump**: updating every intended git-sourced package from one internal repository to the same release tag before resolving.
- **lockfile discipline**: changing dependency declarations with uv and reviewing the resulting `uv.lock`; never editing the lockfile by hand.

## flake-hunt (skills/engineering/flake-hunt)

- **flake**: a test that produces different outcomes under equivalent inputs and environment.
- **quarantine**: a temporary state where a test runs outside the blocking result while its failures remain visible and tracked.

## tech-research (skills/engineering/tech-research)

- **primary source**: the source that directly answers a claim, ranked by the source hierarchy — the installed dependency's own source and tests, then official vendor docs for the pinned version, then specs/RFCs, then release notes and issue trackers. Blog posts and model recall are never primary sources.
- **confidence level**: the high/moderate/low/unknown rating attached to every claim in a findings file, recording how directly a primary source backs it rather than smoothing uncertainty into an unqualified statement.

## perf (skills/engineering/perf)

- **baseline**: the first measurement taken on a harness, before any change; every later re-measurement is compared against it. A one-off shell timing that can't be re-run unchanged doesn't qualify.
- **harness**: the reproducible, committed way of driving a workload under measurement or test, cheap enough to re-run on demand. `perf` builds one to benchmark a workload; `tdd` builds one to drive a seam under test - same concept, a different guard.

## merge-conflict (skills/engineering/merge-conflict)

- **merge conflict**: overlapping changes that Git cannot combine automatically during a merge, rebase, or cherry-pick.
- **merge base**: the common ancestor Git uses to compare diverging histories and identify each side's changes.
- **semantic resolution**: choosing the resulting behavior from each change's intent and the integration contract, rather than from conflict-marker position.

## wayfinder (skills/engineering/wayfinder)

- **destination**: the outcome the map is finding its way to; it fixes the map's scope.
- **decision ticket**: a child issue that resolves a question or prerequisite before implementation; it is not an implementation ticket.
- **map**: the canonical issue that indexes a wayfinder effort, its decisions, its unresolved fog, and its scope boundary.
- **frontier**: the open, unblocked, unclaimed decision tickets available to resolve.
- **fog of war**: in-scope work that is known to be ahead but cannot yet be stated as a precise ticket.
- **ticket type**: the `research`, `prototype`, `grilling`, or `task` label that identifies how a decision ticket is resolved.

## prototype (skills/engineering/prototype)

- **throwaway spike**: a disposable implementation used to answer one design question; its source is discarded and never merged into production.

## lit-research (skills/research/lit-research)

- **canonical record**: the normalized paper representation all sources map into, keyed by DOI (source-native id when no DOI exists). Embodied by the record dataclass in `scripts/common.py`.
- **snowballing**: expanding a paper set by walking a seed paper's citation graph — backward through its references and forward through papers citing it — iterating until new results stop appearing (saturation).
- **reference-check**: verifying a bibliography entry against Crossref: the DOI resolves, the metadata matches, and the work is not retracted. An entry that cannot be confidently matched is reported *unverifiable*, never guessed.
- **screening**: judging each candidate paper against the review's inclusion criteria; a lit-review step performed by the agent, not a script.
- **annotated bibliography**: the lit-review deliverable — the screened paper set with a short relevance note per paper, every entry sourced from script output.
