---
name: dev-workflow
description: Use whenever doing development work inside a GitHub project repo — implementing a feature, fixing a bug, or executing a plan. Covers opening an issue for the work before any code, acquiring an isolated git worktree, committing in reviewable stages, validating locally, enumerating every comment the change adds before publishing, publishing, opening an evergreen PR that closes the issue, watching CI to green, keeping the worktree alive while the PR is open and watching it to merge, and cleaning up the worktree only once the PR is merged. Trigger on "let's build this", "implement the plan", "start working on this feature/fix", "go ahead and make that change", "ship it", "ship the fix", "land this", "open a PR for this", or any request to write and land code in a repo.
---

# dev-workflow

The development workflow for work inside a GitHub project repo.

## 1. Open an issue first

Per the issue hygiene rules in `standards`, work starts from an issue.
Before writing any code, ask the user whether to open one — the `open-issue` skill, if you use it, writes and files it.
Skip the ask only when an issue already covers the work (the user pointed at one, or a ticketing run just filed it) or the change is trivial (a typo, a one-line fix).
Running autonomously (see `standards`), file the issue instead of asking.
Carry the issue number forward to step 7 so the PR closes it.

## 2. Set up an isolated workspace

Use a git worktree so this work is isolated. If the user's instructions specify worktree tooling, use that; otherwise create a worktree and a `feat/`- or `fix/`-named branch, and work from inside it:

```bash
git worktree add ../<short-description> -b <feat|fix>/<short-description>
cd ../<short-description>
```

## 3. Do the work

The house rules for this step live in the `standards` skill — ubiquitous language, the E2E-weighted testing bias, and branch hygiene (flag unrelated out-of-scope bugs, fix them on a separate branch). Beyond those: follow any provided plan exactly, and commit in stages if the scope is large so history stays reviewable. When the request is explicitly test-first ("TDD this", "write the test first", "red, green, refactor"), reach for the `tdd` skill, if you use it, to drive this step. Without one of those markers, do the work directly - the default for most requests.

## 4. Validate locally

- Run tests, if available.
- Run lints.
- For changes with a runtime surface, exercise the change end-to-end against its real entry point (`run`, where available).

## 5. Audit the comments and documentation

The comment form rules in `standards` apply to every comment line the change adds, so this step enumerates them rather than eyeballing the diff. Run both commands and resolve every line they print.

Runs of three or more consecutive added comment lines:

```bash
git diff <base>..HEAD -U0 | awk '
  /^\+\+\+ /  { file = substr($0, 7); n = 0; next }
  /^@@/       { n = 0; next }
  /^\+[[:space:]]*(#|\/\/|--|\*|<!--)/ {
      run[++n] = $0
      if (n == 3) { print "\n" file; for (i = 1; i <= n; i++) print run[i] }
      else if (n > 3) print $0
      next }
              { n = 0 }
'
```

Added comments that clarify with an example:

```bash
git diff <base>..HEAD | grep -nE '^\+.*(#|//|--|\*).*([Ee]\.g\.|[Ff]or example|[Ii]\.e\.)'
```

Both over-collect, hitting docstrings, module-level documentation, and license headers that the cap exempts. Resolve each line either way: dismiss a hit by naming the exemption, and fix a hit on an inline comment by fixing the code the comment was explaining.

Then audit the rest of the surface the change touched: docstrings, the nearest README, `docs/` files, examples. The `doc-audit` skill, if you use it, carries that procedure and the plain-language check.

Close the step by reporting one line: how many lines the commands printed and how each was resolved. Empty output is a result; no output because the commands never ran is not.

## 6. Publish

Push the branch once validation and step 5 both pass.

## 7. Open a PR when ready for review

Open the PR per the `open-pr` skill, passing it the issue from step 1 so the body carries a closing reference. Do not stop here — wait and watch it through CI.

## 8. Watch CI

Wait for CI to complete. If it fails, investigate, fix, and push until it's green.

## 9. Keep the worktree alive and watch the PR

An open PR still needs to survive review, and the worktree is the only place the branch, build cache, and environment live. **Do not tear it down while the PR is open** — tearing it down forces a full recreate on the next round of feedback.

- Watch the PR from a harness-tracked background task (`Bash` with `run_in_background: true`) that blocks until the PR leaves `OPEN`, then exits — not a detached `nohup` daemon. When it exits, the harness re-invokes you for cleanup; check whether the PR ended `MERGED` (work landed) or `CLOSED`.
  ```bash
  until [ "$(gh pr view <branch> --json state --jq .state)" != "OPEN" ]; do
    sleep 60
  done
  ```
- While it runs, handle feedback (PR comments or the live session) on the still-live worktree: fix, revalidate (steps 4–8), push, then let the watcher keep waiting.

**Interaction mode** (see `standards`): running autonomously with no user to return, watch the PR through merge/CI under a bounded timeout, then go to cleanup and record the final PR state — don't hold the worktree open for feedback that won't come.

## 10. Cleanup

Only when the PR is **merged**, was closed without merging, or the user told you to wrap up — never just because a PR opened or CI went green. Remove the worktree with the tooling that created it:

```bash
git worktree remove ../<short-description>
```
