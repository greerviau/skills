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
/plugin install <skill>@greerviau
```

Or from your shell:
```bash
claude plugin marketplace add greerviau/skills
claude plugin install <skill>@greerviau
```

Two ways to install, two philosophies:

- **[skills.sh](https://skills.sh/greerviau/skills)** copies the skills into your project so you can hack on them and make them your own.
- **The plugins** keep them as read-only, always-current bundles you don't edit - best when you just want the set to work and follow along as it evolves.

## Skills reference

### Engineering 

`/plugin install greerviau-engineering@greerviau`

- **[spec](skills/engineering/spec/SKILL.md)** — turns a raw request into a reviewed plan of action: interviews the user to pin down requirements and terminology, explores the code to discover scope, maintains the repo's ubiquitous-language glossary, and writes the plan to a markdown file for review before any building starts.
- **[spec-to-tickets](skills/engineering/spec-to-tickets/SKILL.md)** — turns a reviewed spec into tickets in your tracker (GitHub Issues, Linear, Trello): requires a configured tracker, judges the spec's scope to pick a single-ticket / flat / parent-with-sub-issues shape, and records the ticket IDs back in the spec so re-runs don't duplicate.
- **[dev-workflow](skills/engineering/dev-workflow/SKILL.md)** — the end-to-end development loop for a GitHub repo: isolated worktree, staged commits, local validation, an evergreen PR, watching CI to green, and cleanup.
- **[open-pr](skills/engineering/open-pr/SKILL.md)** — writes the `feat(...)`/`fix(...)` title and an evergreen body (problem, intent, changes, testing, additional testing, regressions) with no AI attribution or volatile details, then opens the PR; used standalone or as the PR step of dev-workflow.
- **[debug](skills/engineering/debug/SKILL.md)** — reproduces a bug end-to-end the way a user hits it before forming any fix hypothesis, localizes the root cause, and hands off to dev-workflow to land the fix as a regression-tested change.
- **[review](skills/engineering/review/SKILL.md)** — reviews a diff, branch, or PR against your engineering standards (lint clean, tests present and green, no flakiness, simplicity over dev cost), flagging incidental defects even when unrelated.
- **[refactor](skills/engineering/refactor/SKILL.md)** — improves code structure without changing behavior, guarded by an unchanged test suite; adds characterization tests first when coverage is thin.
- **[doc-audit](skills/engineering/doc-audit/SKILL.md)** — after any code change, audits the documentation surface it touched (docstrings, comments, READMEs, docs, examples) and rewrites stale passages in present tense describing current state.

### Research 

`/plugin install greerviau-research@greerviau`

- **[lit-research](skills/research/lit-research/SKILL.md)** — scientific-literature tooling backed by OpenAlex, Semantic Scholar, PubMed, and Crossref: search, citation-graph snowballing, bibliography reference-checks, and an orchestrated literature-review workflow, with every citation grounded in real API records.

### Personal 

`/plugin install greerviau-personal@greerviau`

- **[opinions](skills/personal/opinions/SKILL.md)** — consults `~/OPINIONS.md` before making subjective calls the user has likely already formed a view on, and offers to record new opinions the user states mid-task.

## Contributing

Maintainer dev scripts live in [`scripts/`](scripts):

- `scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` so local edits are live.
- `scripts/list-skills.sh` lists every skill in the repo.

Add a new skill by creating `skills/<category>/<name>/SKILL.md`, then register it in both `package.json` (the `skills` array, for the skills.sh installer) and, if it's a new category, `.claude-plugin/marketplace.json` (a new plugin entry).

## License

MIT — see [LICENSE](LICENSE).
