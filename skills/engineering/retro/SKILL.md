---
name: retro
description: Use when the user asks to analyze a coding session for lessons to incorporate into checks, coding standards, or skills.
---

# retro

Read the session record when the user asks for lessons from a coding session.
Propose changes and apply only the candidates the user accepts.

## Targets

Route each candidate to one target:

- A **check** in the repo where the mistake happened: a structural change that removes the wrong path, a type that rejects the bad state, a lint or CI rule, or a test.
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

3. Route each moment to one target. For a coding mistake, take the first level below that works:
   1. Remove the wrong path: give each piece of state one owner and each task one supported way, hide internals so the wrong import fails, replace hand-synced lists with one source, and delete old code an agent would copy.
   2. Make the bad state fail to typecheck.
   3. Add a lint or CI rule whose error names the file, type, or function to use instead. When the pattern is already common, fail only on new occurrences.
   4. Add a test at the behavior's real entry point.
   5. Write a rule in a `CODING-STANDARDS.md` or a skill, only for a judgment call no check can decide.

   Read the target first. When an existing written rule already covers the moment, move it to the first check level that works, and when no level works, clarify the rule instead of adding a second one.
   Drop a one-off finding about the changed code.

4. Look for deletions. For each rule or skill instruction the session exercised, check whether it fired on correct work or changed nothing, and propose deleting it. Propose deleting a written rule that a check now enforces.

5. Report candidates most severe first, where severity is the cost of the failure in the session and how often it will recur. For each, give the cited moment, the target, the exact text or code to add, change, or delete, and why it applies there. For a written rule about code, say why each check level fails. End with a "Dropped" list, one line per dropped moment with the reason.

6. Ask which candidates to apply. When no user can answer, stop after the report. Never apply your own candidates.

7. Apply the accepted candidates and show the diff.
   Before keeping a check, reproduce the session's mistake on a scratch copy and show that the command CI runs fails on it.
   A repo-specific change belongs in that repo's PR: use its open PR when one covers the session, otherwise open one.
   A skill change goes on a branch in the skills checkout with its own PR, and reaches installed copies only after the plugin is updated.
