# skills

Reusable agent skills for engineering and scientific research. Each skill is a self-contained, plain-markdown procedure doc with a small YAML frontmatter header.

## Installation

### npx

```bash
npx skills@latest add
```

Symlinks every skill in this repo into `~/.claude/skills`. Pass a target directory to install elsewhere:

```bash
npx skills@latest add /path/to/other/skills/dir
```

### Claude Code plugin

This repo is also a Claude Code plugin, registered as `greerviau-skills` — `.claude-plugin/plugin.json` declares it, and every folder under `skills/` is auto-discovered as a skill.

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

## License

MIT — see [LICENSE](LICENSE).
