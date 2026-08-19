# engineering skills expansion: design, tdd, tech-research, perf, mermaid

Status: proposed. Each Tier 1 skill below needs its own spec before implementation.

## Summary

The engineering plugin currently covers the plan/build/land/verify loop: `spec`, `spec-to-tickets`, `dev-workflow`, `open-pr`, `doc-audit`, `debug`, `refactor`, `review`, `handoff`, with `standards` as the shared policy reference.
This plan scopes the next wave, drawn from a gap analysis against [mattpocock/skills `skills/engineering`](https://github.com/mattpocock/skills/tree/main/skills/engineering) plus the parts of the day-to-day workflow the current set leaves unaddressed.

Tier 1, in order of structural importance (`Steps` below lands them in a different order, smallest first):

- **`design`** - a second policy reference alongside `standards`, holding the vocabulary for *what good structure is* (module depth, information hiding, seam placement, testability). Consumed by `spec`, `refactor`, and `review`, all three of which currently assert "simplicity" with no operational definition.
- **`tdd`** - the test-first loop as an entry point: choose the seam, write the failing end-to-end test, watch it fail for the right reason, minimum code to green, refactor under green, then land it (the `dev-workflow` skill, if you use it).
- **`tech-research`** - the engineering twin of `research/lit-research`: investigate a technical question against primary sources (vendor docs, the installed dependency's source, RFCs) and capture findings with citations and per-claim confidence.
- **`perf`** - measure-first optimization: baseline with a reproducible harness, profile before hypothesizing, change one thing, re-measure, keep the harness. Structurally `refactor` but guarded by a benchmark instead of a test suite.
- **`mermaid`** - the render-and-refine loop for diagrams: draft, render to an image, look at the layout, critique, refine, repeat. `standards` already forbids one-shotting a mermaid diagram and suggests delegating to a subagent, but supplies no procedure, so the rule is currently unenforceable. Smallest of the five and the first to land.

Tier 2 candidates are listed under [Deferred candidates](#deferred-candidates) with enough rationale to spec later.
Three improvements fall out of the same analysis but are edits to existing files rather than new skills; see [Non-skill fixes](#non-skill-fixes).

## Requirements

- **No duplication of the existing set or the built-ins.** Every proposal either fills a hole in the composition graph or encodes a house standard the built-ins do not know about. The gap analysis below records what was rejected as duplicate.
- **Composition over restatement.** Worktree mechanics, commit staging, PR conventions, and CI-watching live in `dev-workflow`; testing/doc/PR policy lives in `standards`. New skills reference them and never copy them.
- **Policy and procedure stay separated.** `standards` proved the pattern: a reference skill states rules, an entry-point skill supplies the procedure that applies them at the right moment. `design` follows the same split.
- **Descriptions carry concrete trigger phrases** in the established house style (a "Use when ..." situation clause plus quoted triggers), so model-decided invocation is reliable.
- **Each skill declares its interaction mode** per the contract in `standards`, degrading to a defensible default plus a recorded assumption when run autonomously.
- **Success criteria**: an agent with these installed will (a) justify a structural change in the vocabulary of `design` rather than by taste; (b) refuse to claim test-driven work when the implementation came first; (c) never assert an API fact without a primary source and a confidence level; (d) refuse to call an optimization successful without a before/after measurement from the same harness; (e) never commit a mermaid diagram that has not gone through at least one render-and-look cycle, whether that cycle ran inline or was delegated to a subagent that returns only the final source.
- **Skills stand alone.** Every hand-off names a sibling skill only as the option for a step outside the skill's own job ("the `dev-workflow` skill, if you use it"), never as a dependency the skill requires, per `CLAUDE.md`'s standalone-skill rule. Every drafted procedure in `Approach and design` below follows this phrasing; none of the five new skills requires another to complete its own job.
- **New `SKILL.md` files follow `CLAUDE.md`'s authoring rules as written**, including no em dashes. The existing files predate that rule and use them; the new ones don't inherit the habit by imitation.

## Scope

- **Primary repo**: `skills` (this repo). No other repos affected.
- New skill folders under `skills/engineering/`: `design`, `tdd`, `tech-research`, `perf`, `mermaid`.
- Existing files modified:
  - `skills/engineering/standards/SKILL.md` - repoint the mermaid bullet at the `mermaid` skill for the procedure instead of gesturing at "refine it until it reads well"; rewrite the opening framing so `standards` stays accurate as the single source of truth for *compliance* rules once `design` exists as a peer reference for structural vocabulary, and refresh the list of referencing skills to add `tdd`, `perf`, and `mermaid`.
  - `skills/engineering/refactor/SKILL.md` and `skills/engineering/review/SKILL.md` - reference `design` for the definition of better structure instead of leaving it implicit.
  - `skills/engineering/spec/SKILL.md` - reference `design` in the approach/design section of a plan.
  - `skills/engineering/spec-to-tickets/SKILL.md` - add `disable-model-invocation: true` and trim the description to drop the now-dead natural-language trigger phrases, matching `handoff`'s shape (see [Non-skill fixes](#non-skill-fixes)).
  - `skills/engineering/review/SKILL.md` - add the spec-conformance axis, including its degradation path when no originating spec is found (see [Non-skill fixes](#non-skill-fixes)).
  - `skills/engineering/dev-workflow/SKILL.md` - step 2 ("Do the work") names `tdd` as the option to reach for when the request is explicitly test-first, the same way it already names `standards` for policy. This is what makes "`dev-workflow` invokes `tdd` in turn" (see `How they compose`) an actual edit rather than an assertion.
  - `skills/engineering/debug/SKILL.md` - add the reciprocal reference to `tdd` next to the existing `dev-workflow` reference, so the "each references the other" claim about `tdd`/`debug` is backed by both files.
  - `docs/engineering-skill-composition.md` - update the graph and role table; see `Steps` for why this is a restructuring, not just an extension.
  - `.claude-plugin/marketplace.json` - add the new skill names to the `greerviau-engineering` keywords and refresh the plugin description.
  - `README.md` - add an entry per new skill in the engineering list.
  - `package.json` - register each of the five new skills in the `skills` array as it lands (see `Steps`), and fix the array's pre-existing drift from the tree up front: drop `./skills/engineering/pr-describe` (the directory no longer exists; the skill is now `open-pr`), and add the three entries currently missing regardless of this wave - `open-pr`, `standards`, and `handoff`. This array is the skills.sh installer's only manual registration surface; `scripts/link-skills.sh` and `scripts/list-skills.sh` glob for `SKILL.md` and need no change.
  - `docs/UBIQUITOUS-LANGUAGE.md` - add the terms each skill coins (candidates: deep module, seam, characterization test is already implied by `refactor`, baseline, harness, primary source, confidence level).
- **Out of scope**: any skill in [Deferred candidates](#deferred-candidates), and the mattpocock skills rejected as duplicates below.

## Gap analysis against mattpocock/skills

Rejected as already covered:

| Theirs | Ours | Note |
| --- | --- | --- |
| `implement` | `dev-workflow` | Same role; ours additionally owns worktrees, CI-watching, and PR lifecycle. |
| `diagnosing-bugs` | `debug` | Same reproduce-first loop. |
| `to-spec`, `to-tickets` | `spec`, `spec-to-tickets` | `to-spec` skips the interview; our `spec` interviews by design, and skipping it is a mode of `spec`, not a sibling skill. |
| `code-review` | `review` | Their two-axis split is worth stealing as an edit to `review`, not a new skill. |
| `research` | `research/lit-research` | Ours is science-only. The engineering half is the `tech-research` gap. |
| `resolving-merge-conflicts` | none | Genuine gap, but small; deferred. |
| `grill-with-docs` | `spec`'s interview step | Only worth extracting if a second skill needs the same adversarial interview. |
| `improve-codebase-architecture` | none | Blocked on `design`; without the vocabulary the scan produces taste, not findings. |

Adopted as Tier 1: `codebase-design` becomes `design`, `tdd` stays `tdd`, `research` becomes `tech-research`.
Adopted as Tier 2: `triage`, `prototype`.
Net-new, not from their set: `perf` and `mermaid`.

## Approach and design

### `design`

A reference skill, peer to `standards`, read rather than invoked.
It holds the vocabulary and the trade-off rules for structural decisions:

- **Module depth**: interface surface area weighed against the functionality hidden behind it; shallow pass-through layers as the primary smell.
- **Information hiding**: what a caller is forced to know, and which leaks are load-bearing versus accidental.
- **Seam placement**: where the public boundary sits, and the consequence that the seam is also where tests attach. This is the hinge that makes `design` and `tdd` reinforce each other.
- **Error-condition elimination**: designing away an error case beats propagating it.
- **Navigability**: naming and locality so both a human and an agent can find the code that owns a concept, which connects to the ubiquitous-language rule in `standards`.

Why it ranks first: `refactor` justifies a change as "aligning with conventions" and `review` judges "simplicity and maintainability over development cost". Neither term is defined anywhere in the repo, so today both resolve to whatever the model finds tasteful in the moment. `design` makes those judgments citable and reviewable.

Settled: split from `standards` rather than merged into it. `standards` is a rule list an agent complies with; `design` is a vocabulary an agent reasons in. Folding both into one document makes the compliance checklist unusable - a reader can no longer tell "must do" from "here's how to think about it" at a glance. Rejected alternative: fold `design`'s vocabulary into `standards` as more bullets under a new heading. Simpler as a single reference, but it erases exactly the distinction that makes `standards` checkable today; taken in the same breath, the corresponding edit to `standards`'s own opening framing is in `Scope`, since introducing a second policy reference would otherwise falsify its "single source of truth" claim.

Boundaries: states rules, never appears as a numbered step, produces no artifact of its own. Overlaps `refactor`'s own triggers ("make this more maintainable", "simplify this code"): the partition is that `design` is read while judging a structural question, never invoked for a request, while `refactor` is the entry point invoked when the request is to actually restructure code. A request framed as "is this well-structured" or "how should this be organized" reads `design`; a request framed as "clean this up" or "reduce duplication" invokes `refactor`, which then reads `design` for the vocabulary it judges by. Same shape against `tdd`, which also talks about seams: a request to explain or judge a seam reads `design`; a request to drive the test-first loop invokes `tdd`, which reads `design` for the harder calls (see `tdd`'s step 1).

### `tdd`

An entry point that also serves as a component `dev-workflow` names as an option when a change is being built test-first (see `Scope`; this is a real edit to `dev-workflow/SKILL.md`, not just an assertion here).
Procedure, in outline:

1. **Pick the seam** - the point where the change's public boundary sits, which is also where the test attaches. Drive the real entry point (CLI, endpoint, flow), not an internal helper, per the E2E bias in `standards`. This is enough to execute the step alone; `design` holds the fuller vocabulary (module depth, information hiding) for the harder calls, and is named there as where to go for it.
2. **Build the harness if it does not exist.** When there is no fixture, no runner, or no way to drive the seam, building that is step zero and lands as its own commit. This is the step that most often gets skipped, and skipping it is what pushes tests down to whatever unit is convenient.
3. **Red.** Write one failing test that expresses the desired behavior. Run it. Confirm it fails *for the intended reason*, not on an import error or a missing fixture.
4. **Green.** Minimum implementation to pass. No extra scope.
5. **Refactor under green.** Structural cleanup beyond a tidy-up is `refactor`'s own job (the `refactor` skill, if you use it).
6. Repeat per behavior. Landing the change - staging commits, validating, opening the PR - is a separate step, done however you normally land changes (the `dev-workflow` skill, if you use it).

Explicit prohibition: writing the implementation first and the test afterward is not this skill, and describing that sequence as test-driven is a reporting failure. The skill states this directly because it is the dominant failure mode when an agent runs the loop unsupervised.

Relationship to `debug`, settled: `debug` already produces a failing reproduction, which is a red test by another name, which raises the question of merging the two. Kept separate because the trigger surfaces are disjoint - a request for new behavior versus a report of broken behavior - and merging would bury one procedure inside the other. `tdd` covers the feature case; `debug` keeps the bug case. Each references the other rather than absorbing it.

Relationship to `dev-workflow`, the sharper collision: `dev-workflow`'s own trigger surface ("any request to write and land code in a repo") is broad enough to also catch a test-first request, so the partition is drawn explicitly rather than left to overlap. `tdd`'s own triggers stay narrow and explicit - "TDD this", "test-drive this", "write the test first", "red, green, refactor" - so it never competes with `dev-workflow`'s catch-all for an ordinary build request; a plain "implement this feature" still lands on `dev-workflow` directly, which does the work itself without routing through `tdd`. `dev-workflow` is the one edited to close the loop (see `Scope`): its own step 2 names `tdd` as the option for when the request is explicitly test-first, which is what makes "`dev-workflow` invokes `tdd` in turn" true rather than aspirational, without making `dev-workflow` depend on `tdd` being installed - a request without `tdd` present just gets built directly.

Policy stays in `standards` (E2E bias, regression test from the reproduction, flakiness is a defect). `tdd` supplies only the loop.

### `tech-research`

Investigate a technical question against high-trust primary sources and capture the answer as a durable markdown file.

- **Source hierarchy, stated explicitly**: the installed dependency's own source and tests, then official vendor documentation for the pinned version, then specifications and RFCs, then release notes and issue trackers, then everything else. Blog posts and model recall are not sources.
- **Per-claim confidence** (high/moderate/low/unknown) and a citation per claim, matching the global rule that facts are verified and uncertainty is labeled rather than smoothed over.
- **Version-pinned answers.** An API fact is about a version; the findings file records which one.
- **Durable output** in the repo, default `docs/analysis/` alongside `docs/plans/`, this repo's location for a standalone written artifact that isn't a plan, so `spec` can cite it instead of re-deriving it.
- Delegates breadth to background agents where the question decomposes.

Why it earns a slot: it is the mechanism behind the "never hallucinate, always give confidence levels" rule. Today that rule is a hope; a skill makes it a procedure with an artifact attached.

Boundary against `spec`: `tech-research`'s top-ranked source is the installed dependency's own source and tests, which sounds like the same local-code reading `spec`'s exploration step does, but the object of the question differs. `tech-research` answers questions about third-party or external behavior - what a library actually does, what a spec/RFC actually requires; `spec` discovers scope in *this repo's own* code - where a concept lives, what calls what. "How does this dependency behave" is `tech-research`; "where in our code does this belong" is `spec`.

### `perf`

Measure-first optimization, guarded by a benchmark the way `refactor` is guarded by a test suite.

1. **State the target.** Latency, throughput, or cost, with a number and a workload. "Faster" is not a target.
2. **Build the harness and take a baseline.** Reproducible, committed, and cheap enough to re-run. A one-off timing in a shell is not a baseline.
3. **Profile before hypothesizing.** The bottleneck is measured, never guessed.
4. **Change one thing.** Behavior stays fixed; the test suite must stay green, which is the boundary against a smuggled behavior change.
5. **Re-measure on the same harness** and report before/after with the workload named.
6. **Keep the harness** so the next regression is detectable. Landing the change is a separate step, done however you normally land changes (the `dev-workflow` skill, if you use it).

Boundary against `debug`: `perf` owns latency, throughput, and cost; `debug` owns wrong and broken. A report that something is slow is `perf`; a report that something is wrong or crashes is `debug`.

Why net-new: nothing in the current set has a notion of cost or speed. `dev-workflow` validates correctness only, so an optimization lands today with no evidence it optimized anything. Pipeline and dataset-build work is where this bites in practice, which makes `perf` the fastest of the four to pay for itself even though `design` is the larger structural fix.

Interaction mode: autonomous runs report the measured delta and refuse to declare success on an unmeasured change.

### `mermaid`

A component skill, invoked by anything that writes a diagram into markdown: `spec`, `design`, `doc-audit`, `open-pr`, ADRs, READMEs.
`standards` already carries the policy ("favor mermaid over ASCII", "don't one-shot a mermaid diagram, refine it until it reads well, using subagents if needed") with no procedure attached, which makes it a rule nothing can enforce.

The loop:

1. **Draft** the diagram from its intent, stated in one sentence ("show where the new skills attach to the existing hand-off graph").
2. **Render** it to an image locally and **look at the image**. This is the non-negotiable step: layout defects are invisible in source.
3. **Critique** against the layout checklist below.
4. **Refine and re-render** until it passes. One render is the floor, not the target.

Layout checklist, derived from the five-render session that produced the diagram in this plan:

- **`direction` inside a subgraph is ignored when an edge crosses the subgraph boundary.** A `direction TB` group silently lays out horizontally and sprawls the whole diagram sideways. This trap alone cost two renders.
- **A subgraph box forces its children into a stack** and usually buys dead space next to it. Drop the box unless the grouping *is* the message; ranks already communicate stages.
- **Aspect ratio between about 4:3 and 16:9.** A 5:1 sprawl or a 1:3 column means the structure is wrong, not the styling.
- **Edge labels stay at one to three words.** Label width drives node spacing, so a long label pushes the whole layout apart.
- **A skip edge spanning more than two ranks sweeps the margin.** Either restructure or accept exactly one.
- **Reverse an edge when it flattens a rank without changing meaning.** `spec -->|open question| tech-research` says the same thing as the reverse and removes a rank.
- **Zero crossings.** A crossing means the rank assignment is wrong, not that the diagram is inherently complex.
- **Theme-neutral styling only:** stroke-based `classDef`, never `fill`, because GitHub renders both light and dark.

Mechanics: render with the local mermaid CLI (`npx -y -p @mermaid-js/mermaid-cli mmdc -i d.mmd -o d.png -b white -s 2`), first run pays a one-time Chromium download.
Working `.mmd` and `.png` files live in the scratchpad and are never committed; only the final fenced block lands in the document.
Hosted renderers such as mermaid.ink are out, since they publish the diagram content to a third party.

Delegation, which is where the token argument bites: hand the intent plus the checklist to a subagent and have it return only the final mermaid source.
The renders and intermediate images stay in the subagent's context.
Producing the one diagram in this plan cost five renders and five image reads inline; that is exactly the cost a subagent should absorb.

Boundaries: does not decide *whether* a diagram belongs (that is the `standards` rule) and does not touch the surrounding prose.

## How they compose

Runtime hand-offs in the target state, with the three new entry points outlined (`design` and `mermaid` are deliberately absent - see the reading notes below):

```mermaid
flowchart TB
    spec[spec] -->|open question| techresearch[tech-research]
    spec -->|plan| s2t[spec-to-tickets]
    spec -->|plan| dw[dev-workflow]
    s2t -->|issues| dw

    tdd[tdd] -->|test-first change| dw
    debug[debug] -->|confirmed cause| dw
    refactor[refactor] -->|guarded change| dw
    perf[perf] -->|measured change| dw
    review[review] -->|findings| dw

    dw -->|docs| docaudit[doc-audit]
    dw -->|runtime| run[run]
    dw -->|PR| openpr[open-pr]

    classDef new stroke:#2f81f7,stroke-width:3px
    class techresearch,tdd,perf new
```

Reading notes, kept in prose rather than drawn, because adding them as edges turns the graph into a hairball:

- **`standards` and `design` are policy references**, read by every skill above and never a step in any of them. They have no edges by design; the role table in `docs/engineering-skill-composition.md` records which skill reads which.
- **`tdd` doubles as a component.** It is drawn as an entry point handing a change to `dev-workflow`, and `dev-workflow` names it in turn as the option for building test-first (see `Scope`). The back edge is omitted to keep the graph acyclic.
- **`tech-research`'s return is the same shape**, and it's the other omission behind "acyclic as drawn": its findings file exists "so `spec` can cite it instead of re-deriving it", which is a `spec`-to-`tech-research`-to-`spec` loop at runtime. Omitted for the same reason as `tdd`'s back edge.
- **`mermaid` is a component of every skill that writes a diagram**, so it attaches everywhere and is drawn nowhere.
- **`handoff` has no runtime edges** and is omitted; it produces a document and hands off to nothing.

## Non-skill fixes

Three findings from the same analysis are edits, not new skills, and can land ahead of the Tier 1 work.

1. **`spec-to-tickets` is model-invocable despite its own description.** Its description says it should be used "explicitly, never automatically, since it creates work items other people see", yet only `handoff` sets `disable-model-invocation: true`. The description is documentation; the frontmatter flag is enforcement. Set the flag - and account for what it actually does: `disable-model-invocation` turns off *all* model-decided routing, not just the unprompted-fire case, so after this change a request phrased as "turn this spec into tickets" no longer reaches the skill at all; only the explicit `/spec-to-tickets` slash command does. That's the intended outcome here - ticket creation should take a deliberate invocation, not a phrase match - so the description's advertised triggers ("turn this spec into tickets", "create tickets/issues for this plan", "file issues for this") become dead text and must be trimmed in the same change, matching the shape `handoff` already uses: a short statement of what the skill does, no trigger phrases to advertise. Give it an `argument-hint` the way `handoff` does, since the flag makes the slash command the only entry point, e.g. a path to the spec, optional if it can be inferred from context.
2. **`review` has no spec-conformance axis.** It checks the diff against the standards bar but never against what the originating spec or issue asked for, so a well-built change that solves the wrong problem passes. Add a second axis that reads the originating spec/issue and reports scope drift, missing requirements, and out-of-scope additions, run as a parallel sub-agent alongside the standards pass. State both halves of this in the same edit: how the spec/issue is located (a `docs/plans/` reference in the PR body, a linked GitHub issue, a plan path named in the branch, or one the user supplies directly), and what happens when none resolves - the axis reports "no originating spec located, conformance not assessed" and stops there. It never reconstructs an implied spec from the diff itself and grades against its own reconstruction; a confident finding with no ground truth is worse than no finding.
3. **`package.json`'s `skills` array is already stale**, independent of this wave: it lists `./skills/engineering/pr-describe`, a directory that no longer exists (the skill is now `open-pr`), and omits `open-pr`, `standards`, and `handoff` entirely - three missing entries, not the two it might look like at a glance. Fix that drift now, in step 1. The five new skills get their own entries later, one per step, alongside their own README/marketplace.json edits (see `Steps`) - not batched in here, since none of those directories exist yet. This is the array the skills.sh installer reads, and adding five more unregistered skills on top of existing drift leaves the installer serving a set that doesn't match the repo.

## Deferred candidates

Each needs its own spec if promoted; recorded here so the rationale is not re-derived.

- **`triage`** - inbound issues and external PRs to a category plus an agent-ready brief. The mirror image of `spec-to-tickets`, which is outbound. Value is highest if fleet-style runners consume briefs as their input format, since that translation is currently ad hoc.
- **`adr`** - `standards` explicitly exempts ADRs from the present-tense rule, but no skill produces one and the repo has no location convention for them. Cheap; a candidate to fold into `design` rather than stand alone.
- **`flake-hunt`** - `standards` declares flakiness a defect without supplying a procedure. Would cover rerun-N, seed and order bisection, "is CI red from this diff or from the base", and a quarantine policy.
- **`dep-upgrade`** - uv-only dependency work: lockfile discipline, lockstep tag bumps for git-sourced internal packages, and verification by running the downstream suite rather than the upgraded package's own.
- **`prototype`** - a throwaway spike that answers a design question and is explicitly never landed. The value is the boundary; the failure mode it prevents is a prototype accreting into main.
- **`map-subsystem`** - read a subsystem and emit a durable map document. The built-in `Explore` agent covers the reading; nothing makes the output persist.
- **`merge-conflict`** - small but real given long-lived worktrees and evergreen PRs: rebase-versus-merge policy, resolve semantically rather than textually, re-run the suite after.
- **`improve-codebase-architecture` analog** - scan a codebase for structural opportunities and rank them. Blocked on `design`; revisit once the vocabulary exists.

## Steps

1. Land the three [Non-skill fixes](#non-skill-fixes) - including the `package.json` registration fix, cheapest done here alongside the other two. Independent of everything below.
2. Spec and implement `mermaid`, then point the `standards` mermaid bullet at it. First because it is the smallest and because every later step writes diagrams. `docs/engineering-skill-composition.md`'s own diagram (see step 7) is the natural first dogfood target: it currently uses the `subgraph entry[Entry points]` / `subgraph components[Components]` boxes that this plan's own `mermaid` checklist condemns, so re-rendering it through the new loop is a real first use, not a synthetic one.
3. Spec and implement `design`, then update `refactor`, `review`, and `spec` to reference it, and edit `standards`'s opening framing per `Scope` so its "single source of truth" claim stays accurate once `design` exists as a peer reference.
4. Spec and implement `tdd`, wiring the seam concept to `design` and the policy to `standards`. In the same change, edit `dev-workflow/SKILL.md` (step 2 names `tdd` as the test-first option) and `debug/SKILL.md` (adds the reciprocal reference to `tdd`) - both are load-bearing for claims this plan makes about how the skills compose, not incidental cleanup.
5. Spec and implement `tech-research`.
6. Spec and implement `perf`.
7. After each: update `docs/engineering-skill-composition.md`, `README.md`, `.claude-plugin/marketplace.json`, `package.json` (add that skill's own entry to the `skills` array - the pre-existing drift is fixed once, in step 1; each new skill's own registration lands with the skill, not batched to the end), and `docs/UBIQUITOUS-LANGUAGE.md` in the same change. The composition-doc update is a restructuring, not just an extension: the graph in `How they compose` drops the dotted `standards`/`design` policy edges the current doc draws, which retires its "Dotted arrows are policy references" legend line too. Its role-table refresh is also the moment to label `run` as harness-provided rather than a skill in this repo (there is no `skills/engineering/run/`; the current doc already lists it in the Components table without saying so, and this wave shouldn't repeat the ambiguity).

## Testing and verification

- Each new skill is exercised on a real task in a real repo before it is considered done, not just read for plausibility.
- `design` is verified indirectly: a `refactor` or `review` run after it lands should cite its vocabulary for a structural claim rather than asserting taste.
- `tdd` is verified by checking commit order on a task run with it: the failing test commit precedes the implementation.
- `tech-research` is verified by auditing a findings file for a citation and a confidence level on every claim.
- `perf` is verified by confirming the harness is committed and the before/after numbers come from the same workload.
- The `dev-workflow`/`debug`/`tdd` reciprocal references are verified directly: grep `dev-workflow/SKILL.md` and `debug/SKILL.md` for `tdd` after step 4 lands, confirming the relationship is prose in both files, not just asserted in this plan.
- `package.json`'s `skills` array is verified against the tree: every `skills/*/*/SKILL.md` directory has a corresponding entry and no entry points at a missing directory.
- `mermaid` is verified against a deliberately bad diagram: hand it a subgraph-with-crossing-edges sprawl and confirm the loop renders it, names the defect from the checklist, and returns a restructured version rather than a restyled one.

## Risks and open questions

The two design forks this section previously carried as open questions - whether `design` belongs inside `standards`, and whether `tdd` overlaps `debug` enough to merge - are settled decisions, not open questions: both are answered, with the rejected alternative recorded, in `design`'s and `tdd`'s own sections above. What's left here is the one question this plan genuinely leaves open, plus standing risks.

- **Skill sprawl dilutes retrieval.** Every added skill competes for model-decided invocation, so overlapping trigger surfaces make all of them fire less reliably. This wave found five concrete overlaps and drew an explicit partition for each, recorded where the overlap lives rather than here: `design`/`tdd` (vocabulary versus loop, both reached through "seam"), `tdd`/`dev-workflow` (explicit test-first phrasing versus the generic build catch-all), `perf`/`debug` (slow versus wrong/broken), `tech-research`/`spec` (external behavior versus this repo's own code), and `design`/`refactor` (read while judging versus invoked to restructure). The risk itself stays standing for whatever lands next - each future addition needs the same partitioning exercise repeated, not a one-time fix.
- **Should the `mermaid` loop always delegate to a subagent?** The one design decision this plan leaves genuinely open. Delegating keeps renders and images out of the caller's context, which is the whole cost argument, but it also loses the caller's knowledge of what the diagram is for. This plan doesn't settle it; the `mermaid` spec does, against this criterion: does the caller's knowledge of the diagram's intent survive being compressed into an intent sentence plus the surrounding document section? Whichever way it resolves, success criterion (e) above is worded to admit either shape, so this plan's own success criteria don't have to be revisited once the spec decides.
- **First-run Chromium download** makes the render step slow exactly once per machine. Acceptable, but the skill should say so rather than let it look like a hang.
- **Where do `perf` findings live?** Either the PR body or a durable file under `docs/analysis/`. Genuinely deferrable to the `perf` spec; this plan's lean is the PR body for a one-off and a file once the harness becomes a standing benchmark.

## Follow-ups

- Promote the remaining deferred candidates as the pain shows up, most likely `triage`, `prototype`, and `map-subsystem` next.
- Consider extracting `spec`'s interview step into a reusable adversarial-interview component if `design` work turns out to need the same thing.
- Revisit whether `tech-research` and `research/lit-research` should share a plugin or stay split by category.
