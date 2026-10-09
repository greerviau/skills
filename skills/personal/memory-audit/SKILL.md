---
name: memory-audit
description: Audit agent memory for duplicates, contradictions, stale claims, and index drift, then apply the user's verdicts.
disable-model-invocation: true
---

# memory-audit

Run `/memory-audit` to audit the agent's saved memories.

Memory accumulates without review. Facts are saved once and never revisited, duplicates pile up across projects, reversed decisions leave the old memory behind, and rules that later moved into `CLAUDE.md` remain as dead weight.
This skill puts a human in front of the whole corpus and applies their verdicts.

Run it only when the user asks. Never audit memory as a side effect of another task, and never delete a memory outside this skill.

The user decides what stays. Every judgment call goes to them, and anything ambiguous defaults to keep.

## How memory is stored

One directory per project: `~/.claude/projects/<slug>/memory/`, where `<slug>` is the project's resolved working directory with every character that is not a letter or digit replaced by `-` (`/Users/me/.worktrees/fix_v2` becomes `-Users-me--worktrees-fix-v2`).
Only the directory matching a session's working directory is loaded, so the same fact often exists in several projects, and a fact filed under one project is invisible to the others.

Each memory is one file holding one fact:

```markdown
---
name: <kebab-case slug, matching the filename>
description: <one-line summary, used to decide relevance during recall>
metadata:
  type: user | feedback | project | reference
---

<the fact. feedback and project also carry **Why:** and **How to apply:** lines.
[[other-memory-name]] links relatives.>
```

`MEMORY.md` in the same directory is the index loaded every session: one `- [Title](file.md) — hook` line per memory, with no content of its own.

## Procedure

### 1. Scan

```bash
uv run memory_scan.py --backup
```

Run it from the `scripts/` directory next to this file. The only prerequisite is [uv](https://docs.astral.sh/uv/).
Add `--json <scratch-path>` for the same findings as structured data.
`--backup` first snapshots every scanned directory under `~/.claude/memory-audit-backups/<timestamp>/`. Memory is not version controlled, so this is the only way to recover a deletion. Tell the user the backup path.

Audit everything by default.
Narrow with `--project <path-or-slug>` (repeatable) when the user asks for one project, and say what you skipped.

The report lists the roster (every memory with its type, age, and description), then index defects, file defects, overlapping pairs, and memories already stated in a `CLAUDE.md` the session loads anyway.
Findings are candidates, not verdicts.

### 2. Fix mechanical defects yourself

Do not interview for these:

- Index drift: a memory missing from `MEMORY.md`, an index line pointing at a deleted file, or content that belongs in a memory file sitting in the index.
- `name` not matching the filename, a missing `description`, or a missing or invalid `type` where the body makes the answer obvious.
- A missing `**Why:**` or `**How to apply:**` line that the body already answers in prose.
- Dangling `[[links]]`: repoint to the memory that absorbed the target, or drop the link.
- A relative date, when the memory's content or `modified:` timestamp fixes the anchor.

When a fix needs a fact you lack, it becomes an interview item.

### 3. Check flagged memories against reality

Read every flagged memory and check its claim before putting it to the user.
A memory that names a file, function, flag, or command is testable, so look.
`path-unverified` findings are guesses from backtick contents and include repo slugs and package names. Confirm each before calling a memory wrong.

### 4. Build the interview list

A memory earns a question only when there is a case against it.
For healthy memories, report only a count.

| Case | What it looks like | Recommend |
| --- | --- | --- |
| Wrong | contradicts what the code, config, or repo now does; the decision was reversed | delete, or edit to the current fact |
| Contradicts a sibling | two memories give conflicting instructions (an overlapping pair is often this, not a duplicate) | keep one, delete the other |
| Duplicate | same fact in several projects, or two files on one subject | keep one, and consider moving it somewhere every project sees |
| Already a standing rule | restated in `CLAUDE.md`, `~/OPINIONS.md`, or a skill the session loads anyway | delete |
| Spent | a project memory for work that shipped, a reference that is dead | delete |
| Inert | too vague to change behavior, or records what the repo and git history already say | delete |
| Misfiled | wrong `type`, or a fact that applies everywhere living in one project | move |
| Overgrown | one file carrying several facts | split |

### 5. Interview

Use `AskUserQuestion`, at most four memories per round, one memory per question.

Quote the memory's claim in the question. The user is not looking at the files, and a slug does not say what they are ruling on.
State the case against the memory in the description instead of a neutral summary, and put the recommended option first.
Offer `Keep`, `Delete`, `Edit` (say what the edit would be), and `Move` (name the destination) as they apply.

Work down the list in rounds.
Follow the user into chat if they would rather talk through a memory than pick an option.

### 6. Apply the verdicts

- Delete: remove the file and its `MEMORY.md` line.
- Edit: change the fact, not the subject. Tighten wording, correct errors, convert relative dates to absolute, and fix the type. Do not add a claim the user never made.
- Move between projects: write the file into the destination `memory/` directory, add its index line, then delete the original and its line. A fact that applies to every project belongs in `CLAUDE.md` or `~/OPINIONS.md`, so offer that destination instead of copying it into ten memory directories.
- Split: one fact per file, each with its own frontmatter and index line, cross-linked with `[[name]]`.
- Update the description whenever you edit a body, because recall matches on it.

### 7. Re-scan and report

Re-run the scan without `--backup` and confirm it is clean.
Report per project how many memories were kept, edited, moved, and deleted, and what the corpus now holds.
Name any finding the user deferred so the next audit starts there.

### 8. Ask what is missing

Ask one question: what do they repeat to agents that no memory covers?
Write the answer as a new memory in the project it belongs to, following the file shape above, and add its index line.

## Notes

- A memory exists to change what an agent does. One that would not change any decision costs context and attention, so a falling count is a good outcome.
- Never re-add a memory the user deleted in an earlier audit. If the scan finds it back, tell them.
- An empty memory directory is a finding, not an error: nothing has been saved for that project.
- A slug that resolves to no directory on disk means the project moved or is gone. Its memories are unreachable, so surface them for deletion or a move to the project's new path.
