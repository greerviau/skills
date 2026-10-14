---
name: retro
description: Review a finished coding session for lessons that should update the user's coding standards or shipped engineering skills.
disable-model-invocation: true
---

# retro

Run `/retro` after a session that went worse than it should have.
It reads the session record and proposes changes to the user's evolving coding standards or to a shipped skill when the lesson applies across repos.
It applies only the candidates the user accepts.

## Targets

Route each candidate to one of these targets:

- `$HOME/CODING-STANDARDS.md`, for a user-specific judgment-call rule about code.
- `skills/engineering/standards/CODING-STANDARDS.md`, for a coding rule that should apply to every user and repo.
- `skills/engineering/standards/SKILL.md`, for a rule about prose, artifacts, or workflow.
- The mechanical-check table in `skills/engineering/review/SKILL.md`, for a rule a grep can check.
- Any other skill in the skills repo, when its procedure caused the failure.

The shipped `skills/engineering/standards/CODING-STANDARDS.md` is the starter set, not the user's editable standards file.
When the personal file does not exist and the user accepts a coding-rule candidate, copy the starter file to `$HOME/CODING-STANDARDS.md` before applying the candidate.
Keep personal coding rules in that file; do not add repo-specific rules to the global personal file.
Drop a repo-specific finding unless it exposes a shared skill failure.
Route a lesson that should change shared skill behavior to the relevant skill source and publish that change through an issue and PR.

Edit the skills repo's source checkout, never the installed copies under `~/.claude/plugins/`, `~/.claude/skills/`, or `~/.agents/skills/`.
The checkout is the directory where `git remote get-url origin` names `greerviau/skills`. Check the session's working directory and its parent, and ask for the path when neither matches.

## Procedure

1. Choose the session.
   When `/retro` is given a session id or a log path, use that log.
   Otherwise use the current session: its conversation is in context, and its log holds the tool calls and results that context has summarized.
   Find a log by its session id. Claude Code exports the current one as `CLAUDE_CODE_SESSION_ID`:

   ```bash
   find ~/.claude/projects -name "${CLAUDE_CODE_SESSION_ID}.jsonl"
   ```

   Subagent transcripts are in `<session-id>/subagents/` next to the log.
   Each line of a log is a JSON record. Records with `type` of `user` or `assistant` carry `message.content`, which holds text, `tool_use`, and `tool_result` blocks.
   A tool result too large for the conversation appears as `<persisted-output>` with its size, and its full text is in `<session-id>/tool-results/`.
   This lists the user's prompts and interruptions, every failed tool call, and every oversized result, each with its log line number:

   ```bash
   python3 - <session-log> <<'EOF'
   import json, sys
   for number, line in enumerate(open(sys.argv[1]), 1):
       record = json.loads(line)
       content = (record.get("message") or {}).get("content") or []
       blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
       for block in blocks:
           text = block.get("text", "")
           if record.get("type") == "user" and text and not record.get("isMeta"):
               if text.startswith("[Request interrupted"):
                   print(f"{number} interrupted")
               elif not text.startswith(("<local-command", "<command-", "<task-notification")):
                   print(f"{number} prompt: {text[:200]!r}")
           if block.get("type") == "tool_result":
               result = str(block.get("content"))
               if block.get("is_error"):
                   print(f"{number} tool error: {result[:200]!r}")
               elif "<persisted-output>" in result:
                   print(f"{number} oversized result: {result.splitlines()[1][:120]!r}")
   EOF
   ```

2. Find the moments the agent struggled. Read for:
   - A defect that review (the `review` skill, a self-review step, or the user) caught late or never caught.
   - A mistake a grep could have caught.
   - A skill step that was skipped or misread, a skill that should have run and did not, or a skill instruction that led the agent wrong.
   - A user correction, a repeated request, or rejected work.
   - Many tool calls spent finding one fact.
   - A tool call whose output was far larger than what the agent used.
   - A shared skill instruction that the session shows changing nothing.

   Each moment is cited by its log line number and a short quote. A candidate without a cited moment is not a candidate.

3. Route each moment to one target.
   - A fixed pattern a grep can find goes to `review`'s mechanical-check table as a row with its grep.
   - A user-specific judgment call goes to `$HOME/CODING-STANDARDS.md` for code.
   - A coding rule that should apply to every user and repo goes to the shipped `CODING-STANDARDS.md`.
   - A shared judgment call about prose or workflow goes to `standards/SKILL.md`.
   - A lesson that applies across repos and changes a skill's procedure goes to that skill's source in the skills checkout.
   - A failure a skill's procedure caused goes to that skill.
   - A moment specific to the session's repo is dropped. Before dropping it, look for a general rule behind it: twenty calls spent finding one repo's entry point becomes a `dev-workflow` step to read the README and build manifest before searching.

   Read the target before writing a rule. When an existing rule already covers the moment, the candidate clarifies that rule or the step that should have applied it, and adds no second rule.

4. Look for deletions.
   For each coding rule or skill instruction the session exercised, check whether it fired on correct work or changed nothing, and propose deleting each one that did.
   For each shared rule in the skills checkout older than a month (`git log --diff-filter=A -S '<rule text>'` gives its date), search the logs since that date for a finding that cites it:
   `grep -l '<rule text>' ~/.claude/projects/*/*.jsonl`. A rule no session has cited since it was added is a deletion candidate.

5. Report the candidates ranked by severity: how much the failure cost in the session, and how often it will recur.
   For each, give the cited moment, the target file, the exact text to add, change, or delete, and the reason it holds in any repo.
   End with a "Dropped" list, one line per dropped moment with the reason.
   The report is human-facing (*Artifact audience* in `standards`).

6. Ask the user which candidates to apply.
   When no user can answer, stop after the report. `retro` never applies its own candidates.

7. Apply accepted candidates.
   Apply personal coding-rule changes to `$HOME/CODING-STANDARDS.md`; show the diff.
   Make shared skill changes in the skills checkout on a branch, then open a PR that contains them.
   Do not leave an accepted shared skill change only in a local checkout.
   Tell the user that installed skills pick up a merged change only after the plugin or skill install is updated.
