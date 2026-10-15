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

- [spec](skills/engineering/spec/SKILL.md) - turns a raw request into a reviewed spec. It interviews the user, explores the code, researches external behavior, checks each decision against the code, extends the repo's `UBIQUITOUS-LANGUAGE.md`, and writes a short human-facing spec whose work items become tickets.
- [spec-to-tickets](skills/engineering/spec-to-tickets/SKILL.md) - turns a reviewed spec into GitHub Issues, choosing a single-issue, flat, or parent-with-sub-issues shape from the spec's scope.
- [handoff](skills/engineering/handoff/SKILL.md) - compacts the current conversation into a handoff document for another agent.
- [retro](skills/engineering/retro/SKILL.md) - reads a finished session's log and proposes updates to the repo's or the global `CODING-STANDARDS.md`, or changes to a skill.

#### Model-invoked

- [implement](skills/engineering/implement/SKILL.md) - implements a prompt, issue, ticket, or spec in an isolated worktree, builds it test-first, reviews the diff, opens a PR, and finishes when CI passes.
- [tdd](skills/engineering/tdd/SKILL.md) - the test-first loop every behavior change runs: pick the seam, write the failing test, confirm it fails for the right reason, write the minimum code to pass, and refactor under green.
- [diagnose](skills/engineering/diagnose/SKILL.md) - reproduces a failure, narrows to the root cause with evidence, and reports the cause before any fix.
- [prototype](skills/engineering/prototype/SKILL.md) - answers a design or feasibility question with a throwaway spike whose source is discarded.
- [open-issue](skills/engineering/open-issue/SKILL.md) - checks for duplicates, honors the repo's issue template, writes a descriptive title and a short problem, reproduction, and acceptance-criteria body, and labels from `gh label list`.
- [open-pr](skills/engineering/open-pr/SKILL.md) - writes the `feat(...)` or `fix(...)` title and an evergreen body, then opens the PR.
- [review](skills/engineering/review/SKILL.md) - reviews a diff, branch, or PR for correctness, tests, flakiness, repo coding standards, structure, and conformance to the originating spec or issue.
- [refactor](skills/engineering/refactor/SKILL.md) - improves code structure without changing behavior, guarded by an unchanged test suite.
- [merge-conflict](skills/engineering/merge-conflict/SKILL.md) - resolves merge and rebase conflicts from both sides' intent, reruns the repository checks, and completes the operation.
- [doc-audit](skills/engineering/doc-audit/SKILL.md) - audits the documentation a change touched, rewrites stale passages in present tense, and checks the prose for plain language.
- [mermaid](skills/engineering/mermaid/SKILL.md) - the draft, render, critique, refine loop for mermaid diagrams.

Skills write specs, plans, analyses, and glossaries into the repo by default (`docs/plans/`, `docs/analysis/`, `docs/UBIQUITOUS-LANGUAGE.md`).
Tell the agent, or put a line in the repo's agent instructions (`AGENTS.md` or equivalent), not to write documents to the repo, and they go to the OS temporary directory instead.

Coding rules live in `<repo>/CODING-STANDARDS.md` for one repo and in `~/CODING-STANDARDS.md` (referenced from your global agent instructions) for every repo. `retro` maintains both.

### Research

`/plugin install greerviau-research@greerviau`

#### Model-invoked

- [lit-research](skills/research/lit-research/SKILL.md) - literature search, citation-graph snowballing, bibliography reference checks, and a literature-review workflow backed by OpenAlex, Semantic Scholar, PubMed, and Crossref, with every citation taken from API records.

### Personal

`/plugin install greerviau-personal@greerviau`

#### User-invoked

- [doc-review](skills/personal/doc-review/SKILL.md) - renders Markdown, text, HTML, PDF, or DOCX in the browser for inline comments, then returns each comment with its source location and quoted text so the document can be revised.

## Contributing

Maintainer scripts are in [`scripts/`](scripts):

- `scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` so local edits take effect immediately.
- `scripts/list-skills.sh` lists every skill in the repo.

Add a skill by creating `skills/<category>/<name>/SKILL.md`, then register it in `package.json` (the `skills` array, for the skills.sh installer) and, for a new category, in `.claude-plugin/marketplace.json` (a new plugin entry).
See [AGENTS.md](AGENTS.md) for authoring rules.

## License

MIT, see [LICENSE](LICENSE).
