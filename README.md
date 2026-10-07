# skills

Reusable agent skills for engineering and scientific research.
Each skill is a plain-markdown procedure doc with a small YAML frontmatter header.

Skills are organized into categories and ship as separately installable Claude Code plugins, so you can take the categories you want and skip the rest.

## Install with skills.sh

The [skills.sh](https://skills.sh/greerviau/skills) installer copies the skills into your project so you can edit them.
It fetches this repo directly, with no cloning or symlinking.

Install every skill:

```bash
npx skills@latest add greerviau/skills
```

Then pick the skills you want and the agents to install them on.

## Install as Claude Code plugins

The skills also ship as native [Claude Code plugins](https://code.claude.com/docs/en/plugins): a read-only bundle that updates when this repo ships a new version.

This repo is a Claude Code plugin marketplace (`.claude-plugin/marketplace.json`) that registers the `greerviau` marketplace and serves one plugin per category.
Install only the categories you want.

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

Choose by how you want to maintain the skills:

- [skills.sh](https://skills.sh/greerviau/skills) copies the skills into your project, and you edit them.
- The plugins are read-only bundles that follow this repo as it changes.

## Skills reference

Claude Code uses `disable-model-invocation: true` to mark a skill as user-invoked.
Skills without that field are model-invoked and available whenever the model recognizes a matching task.
Each category below separates the two.

### Engineering

`/plugin install greerviau-engineering@greerviau`

#### User-invoked

- [improve-codebase-architecture](skills/engineering/improve-codebase-architecture/SKILL.md) - scans a codebase for evidence-backed structural opportunities and ranks them in an HTML report before implementation.
- [spec](skills/engineering/spec/SKILL.md) - turns a raw request into a reviewed spec. It interviews the user, explores the code, settles the approach and checks each decision against the code, maintains the repo's ubiquitous-language glossary, and writes a short human-facing spec whose work items become tickets.
- [spec-to-tickets](skills/engineering/spec-to-tickets/SKILL.md) - turns a reviewed spec into GitHub Issues. It picks a single-issue, flat, or parent-with-sub-issues shape from the spec's scope, files each issue through `open-issue`, and records the issue URLs in the spec so re-runs do not duplicate.
- [triage](skills/engineering/triage/SKILL.md) - classifies an inbound GitHub issue or pull request and produces an agent-ready brief with evidence, scope, acceptance criteria, and verification.
- [handoff](skills/engineering/handoff/SKILL.md) - compacts the current conversation into a handoff document for another agent.

#### Model-invoked

- [standards](skills/engineering/standards/SKILL.md) - the house rules the other engineering skills enforce: artifact audience and length, documentation and plain-language style, ubiquitous language, branch, issue, and PR hygiene, and the interactive and autonomous interaction contract. Its [CODING-STANDARDS.md](skills/engineering/standards/CODING-STANDARDS.md) holds the rules for code: comments, docstrings, identifiers, and test-first testing.
- [design](skills/engineering/design/SKILL.md) - vocabulary for structural judgment (module depth, information hiding, seam placement, error-condition elimination, navigability), so a structural claim can be cited.
- [open-issue](skills/engineering/open-issue/SKILL.md) - issue conventions: checks for duplicates, honors the repo's issue template, writes a descriptive title and a short problem, reproduction, and acceptance-criteria body, and labels from `gh label list`.
- [dev-workflow](skills/engineering/dev-workflow/SKILL.md) - the development loop for a GitHub repo: an issue before code, an isolated worktree, test-first building, local validation, an evergreen PR that closes the issue, CI to green, and cleanup.
- [open-pr](skills/engineering/open-pr/SKILL.md) - writes the `feat(...)` or `fix(...)` title and an evergreen body (problem, changes, testing, additional testing, regressions) with no AI attribution or volatile details, then opens the PR.
- [tdd](skills/engineering/tdd/SKILL.md) - the test-first loop every behavior change runs: pick the seam, write the failing test, confirm it fails for the right reason, write the minimum code to pass, and refactor under green.
- [tech-research](skills/engineering/tech-research/SKILL.md) - answers a question about third-party or external behavior from a source hierarchy (installed source and tests, vendor docs for the pinned version, specs and RFCs, release notes and issue trackers) and writes a version-pinned findings file with a citation and confidence level per claim.
- [dep-upgrade](skills/engineering/dep-upgrade/SKILL.md) - upgrades Python dependencies with uv, reviews the lockfile diff, moves git-sourced internal packages to the same tag, and verifies the downstream suite.
- [debug](skills/engineering/debug/SKILL.md) - reproduces a bug end to end as a user hits it before forming a fix hypothesis, then localizes and confirms the root cause.
- [flake-hunt](skills/engineering/flake-hunt/SKILL.md) - investigates intermittent, order-dependent, seed-dependent, and CI-only test failures with fixed-count reruns, base-versus-change comparison, seed and order bisection, and a bounded quarantine policy.
- [merge-conflict](skills/engineering/merge-conflict/SKILL.md) - resolves merge and rebase conflicts from both sides' intent, reruns the repository checks, and completes the operation.
- [review](skills/engineering/review/SKILL.md) - reviews a diff, branch, or PR against the engineering standards (lint, tests, flakiness, correctness, structure) and the originating spec or issue when one can be found, and flags incidental defects.
- [refactor](skills/engineering/refactor/SKILL.md) - improves code structure without changing behavior, guarded by an unchanged test suite, and adds characterization tests first when coverage is thin.
- [perf](skills/engineering/perf/SKILL.md) - measure-first optimization: a numeric target, a baseline and profile from a reproducible harness, one change at a time, and a before/after report from the same harness.
- [prototype](skills/engineering/prototype/SKILL.md) - answers a design question with a throwaway spike whose source is discarded.
- [doc-audit](skills/engineering/doc-audit/SKILL.md) - after a code change, audits the documentation it touched (docstrings, comments, READMEs, docs, examples), rewrites stale passages in present tense, and has a subagent check the prose for plain language.
- [mermaid](skills/engineering/mermaid/SKILL.md) - the draft, render, critique, refine loop for mermaid diagrams, checked against a layout checklist and rendered locally.

[docs/engineering-skill-composition.md](docs/engineering-skill-composition.md) maps the entry points, components, and hand-offs between these skills.

### Research

`/plugin install greerviau-research@greerviau`

#### Model-invoked

- [lit-research](skills/research/lit-research/SKILL.md) - literature search, citation-graph snowballing, bibliography reference checks, and a literature-review workflow backed by OpenAlex, Semantic Scholar, PubMed, and Crossref, with every citation taken from API records.

### Personal

`/plugin install greerviau-personal@greerviau`

#### User-invoked

- [doc-review](skills/personal/doc-review/SKILL.md) - renders Markdown, text, HTML, PDF, or DOCX in the browser for inline comments, then returns each comment with its source location and quoted text so the document can be revised.
- [my-voice](skills/personal/my-voice/SKILL.md) - captures how you write into `~/VOICE.md` from samples you supply, then rewrites a finished draft against it in a subagent pass limited to wording, so no fact or section changes.
- [memory-audit](skills/personal/memory-audit/SKILL.md) - scans every agent memory directory for duplicates, contradictions, stale claims, rules a `CLAUDE.md` already states, and index drift, then asks you to rule on each memory with a case against it and applies your keep, edit, delete, and move verdicts.

#### Model-invoked

- [opinions](skills/personal/opinions/SKILL.md) - reads `~/OPINIONS.md` before subjective calls the user has likely formed a view on, and offers to record opinions the user states mid-task.

## Contributing

Maintainer scripts are in [`scripts/`](scripts):

- `scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` so local edits take effect immediately.
- `scripts/list-skills.sh` lists every skill in the repo.

Add a skill by creating `skills/<category>/<name>/SKILL.md`, then register it in `package.json` (the `skills` array, for the skills.sh installer) and, for a new category, in `.claude-plugin/marketplace.json` (a new plugin entry).
See [AGENTS.md](AGENTS.md) for authoring rules.

## License

MIT, see [LICENSE](LICENSE).
