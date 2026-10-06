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
Running autonomously (`standards`), file the issue instead of asking.
Carry the issue number to step 7 so the PR closes it.

## 2. Set up an isolated workspace

Use the worktree tooling the user's instructions specify. Otherwise create a worktree on a `feat/` or `fix/` branch and work inside it:

```bash
git worktree add ../<short-description> -b <feat|fix>/<short-description>
cd ../<short-description>
```

## 3. Do the work

Follow the `standards` rules for ubiquitous language, E2E-weighted tests, and branch hygiene.
Follow any provided plan exactly. Commit in stages when the scope is large.
When the request is explicitly test-first ("TDD this", "write the test first", "red, green, refactor"), drive this step with the `tdd` skill, if you use it. Otherwise work directly.

## 4. Validate locally

- Run tests, if available.
- Run lints.
- For a change with a runtime surface, exercise it end to end through its real entry point (`run`, where available).

## 5. Audit comments and documentation

Before publishing, audit every comment line the change adds and every documentation surface it touches. The `doc-audit` skill, if you use it, carries the procedure and applies the rules in `standards`.

The step closes with a stated result: what the audit covered and what it updated. A step with no stated result has not run.

## 6. Publish

Push the branch once steps 4 and 5 pass.

## 7. Open a PR

Open the PR per the `open-pr` skill, passing it the issue from step 1 so the body carries a closing reference. Then continue to CI.

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

Autonomous runs (`standards`) with no user to return to watch the PR through merge or CI under a bounded timeout, record the final PR state, and go to cleanup.

## 10. Cleanup

Clean up only when the PR is merged, closed without merging, or the user says to wrap up. An opened PR or green CI is not a reason. Remove the worktree with the tooling that created it:

```bash
git worktree remove ../<short-description>
```
