---
name: retro
description: Review a finished coding session for lessons that should update coding standards or skills.
disable-model-invocation: true
---

# retro

Invoke `/retro` in Claude Code or `$retro` in Codex after a session that went worse than it should have.
It reads the session record, proposes changes, and applies only the candidates the user accepts.

## Targets

Route each candidate to one file:

- `<repo-root>/CODING-STANDARDS.md`, for a coding rule specific to the current repo. Create the file when it does not exist.
- `~/CODING-STANDARDS.md`, for a coding rule that applies in every repo. Create the file when it does not exist, and add a line to the user's global agent instructions that points agents at it.
- The skill whose procedure caused the failure or should have prevented it, in the skills repo's source checkout. Locate it as the directory where `git remote get-url origin` names `greerviau/skills`, checking the session's working directory and its parent, and ask for the path when neither matches. Never edit an installed copy.

Resolve the repo root with `git rev-parse --show-toplevel`.
When the user or the repo's agent instructions (`AGENTS.md` or equivalent) say not to write documents to the repo, send repo-specific rules to `~/CODING-STANDARDS.md` or to the Git common directory (`git rev-parse --path-format=absolute --git-common-dir`) at `skills/CODING-STANDARDS.md`, and tell the user the rule stays local.

## Procedure

1. Choose the session: the one the user names by id or transcript path, otherwise the current conversation. Find the transcript the agent harness keeps for it, and ask the user for the path when you cannot locate it.
   `scripts/session_events.py <transcript>` reads a JSONL transcript whose records carry `message.content` blocks of text, `tool_use`, and `tool_result`. It lists the user's prompts and interruptions, every failed tool call, and every oversized result with its line number. Adapt it for a transcript in another format.

2. Find the moments the agent struggled:
   - A defect that review or the user caught late or never caught.
   - A mistake a grep could have caught.
   - A skill step that was skipped or misread, a skill that should have run and did not, or an instruction that led the agent wrong.
   - A user correction, a repeated request, or rejected work.
   - Many tool calls spent finding one fact, or a tool result far larger than what the agent used.

   Cite each moment by log line number and a short quote. A candidate without a cited moment is dropped.

3. Route each moment to one target. Read the target first. When an existing rule already covers the moment, the candidate clarifies that rule and adds no second one. Drop a one-off finding about the changed code.

4. Look for deletions. For each rule or skill instruction the session exercised, check whether it fired on correct work or changed nothing, and propose deleting it.

5. Report candidates most severe first, where severity is the cost of the failure in the session and how often it will recur. For each, give the cited moment, the target file, the exact text to add, change, or delete, and why it applies there. End with a "Dropped" list, one line per dropped moment with the reason.

6. Ask which candidates to apply. When no user can answer, stop after the report. Never apply your own candidates.

7. Apply the accepted candidates and show the diff.
   A repo-specific change belongs in that repo's PR: use its open PR when one covers the session, otherwise open one.
   A skill change goes on a branch in the skills checkout with its own PR, and reaches installed copies only after the plugin is updated.
