---
name: dev-workflow
description: Use whenever doing development work inside a GitHub project repo — implementing a feature, fixing a bug, or executing a plan. Covers acquiring an isolated git worktree, committing in reviewable stages, validating locally, publishing, opening an evergreen PR, watching CI to green, keeping the worktree alive while the PR is open and watching it to merge, and cleaning up the worktree only once the PR is merged. Trigger on "let's build this", "implement the plan", "start working on this feature/fix", "go ahead and make that change", "ship it", "ship the fix", "land this", "open a PR for this", or any request to write and land code in a repo.
---

# dev-workflow

The development workflow for work inside a GitHub project repo.

## 1. Set up an isolated workspace

Use a git worktree so this work is isolated. If the user's instructions specify worktree tooling, use that; otherwise create a worktree and a `feat/`- or `fix/`-named branch, and work from inside it:

```bash
git worktree add ../<short-description> -b <feat|fix>/<short-description>
cd ../<short-description>
```

## 2. Do the work

The house rules for this step live in the `standards` skill — ubiquitous language, the E2E-weighted testing bias, and branch hygiene (flag unrelated out-of-scope bugs, fix them on a separate branch). Beyond those: follow any provided plan exactly, and commit in stages if the scope is large so history stays reviewable.

## 3. Validate locally

- Run tests, if available.
- Run lints.
- Audit affected documentation (`doc-audit`) and, for changes with a runtime surface, exercise the change end-to-end against its real entry point (`run`, where available).

## 4. Publish

Push the branch once validation passes.

## 5. Open a PR when ready for review

Open the PR per the `open-pr` skill. Do not stop here — wait and watch it through CI.

## 6. Watch CI

Wait for CI to complete. If it fails, investigate, fix, and push until it's green.

## 7. Keep the worktree alive and watch the PR

An open PR still needs to survive review, and the worktree is the only place the branch, build cache, and environment live. **Do not tear it down while the PR is open** — tearing it down forces a full recreate on the next round of feedback.

- Watch the PR from a harness-tracked background task (`Bash` with `run_in_background: true`) that blocks until the PR leaves `OPEN`, then exits — not a detached `nohup` daemon. When it exits, the harness re-invokes you for cleanup; check whether the PR ended `MERGED` (work landed) or `CLOSED`.
  ```bash
  until [ "$(gh pr view <branch> --json state --jq .state)" != "OPEN" ]; do
    sleep 60
  done
  ```
- While it runs, handle feedback (PR comments or the live session) on the still-live worktree: fix, revalidate (steps 3–6), push, then let the watcher keep waiting.

**Interaction mode** (see `standards`): running autonomously with no user to return, watch the PR through merge/CI under a bounded timeout, then go to cleanup and record the final PR state — don't hold the worktree open for feedback that won't come.

## 8. Cleanup

Only when the PR is **merged**, was closed without merging, or the user told you to wrap up — never just because a PR opened or CI went green. Remove the worktree with the tooling that created it:

```bash
git worktree remove ../<short-description>
```
