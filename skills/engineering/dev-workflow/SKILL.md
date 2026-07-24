---
name: dev-workflow
description: Use whenever doing development work inside a GitHub project repo — implementing a feature, fixing a bug, or executing a plan. Covers acquiring an isolated git worktree, committing in reviewable stages, validating locally, publishing, opening an evergreen PR, watching CI to green, keeping the worktree alive while the PR is open and watching it to merge, and cleaning up the worktree only once the PR is merged. Trigger on "let's build this", "implement the plan", "start working on this feature/fix", "go ahead and make that change", "ship it", "ship the fix", "land this", "open a PR for this", or any request to write and land code in a repo.
---

# dev-workflow

This is the development workflow to follow when doing work inside a GitHub project repo.

## 1. Set up an isolated workspace

Use a git worktree so this work is isolated from other branches and in-progress changes. If the user's instructions specify worktree tooling (e.g. a CLI like `treehouse`), use that; otherwise:

- Create a worktree and a branch that follows the `feat/`, `fix/` naming convention (e.g. `feat/short-description`, `fix/short-description`):
  ```bash
  git worktree add ../<short-description> -b <branch>
  cd ../<short-description>
  ```
- Do all subsequent work from inside that worktree.

## 2. Do the work

The house rules for this step live in the `standards` skill — ubiquitous language (read the glossary, use its terms verbatim, extend it in the same PR), the E2E-weighted testing bias, and branch hygiene (flag unrelated out-of-scope bugs and fix them on a separate branch). Beyond those:

- If a plan is provided, follow it exactly.
- Commit work in stages if the scope is large, so history stays reviewable.

## 3. Validate locally

- Run tests if they're available.
- Run lints.
- Audit affected documentation (the `doc-audit` skill) and, for changes with a runtime surface, exercise the change end-to-end against its real entry point (the `run` skill, where available).

## 4. Publish

Push the work to the branch once validation passes.

## 5. Open a PR when ready for review

Open the PR per the `open-pr` skill — it writes the `feat(...)`/`fix(...)` title and an evergreen body (problem, intent, changes, testing, additional testing required, regressions, with no AI attribution or volatile version details) and creates the PR.

Do not stop here — wait and watch the PR through CI.

## 6. Watch CI

- Wait for CI to complete.
- If it fails, investigate, fix, and push the fixes. Continue until CI is green.

## 7. Keep the worktree alive and watch the PR

Once the PR is open, the work is not done — it needs to survive review. **Do not tear down the worktree while the PR is open.** The user may come back with feedback in the same session or a later one, and the worktree is the only place the branch, build cache, and environment live. Destroying it prematurely forces a full recreate-from-scratch on the next round of feedback.

- Watch the PR in the background so the session stays responsive. Start a harness-tracked background task (a `Bash` call with `run_in_background: true`) that **blocks until the PR is merged, then exits** — not a detached `nohup` daemon. When it exits, the harness re-invokes you to run cleanup. Poll on an interval, e.g.:
  ```bash
  # blocks until the PR leaves the OPEN state (MERGED or CLOSED), then exits 0
  until [ "$(gh pr view <branch> --json state --jq .state)" != "OPEN" ]; do
    sleep 60
  done
  ```
  When it exits, check whether the PR was `MERGED` or `CLOSED` — either way the worktree is safe to clean up, but only a merge means the work landed.
- While the watcher runs, handle any feedback you receive — in PR review comments or directly in the interactive session — on the still-live worktree: fix, revalidate (steps 3–6), and push. Then let the watcher keep waiting.
- If the user explicitly tells you to wrap up / abandon the work, stop the watcher and go to cleanup. Otherwise keep the worktree alive until the watcher exits.

**Interaction mode** (see `standards`): the keep-alive-for-feedback loop assumes an interactive user who may return. When running autonomously with no user to return, don't hold the worktree open indefinitely — watch the PR through merge/CI under a bounded timeout, then proceed to cleanup, recording the final PR state instead of waiting on feedback that won't come.

## 8. Cleanup

Only reach this step when the PR is **merged**, the PR was closed without merging, or the user explicitly told you to wrap up. Never remove the worktree just because a PR was opened or CI went green — an open PR means work may still come back.

- Remove the worktree using the same tooling that created it:
  ```bash
  git worktree remove ../<short-description>
  ```
