---
name: dev-workflow
description: Use for development work in a GitHub project repo, including implementing features or fixes, executing plans, and requests to start, ship, land, or open a pull request. Covers issue-first work, isolated worktrees, validation, review, CI, and cleanup.
---

# dev-workflow

The development workflow for work inside a GitHub project repo.

## 1. Open an issue first

Work starts from an issue (`standards`, issue hygiene).
Before writing code, ask the user whether to open one. The `open-issue` skill, if you use it, writes and files it.
Skip the ask when an issue already covers the work (the user pointed at one, or a ticketing run filed it) or the change is trivial (a typo, a one-line fix).
When no user can answer (`standards`, interaction mode), file the issue instead of asking.
Carry the issue number to step 7 so the PR closes it.

## 2. Set up an isolated workspace

Create the worktree at `.worktrees/<short-description>` under the main checkout's root, on a `feat/` or `fix/` branch, and work inside it.
The commands resolve the main checkout from any worktree and add `.worktrees/` to the repo's local exclude file, so the repo's `.gitignore` stays unchanged:

```bash
common=$(git rev-parse --path-format=absolute --git-common-dir)
grep -qxF '.worktrees/' "$common/info/exclude" || echo '.worktrees/' >> "$common/info/exclude"
wt="$(dirname "$common")/.worktrees/<short-description>"
git fetch origin
git worktree add "$wt" -b <feat|fix>/<short-description> origin/<default-branch>
cd "$wt"
```

## 3. Do the work

Read `standards` and its `CODING-STANDARDS.md` before writing code, and follow their rules for ubiquitous language, test-first testing, and branch hygiene.
Follow any provided plan exactly. Commit in stages when the scope is large.

Build each behavior change test-first with the `tdd` skill, if you use it.
Without it, run the loop directly: write a test at the change's real entry point, run it and confirm it fails because the behavior is missing, write the minimum code to pass, then refactor while it stays green.
Record each red run's test name and failure message for the PR.
The exemptions (no behavior to test, or another guard proves the change) are in `CODING-STANDARDS.md`.

While building, run the typechecker and the test file you are changing after each edit. Run the full suite in step 4.

## 4. Validate locally

- Run the full test suite, if available.
- Run lints and the typechecker, if the repo has one.
- For a change with a runtime surface, exercise it end to end through its real entry point (`run`, where available).

## 5. Audit comments and documentation

Before publishing, audit every comment line the change adds and every documentation surface it touches. The `doc-audit` skill, if you use it, carries the procedure and applies the rules in `standards`.

The step closes with a stated result: what the audit covered and what it updated. A step with no stated result has not run.

## 6. Publish

Push the branch once steps 4 and 5 pass.

## 7. Open a PR

Open the PR per the `open-pr` skill, passing it the issue from step 1 so the body carries a closing reference.
Do not stop after opening the PR. Wait for CI in step 8.

## 8. Watch CI

Wait for CI to finish. On failure, investigate, fix, and push until it passes.

## 9. Keep the worktree and watch the PR

Keep the worktree while the PR is open. It holds the branch, build cache, and environment, and recreating it for each round of feedback is slow.

- Watch the PR from a harness-tracked background task (`Bash` with `run_in_background: true`) that exits when the PR leaves `OPEN`. Do not use a detached `nohup` daemon. When the task exits, the harness re-invokes you; check whether the PR ended `MERGED` or `CLOSED`.
  ```bash
  until [ "$(gh pr view <branch> --json state --jq .state)" != "OPEN" ]; do
    sleep 60
  done
  ```
- Handle feedback (PR comments or the live session) in the worktree: fix, revalidate (steps 4-8), push, and let the watcher keep waiting.

When no user can answer, watch the PR through merge or CI under a bounded timeout, record the final PR state, and go to cleanup.

## 10. Cleanup

Clean up only when the PR is merged, closed without merging, or the user says to wrap up. An opened PR or green CI is not a reason. Remove the worktree and its local branch:

```bash
common=$(git rev-parse --path-format=absolute --git-common-dir)
git -C "$(dirname "$common")" worktree remove .worktrees/<short-description>
git -C "$(dirname "$common")" branch -D <feat|fix>/<short-description>
```
