---
name: retro
description: Review a finished coding session for what went wrong and propose fixes to the global standards, review's checks, the skills, or the global CLAUDE.md.
disable-model-invocation: true
---

# retro

Run `/retro` after a session that went worse than it should have.
It reads the session's record, finds the moments the agent struggled, and proposes changes that stop the same failure in any repo.
It only proposes. Nothing changes until the user picks a candidate.

## Targets

Every candidate changes one of these:

- `skills/engineering/standards/CODING-STANDARDS.md`, for a judgement-call rule about code.
- `skills/engineering/standards/SKILL.md`, for a rule about prose, artifacts, or workflow.
- The mechanical-check table in `skills/engineering/review/SKILL.md`, for a rule a grep can check.
- Any other skill in the skills repo, when its procedure caused the failure.
- The user's global `~/.claude/CLAUDE.md`, to delete an instruction that changes nothing or move a coding rule into `CODING-STANDARDS.md`.

Never propose a change to the project repo the session worked in: no per-repo standards file, `AGENTS.md` pointer, linter rule, or memory entry.
A finding that cannot be stated as a rule that holds in a repo the agent has never seen is dropped.

Edit the skills repo's source checkout, found by its `origin` remote (`greerviau/skills`), never the installed copies under `~/.claude/plugins/` or `~/.agents/skills/`.
Ask for the checkout's path when none is found.

## Procedure

1. Choose the session. The default is the current one: its conversation is in context, and its log holds the tool calls and results that context has summarized.
   Logs are `~/.claude/projects/<slug>/<session-id>.jsonl`, where the slug is the session's starting directory with every character that is not a letter or digit replaced by `-`.
   The current session's log is the most recently modified file in that directory. Subagent transcripts are in `<session-id>/subagents/`.
   Each line is a JSON record. Records with `type` of `user` or `assistant` carry `message.content`, which holds text, `tool_use`, and `tool_result` blocks.
   This lists the user's prompts and every failed tool call with its position:

   ```bash
   python3 - <session-log> <<'EOF'
   import json, sys
   for number, line in enumerate(open(sys.argv[1]), 1):
       record = json.loads(line)
       content = (record.get("message") or {}).get("content") or []
       blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
       for block in blocks:
           if record.get("type") == "user" and block.get("type") == "text":
               print(f"{number} prompt: {block['text'][:200]!r}")
           if block.get("type") == "tool_result" and block.get("is_error"):
               print(f"{number} tool error: {str(block.get('content'))[:200]!r}")
   EOF
   ```

2. Find the moments the agent struggled. Read for:
   - A defect that review (the `review` skill, a self-review step, or the user) caught late or never caught.
   - A mistake a grep could have caught.
   - A skill step that was skipped or misread, a skill that should have run and did not, or a skill instruction that led the agent wrong.
   - A user correction, a repeated request, or rejected work.
   - Many tool calls spent finding one fact.
   - A tool call whose output was far larger than what the agent used.
   - A steering instruction, in a skill or the global `CLAUDE.md`, that the session shows changing nothing.

   Each moment is cited by its log line number and a short quote. A candidate without a cited moment is not a candidate.

3. Route each moment to one target.
   - A fixed pattern a grep can find goes to `review`'s mechanical-check table as a row with its grep.
   - A judgement call goes to `CODING-STANDARDS.md` for code, or `standards/SKILL.md` for prose and workflow.
   - A failure a skill's procedure caused goes to that skill.
   - A moment specific to the session's repo is dropped. Before dropping it, look for a general rule behind it: twenty calls spent finding one repo's entry point becomes a `dev-workflow` step to read the README and build manifest before searching.

   Read the target before writing a rule. When an existing rule already covers the moment, the candidate clarifies that rule or the step that should have applied it, and adds no second rule.

4. Look for deletions. For each standards rule or skill instruction the session exercised, check whether it fired on correct work or changed nothing. Propose deleting each one that did.

5. Report the candidates ranked by severity: how much the failure cost in the session, and how often it will recur.
   For each, give the cited moment, the target file, the exact text to add, change, or delete, and the reason it holds in any repo.
   End with a "Dropped" list, one line per dropped moment with the reason.
   The report is human-facing (*Artifact audience* in `standards`).

6. Ask the user which candidates to apply.
   When no user can answer, stop after the report. `retro` never applies its own candidates.

7. Apply the accepted candidates.
   Changes to the skills repo land through an issue, a branch, and a PR (the `dev-workflow` skill, if you use it). Edit the global `CLAUDE.md` directly after showing the user the diff.
   Tell the user that installed skills pick up a merged change only after the plugin or skill install is updated.

## Credits

Adapted from `retro` in [mattpocock/skills](https://github.com/mattpocock/skills), Copyright (c) 2026 Matt Pocock, used under the [MIT License](https://github.com/mattpocock/skills/blob/main/LICENSE).
