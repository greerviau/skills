# skills

Reusable agent skills for engineering and scientific research.
Each skill is a self-contained, plain-markdown procedure doc with a small YAML frontmatter header.

Skills are organized into categories, and ship as separately installable Claude Code plugins so you can take the categories you want and skip the rest.

## Install with skills.sh

The [skills.sh](https://skills.sh/greerviau/skills) installer copies the skills into your project so you can hack on them and make them your own.
It fetches this repo directly - no manual cloning or symlinking required.

Install every skill:

```bash
npx skills@latest add greerviau/skills
```

Then pick the skills you want and the agents to install them on.

## Install as Claude Code plugins

Prefer a plug-and-play install you don't maintain by hand?
The skills also ship as native [Claude Code plugins](https://code.claude.com/docs/en/plugins): a read-only, always-current bundle you don't edit, updated when this repo ships a new version.

This repo is a Claude Code plugin marketplace (`.claude-plugin/marketplace.json`) that registers the `greerviau` marketplace and serves one plugin per category.
Install only the categories you want:

Inside Claude Code:
```bash
/plugin marketplace add greerviau/skills
/plugin install <plugin>@greerviau
```

Or from your shell:
```bash
claude plugin marketplace add greerviau/skills
claude plugin install <plugin>@greerviau
```

Two ways to install, two philosophies:

- **[skills.sh](https://skills.sh/greerviau/skills)** copies the skills into your project so you can hack on them and make them your own.
- **The plugins** keep them as read-only, always-current bundles you don't edit - best when you just want the set to work and follow along as it evolves.

## Skills reference

### Engineering 

`/plugin install greerviau-engineering@greerviau`

- **[standards](skills/engineering/standards/SKILL.md)** — the shared house rules the other engineering skills enforce (artifact audience and length, documentation and plain-language style, naming and ubiquitous language, testing bias, branch hygiene, issue hygiene, PR/commit hygiene, and the interactive-vs-autonomous interaction contract), kept in one place so a change applies everywhere.
- **[design](skills/engineering/design/SKILL.md)** — the shared vocabulary for structural judgment (module depth, information hiding, seam placement, error-condition elimination, navigability), read rather than invoked, so a structural claim is citable instead of asserted as taste.
- **[improve-codebase-architecture](skills/engineering/improve-codebase-architecture/SKILL.md)** - scans a codebase for evidence-backed structural opportunities, ranks them, and presents a visual HTML report before implementation.
- **[spec](skills/engineering/spec/SKILL.md)** — turns a raw request into a reviewed plan of action: interviews the user to pin down requirements and terminology, explores the code to discover scope, settles the approach, maintains the repo's ubiquitous-language glossary, then writes the detailed agent-facing implementation plan against the real code and derives the short human-facing spec that carries the review gate from it, so the review lands on an approach the code has already been checked against.
- **[spec-to-tickets](skills/engineering/spec-to-tickets/SKILL.md)** — turns a reviewed spec into GitHub Issues with no configuration: judges the spec's scope to pick a single-issue / flat / parent-with-native-sub-issues shape, files each one through open-issue, and records the issue URLs back in the spec so re-runs don't duplicate.
- **[wayfinder](skills/engineering/wayfinder/SKILL.md)** — maps work larger than one agent session as a GitHub issue map of decision tickets, advances one frontier ticket at a time, and hands the cleared map to spec rather than implementing it.
- **[open-issue](skills/engineering/open-issue/SKILL.md)** — the single source of truth for issue conventions: checks for duplicates, honors the repo's issue template, writes a plain descriptive title and a short problem/reproduction/acceptance-criteria body, and labels from the repo's real labels read with `gh label list` rather than invented ones.
- **[dev-workflow](skills/engineering/dev-workflow/SKILL.md)** — the end-to-end development loop for a GitHub repo: an issue for the work before any code, isolated worktree, staged commits, local validation, an evergreen PR that closes the issue, watching CI to green, and cleanup.
- **[open-pr](skills/engineering/open-pr/SKILL.md)** — writes the `feat(...)`/`fix(...)` title and an evergreen body (problem, intent, changes, testing, additional testing, regressions) with no AI attribution or volatile details, then opens the PR; used standalone or as the PR step of dev-workflow.
- **[tdd](skills/engineering/tdd/SKILL.md)** — the test-first loop: pick the seam, write the failing test before any implementation, confirm it fails for the right reason, minimum code to green, refactor under green, then hands off to dev-workflow to land the change.
- **[tech-research](skills/engineering/tech-research/SKILL.md)** — investigates a technical question about third-party or external behavior against a strict source hierarchy (installed source and tests, then vendor docs for the pinned version, then specs/RFCs, then release notes and issue trackers), and writes a version-pinned findings file with a citation and confidence level per claim.
- **[dep-upgrade](skills/engineering/dep-upgrade/SKILL.md)** - upgrades Python dependencies with uv-only commands, lockfile discipline, lockstep tags for git-sourced internal packages, and downstream-suite verification.
- **[debug](skills/engineering/debug/SKILL.md)** — reproduces a bug end-to-end the way a user hits it before forming any fix hypothesis, localizes the root cause, and hands off to dev-workflow to land the fix as a regression-tested change.
- **[flake-hunt](skills/engineering/flake-hunt/SKILL.md)** - investigates intermittent, order-dependent, seed-dependent, and CI-only test failures with fixed-count reruns, base-versus-change comparison, seed and order bisection, and a bounded quarantine policy.
- **[merge-conflict](skills/engineering/merge-conflict/SKILL.md)** - resolves Git merge and rebase conflicts from both sides' intent, checks the integration contract, reruns the repository checks, and completes the operation.
- **[review](skills/engineering/review/SKILL.md)** — reviews a diff, branch, or PR against your engineering standards (lint clean, tests present and green, no flakiness, correctness and structure over dev cost) and, when one can be located, against the originating spec or issue, flagging incidental defects even when unrelated.
- **[refactor](skills/engineering/refactor/SKILL.md)** — improves code structure without changing behavior, guarded by an unchanged test suite; adds characterization tests first when coverage is thin.
- **[perf](skills/engineering/perf/SKILL.md)** — measure-first optimization: state a numeric target, baseline and profile with a reproducible harness, change one thing with the test suite staying green, then re-measure on the same harness and report the before/after delta.
- **[prototype](skills/engineering/prototype/SKILL.md)** - answers a design question with a throwaway spike whose source is discarded and never merged.
- **[doc-audit](skills/engineering/doc-audit/SKILL.md)** — after any code change, audits the documentation surface it touched (docstrings, comments, READMEs, docs, examples) and rewrites stale passages in present tense describing current state, then delegates a plain-language check of the prose to a subagent.
- **[mermaid](skills/engineering/mermaid/SKILL.md)** — the draft/render/look/critique/refine loop for mermaid diagrams, checked against a layout checklist (subgraph boxes, edge crossings, aspect ratio, theme-neutral styling) and rendered locally, never via a hosted service.

How these skills fit together — entry points, components, and hand-offs — is mapped in [docs/engineering-skill-composition.md](docs/engineering-skill-composition.md).

### Research 

`/plugin install greerviau-research@greerviau`

- **[lit-research](skills/research/lit-research/SKILL.md)** — scientific-literature tooling backed by OpenAlex, Semantic Scholar, PubMed, and Crossref: search, citation-graph snowballing, bibliography reference-checks, and an orchestrated literature-review workflow, with every citation grounded in real API records.

### Personal 

`/plugin install greerviau-personal@greerviau`

- **[opinions](skills/personal/opinions/SKILL.md)** — consults `~/OPINIONS.md` before making subjective calls the user has likely already formed a view on, and offers to record new opinions the user states mid-task.
- **[doc-review](skills/personal/doc-review/SKILL.md)** — on request, renders a document in the browser for Notion-style inline commenting, then hands every comment back with its source line range and quoted text so the document can be revised against them.
- **[my-voice](skills/personal/my-voice/SKILL.md)** — captures how you write into `~/VOICE.md` from samples you supply, then rewrites a finished draft against it in a subagent pass bounded to wording only, so a spec or README goes out sounding like you without a fact or a section moving.
- **[memory-audit](skills/personal/memory-audit/SKILL.md)** — on request, scans every agent memory directory for duplicates, contradictions, stale claims, rules a `CLAUDE.md` already states, and index drift, then interviews you over each memory with a case against it and applies your keep/edit/delete/move verdicts, so the corpus an agent recalls stays true and small.

## Contributing

Maintainer dev scripts live in [`scripts/`](scripts):

- `scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` so local edits are live.
- `scripts/list-skills.sh` lists every skill in the repo.

Add a new skill by creating `skills/<category>/<name>/SKILL.md`, then register it in both `package.json` (the `skills` array, for the skills.sh installer) and, if it's a new category, `.claude-plugin/marketplace.json` (a new plugin entry).

## License

MIT — see [LICENSE](LICENSE).
