# Contributing

## Local development

Link every skill in this checkout into `~/.agents/skills` (Codex, Pi, OpenCode) and `~/.claude/skills` (Claude Code):

```bash
bash scripts/link-skills.sh
```

Uninstall any skills.sh or plugin copies of these skills first, since the script refuses to overwrite them.
Edits take effect through the links.
After adding, renaming, or removing a skill, rerun the script and restart the harness.

Test the linker with `node --test scripts/tests/link-skills.test.cjs`.
List every skill with `bash scripts/list-skills.sh`.

## Adding a skill

1. Create `skills/<category>/<name>/SKILL.md`.
2. Add it to the `skills` array in `package.json`.
3. For a new category, add the category directory to the plugin's `skills` array in `.claude-plugin/marketplace.json`.
4. Add `agents/openai.yaml` when the skill needs Codex invocation or interface metadata.

See [AGENTS.md](AGENTS.md) for authoring rules.
