# skills

Reusable agent skills for engineering and scientific research.
Each skill is a self-contained, plain-markdown procedure doc with a small YAML frontmatter header.

Skills are organized into three categories, `engineering`, `research`, and `personal`, and ship as three separately installable Claude Code plugins so you can take the categories you want and skip the rest.

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

```bash
claude plugin marketplace add greerviau/skills
claude plugin install greerviau-engineering@greerviau   # engineering skills
claude plugin install greerviau-research@greerviau       # research skills
claude plugin install greerviau-personal@greerviau       # personal skills
```

Each is optional and independent - install any subset of the categories.
Manage them the usual way:

```bash
claude plugin list                                        # confirm what's installed
claude plugin marketplace update greerviau                # pull in new/changed skills later
claude plugin uninstall greerviau-research@greerviau      # remove a category
```

Two ways to install, two philosophies:

- **[skills.sh](https://skills.sh/greerviau/skills)** copies the skills into your project so you can hack on them and make them your own.
- **The plugins** keep them as read-only, always-current bundles you don't edit - best when you just want the set to work and follow along as it evolves.

## Skills reference

### Engineering

- **[spec](skills/engineering/spec/SKILL.md)** — turns a raw request into a reviewed plan of action: interviews the user to pin down requirements and terminology, explores the code to discover scope, maintains the repo's ubiquitous-language glossary, and writes the plan to a markdown file for review before any building starts.
- **[dev-workflow](skills/engineering/dev-workflow/SKILL.md)** — the end-to-end development loop for a GitHub repo: isolated worktree, staged commits, local validation, an evergreen PR, watching CI to green, and cleanup.
- **[doc-audit](skills/engineering/doc-audit/SKILL.md)** — after any code change, audits the documentation surface it touched (docstrings, comments, READMEs, docs, examples) and rewrites stale passages in present tense describing current state.

### Research

- **[lit-research](skills/research/lit-research/SKILL.md)** — scientific-literature tooling backed by OpenAlex, Semantic Scholar, PubMed, and Crossref: search, citation-graph snowballing, bibliography reference-checks, and an orchestrated literature-review workflow, with every citation grounded in real API records.

### Personal

- **[opinions](skills/personal/opinions/SKILL.md)** — consults `~/OPINIONS.md` before making subjective calls the user has likely already formed a view on, and offers to record new opinions the user states mid-task.

## Contributing

Maintainer dev scripts live in [`scripts/`](scripts):

- `scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` so local edits are live.
- `scripts/list-skills.sh` lists every skill in the repo.

Add a new skill by creating `skills/<category>/<name>/SKILL.md`, then register it in both `package.json` (the `skills` array, for the skills.sh installer) and, if it's a new category, `.claude-plugin/marketplace.json` (a new plugin entry).

## License

MIT — see [LICENSE](LICENSE).
