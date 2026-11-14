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
When any of them is missing, ask for all missing values in one question before you start the work, offering the defaults below. When no user can answer, use the defaults and list them in the final report.

- Judges: three models from three different providers, excluding your own model.
- Threshold: 8.
- Round limit: 3.

A judge is a model plus a launch method that can run it (see step 4).
Before round 1, send each judge a one-line prompt through its launch method and confirm that it answers.
When a judge does not answer, tell the user and ask for a replacement, and do not substitute a model yourself. When no user can answer, stop and report the judge that failed.

Create the ledger and each judge directory with separate `mktemp -d` calls.
The judge prompt sets the read boundary, and these commands do not restrict filesystem reads.
Give each judge a short id (`j1`, `j2`, ...) and add one line per judge to `judges.tsv`:

```bash
ledger=$(mktemp -d)
printf 'j1\t<model>\t<launch method>\t%s\n' "$(mktemp -d)" >> "$ledger/judges.tsv"
```

For work in a Git repository, record the starting point once.
Use the base the task names, or else the merge base with the default branch:

```bash
base=$(git merge-base HEAD origin/<default-branch>)
```

## 2. Freeze the judge prompt

For each judge, write `<judge dir>/prompt.md` from [references/judge-prompt.md](references/judge-prompt.md), and do not change it after that.
Every round sends each judge the same file, byte for byte.

Fill the placeholders:

- `{{TASK}}`: the user's request, without the panel instructions (the judge list, threshold, and round limit).
- `{{WORK}}`: what the judge reviews.
  For Git work, state that `git diff HEAD~1` in the work directory shows the proposed change against the starting point.
  For visual work, name each screenshot file and the viewport width it shows.
- `{{WORK_DIR}}`: `<judge dir>/work`.
- `{{REVIEW_FILE}}`: `<judge dir>/review.md`.

Do not put any of these in the prompt: the threshold, the round limit, your model, scores, findings, or words that imply an earlier version.

## 3. Do the work

Do the requested task.
When the work already exists (for example, "run the panel on this PR"), go to step 4.

## 4. Run a round

Start at round 1.
Replace each judge's `work` directory with a fresh snapshot of the current work.

For Git work, build the snapshot commit with a temporary index, so the user's index stays unchanged.
Then give each judge a new repository whose only history is the starting point and the snapshot, so the judge cannot see your branches or revision commits.
`snapshot` also deletes the judge's previous work directory and review:

```bash
export GIT_INDEX_FILE="$ledger/index"
git read-tree HEAD && git add -A
snap=$(git commit-tree "$(git write-tree)" -p "$base" -m "Proposed change")
unset GIT_INDEX_FILE
snapshot() {
  rm -rf "$1/work" "$1/review.md" "$ledger/export-index" && git init -q "$1/work"
  GIT_INDEX_FILE="$ledger/export-index" git --work-tree="$1/work" read-tree --reset -u "$base"
  git -C "$1/work" add -A
  git -C "$1/work" -c user.name=panel -c user.email=panel@localhost commit -q --allow-empty -m "Starting point"
  GIT_INDEX_FILE="$ledger/export-index" git --work-tree="$1/work" read-tree --reset -u "$snap"
  git -C "$1/work" add -A
  git -C "$1/work" -c user.name=panel -c user.email=panel@localhost commit -q --allow-empty -m "Proposed change"
}
while IFS=$'\t' read -r id model launch jdir; do snapshot "$jdir"; done < "$ledger/judges.tsv"
```

When the repository has submodules, copy each submodule's checked-out files into every `work` directory and commit them in the "Proposed change" commit.
For other work, delete each judge's `work` directory and `review.md`, and copy the artifact into `work` again.
For visual work, render the screenshots the prompt names into each `work` directory.

Launch every judge in parallel as a fresh session whose only input is its `prompt.md`.
Never resume or message a judge from an earlier round.
Use the first launch method that can run the judge's model:

- Your host's subagent or delegation tool, when it can select that model and start the session without your conversation history.
  Do not use a mode that forks or shares your context.
  Pass the contents of `prompt.md` as the whole task.
- Codex CLI:

  ```bash
  codex exec --ephemeral --skip-git-repo-check -m "<model>" -s workspace-write \
    -c sandbox_workspace_write.network_access=true \
    -C "<judge dir>" - < "<judge dir>/prompt.md" > /dev/null 2>&1
  ```

- Claude Code CLI:

  ```bash
  (cd "<judge dir>" && claude -p --model "<model>" \
    --allowedTools "Read Grep Glob Bash Write" < prompt.md > /dev/null 2>&1)
  ```

- Another provider's CLI: run it non-interactively in the judge directory with the model selected and its output discarded.

When all judges finish, check each review without reading it.
A valid review has a score on its first line and no other score line:

```bash
f="<judge dir>/review.md"
score=$(head -1 "$f" | grep -E '^SCORE: ([1-9]|10)$')
[ -n "$score" ] && [ "$(grep -c '^SCORE:' "$f")" -eq 1 ] && echo "${score#SCORE: }" || echo invalid
```

When a review is invalid, rebuild that judge's `work` directory from the same snapshot, then relaunch the judge once as a fresh session.
When it is invalid again, stop and report the judge that failed.

Move each review into the ledger and append its score to `$ledger/scores.tsv`:

```bash
mv "<judge dir>/review.md" "$ledger/round-<n>-<id>.md"
printf '<n>\t<id>\t<score>\n' >> "$ledger/scores.tsv"
```

## 5. Consolidate

Launch a fresh consolidator subagent, without your conversation history, with [references/consolidator-prompt.md](references/consolidator-prompt.md).
Any available model can consolidate.
Fill `{{REVIEW_FILES}}` with this round's ledger review paths, `{{PREVIOUS_FEEDBACK}}` with `$ledger/feedback-round-<n-1>.md` or `none`, and `{{FEEDBACK_FILE}}` with `$ledger/feedback-round-<n>.md`.

Check that the feedback file exists and cites every finding id from this round exactly once and no other id, without reading the reviews:

```bash
fb="$ledger/feedback-round-<n>.md"
test -s "$fb" || echo "feedback file missing"
for f in "$ledger"/round-<n>-*.md; do
  id=$(basename "$f" .md); id=${id#round-<n>-}
  grep -oE '^F[0-9]+' "$f" | sed "s/^/$id./"
done | sort -u > "$ledger/expected"
grep -oE '\bj[0-9]+\.F[0-9]+\b' "$fb" | sort > "$ledger/cited"
sort -u "$ledger/cited" | diff "$ledger/expected" -
uniq -d "$ledger/cited"
```

The check passes when the commands print nothing.
The `diff` lines marked `<` are missing ids, the lines marked `>` are ids that no review contains, and `uniq -d` prints ids cited more than once.
When the check fails, relaunch the consolidator once and name the failing ids or the missing file.
When the check fails again, stop and report a consolidation failure.

## 6. Decide

Stop the loop at the first condition that holds, and go to step 7:

- Every score is at or above the threshold. The panel passed.
- The round equals the round limit.

From round 3 on, when the lowest score is no higher than the lowest score two rounds earlier, ask the user whether to continue. When no user can answer, stop and go to step 7.

Otherwise read the feedback file and the scores, then revise the work.
Fix every finding.
When you reject a finding, write its item number and your reason to `$ledger/decisions-round-<n>.md`.
The judges never see these decisions.

For each item under Conflicts, pick one side and record the choice in the decisions file.
When a conflict is marked `repeat`, ask the user which side to take and continue with their answer. When no user can answer, stop and go to step 7.

Go to step 4 with the next round number.

## 7. Report

Report:

- The outcome: passed in round `<n>`, stopped at the round limit, stopped when scores stalled, stopped on a conflict, or stopped on a judge or consolidation failure.
- A score table with one row per round and one column per judge, headed by the judge's model.
- The items in the last feedback file, the rejected findings with reasons, and the unresolved conflicts.
- The defaults you used when no user could answer.
- The ledger path.

Delete each judge directory, and keep the ledger.
