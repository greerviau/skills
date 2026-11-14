---
name: panel
description: Use only when the user explicitly asks for a panel of judges, for example "use the panel", "run this past the panel", or "until the panel scores 8". Do not use for an ordinary review, critique, or quality request that does not name a panel.
---

# panel

Do the requested work, then have a **panel** of independent **judges**, each a different model, score it from 1 to 10.
Revise until every judge's score is at or above the **threshold**, or until the loop stops.
A judge never sees the threshold, a round number, an earlier score or finding, another judge's output, or any sign that the work was revised.
You never read a judge's raw review.
You read the scores and the consolidated feedback.

A **round** is one scoring by every judge.
The **round limit** caps the number of rounds.

## 1. Set up the panel

Take the judges, the threshold, and the round limit from the request.
When any of them is missing, ask for all missing values in one question before you start the work, and offer these defaults:

- Judges: three models from three different providers, excluding your own model.
- Threshold: 8.
- Round limit: 3.

When no user can answer, use the defaults and list them in the final report.

A judge is a model plus a launch method that can run it (see step 4).
Before round 1, send each judge a one-line prompt through its launch method and confirm that it answers.
When a judge does not answer, tell the user and ask for a replacement, and do not substitute a model yourself.
When no user can answer, stop and report the judge that failed.

Create the panel directory outside the work tree, and give each judge a short id (`j1`, `j2`, ...):

```bash
panel=$(mktemp -d "${TMPDIR:-/tmp}/panel.XXXXXX")
mkdir -p "$panel/ledger"
printf 'j1\t<model>\t<launch method>\n' >> "$panel/judges.tsv"   # one line per judge
```

For work in a Git repository, record the base once.
Use the base the task names, or else the merge base with the default branch:

```bash
base=$(git merge-base HEAD origin/<default-branch>)
```

## 2. Freeze the judge prompt

For each judge, write `$panel/judges/<id>/prompt.md` from [references/judge-prompt.md](references/judge-prompt.md), and do not change it after that.
Every round sends each judge the same file, byte for byte.

Fill the placeholders:

- `{{TASK}}`: the user's request, without the panel instructions (the judge list, threshold, and round limit).
- `{{WORK}}`: what the judge reviews and where, with `{{WORK_DIR}}` set to `$panel/judges/<id>/work`.
  For Git work, name `$base` (as a commit hash) and tell the judge to review `git diff <base>` in the work directory.
  For visual work, name each screenshot file and the viewport width it shows.
- `{{REVIEW_FILE}}`: `$panel/judges/<id>/review.md`.

Do not put any of these in the prompt: the threshold, the round limit, your model, scores, findings, or words that imply an earlier version.

## 3. Do the work

Do the requested task.
When the work already exists (for example, "run the panel on this PR"), go to step 4.

## 4. Run a round

Start at round 1.
Snapshot the current work into each judge's work directory, replacing the previous snapshot.

For Git work, build one commit on `$base` from the working tree with a temporary index, so the user's index stays unchanged and the judge sees no revision history:

```bash
export GIT_INDEX_FILE="$panel/index"
git read-tree HEAD && git add -A
snap=$(git commit-tree "$(git write-tree)" -p "$base" -m "Proposed change")
unset GIT_INDEX_FILE
for id in $(cut -f1 "$panel/judges.tsv"); do
  git worktree remove --force "$panel/judges/$id/work" 2>/dev/null
  git worktree add --detach "$panel/judges/$id/work" "$snap"
done
```

For other work, delete each `work` directory and copy the artifact into it again.
For visual work, render the screenshots the prompt names into each `work` directory.

Launch every judge in parallel as a fresh session with its `prompt.md`.
Never resume or message a judge from an earlier round.
Use the first launch method that can run the judge's model:

- Your host's subagent or delegation tool, when it can select that model.
  Pass the contents of `prompt.md` as the task.
  The judge writes its review file and replies `done`.
- Codex CLI:

  ```bash
  codex exec --ephemeral --skip-git-repo-check -m "<model>" -s workspace-write \
    -c sandbox_workspace_write.network_access=true \
    -C "$panel/judges/<id>" - < "$panel/judges/<id>/prompt.md" > /dev/null 2>&1
  ```

- Claude Code CLI:

  ```bash
  (cd "$panel/judges/<id>" && claude -p --model "<model>" \
    --allowedTools "Read Grep Glob Bash Write" < prompt.md > /dev/null 2>&1)
  ```

- Another provider's CLI: run it non-interactively in `$panel/judges/<id>` with the model selected and its output discarded.

When all judges finish, read only the score lines:

```bash
for id in $(cut -f1 "$panel/judges.tsv"); do
  printf '%s\t%s\n' "$id" "$(grep -m1 -E '^SCORE: ([1-9]|10)$' "$panel/judges/$id/review.md")"
done
```

When a judge's score line is missing or malformed, relaunch that judge once as a fresh session.
When it fails again, stop and report the judge that failed.

Move each review into the ledger and append each score to `$panel/ledger/scores.tsv`:

```bash
mv "$panel/judges/<id>/review.md" "$panel/ledger/round-<n>-<id>.md"
printf '<n>\t<id>\t<score>\n' >> "$panel/ledger/scores.tsv"
```

## 5. Decide

Stop the loop at the first condition that holds:

- Every score is at or above the threshold. The panel passed.
- The round equals the round limit.
- From round 3 on, the lowest score is no higher than the lowest score two rounds earlier. The scores stalled.

When the panel passed, go to step 7.
When the loop stops for another reason, consolidate this round as in step 6, skip the revision, and go to step 7.
Otherwise go to step 6.

## 6. Consolidate and revise

Launch a fresh consolidator subagent with [references/consolidator-prompt.md](references/consolidator-prompt.md).
Any available model can consolidate.
Fill `{{REVIEW_FILES}}` with this round's ledger review paths, `{{PREVIOUS_FEEDBACK}}` with `$panel/ledger/feedback-round-<n-1>.md` or `none`, and `{{FEEDBACK_FILE}}` with `$panel/ledger/feedback-round-<n>.md`.

Check that the feedback file cites every finding id from this round, without reading the reviews:

```bash
for f in "$panel"/ledger/round-<n>-*.md; do
  id=$(basename "$f" .md); id=${id#round-<n>-}
  grep -oE '^F[0-9]+' "$f" | sed "s/^/$id./"
done | sort -u > "$panel/expected"
grep -oE '\bj[0-9]+\.F[0-9]+\b' "$panel/ledger/feedback-round-<n>.md" | sort -u > "$panel/cited"
comm -23 "$panel/expected" "$panel/cited"
```

When the check prints ids, relaunch the consolidator once and name the missing ids.
When ids are still missing, continue and list them in the final report.

Read the feedback file and the scores, then revise the work.
Fix every finding.
When you reject a finding, write its item number and your reason to `$panel/ledger/decisions-round-<n>.md`.
The judges never see these decisions.

For each item under Conflicts, pick one side and record the choice in the decisions file.
When a conflict is marked `repeat`, stop the loop and ask the user which side to take, then continue with their answer.
When no user can answer, stop and go to step 7.

Go to step 4 with the next round number.

## 7. Report

Report:

- The outcome: passed in round `<n>`, stopped at the round limit, stalled, stopped on a conflict, or stopped on a judge failure.
- A score table with one row per round and one column per judge, headed by the judge's model.
- The open items from the last feedback file, the rejected findings with reasons, the unresolved conflicts, and any finding ids the consolidator left out.
- The defaults you used when no user could answer.
- The panel directory path.

Remove the judge worktrees with `git worktree remove --force "$panel/judges/<id>/work"`, and keep the ledger.
