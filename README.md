# skills

Reusable agent skills for engineering and scientific research. Each skill is a self-contained, plain-markdown procedure doc with a small YAML frontmatter header.

## Installation

Skills are independently installable — install only the ones you want (see the [reference](#skills-reference) below).

### npx

Install every skill:

```bash
npx skills@latest add
```

Or just the ones you want:

```bash
npx skills@latest add spec doc-audit
```

Skills are symlinked into `~/.claude/skills`. Pass `--target` to install elsewhere, and use `list` to see what's available:

```bash
npx skills@latest add spec --target /path/to/other/skills/dir
npx skills@latest list
```

### Claude Code plugin

This repo is also a Claude Code plugin, registered as `greerviau-skills` — `.claude-plugin/plugin.json` declares it, and every folder under `skills/` is auto-discovered as a skill. Note the plugin form installs all skills; use the npx installer for per-skill installs.

```bash
claude plugin install github:greerviau/skills
# or, from a local clone:
claude plugin install ./skills
```

```bash
claude plugin list                         # confirm it's installed
claude plugin update greerviau-skills      # pull in new/changed skills later
claude plugin uninstall greerviau-skills   # remove it
```

## Skills reference

- **[spec](skills/spec/SKILL.md)** — turns a raw request into a reviewed plan of action: interviews the user to pin down requirements and terminology, explores the code to discover scope, maintains the repo's ubiquitous-language glossary, and writes the plan to a markdown file for review before any building starts.
- **[dev-workflow](skills/dev-workflow/SKILL.md)** — the end-to-end development loop for a GitHub repo: isolated worktree, staged commits, local validation, an evergreen PR, watching CI to green, and cleanup.
- **[doc-audit](skills/doc-audit/SKILL.md)** — after any code change, audits the documentation surface it touched (docstrings, comments, READMEs, docs, examples) and rewrites stale passages in present tense describing current state.
- **[opinions](skills/opinions/SKILL.md)** — consults `~/OPINIONS.md` before making subjective calls the user has likely already formed a view on, and offers to record new opinions the user states mid-task.

## License

MIT — see [LICENSE](LICENSE).
