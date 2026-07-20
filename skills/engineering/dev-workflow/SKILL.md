---
name: dev-workflow
description: Use whenever doing development work inside a GitHub project repo — implementing a feature, fixing a bug, or executing a plan. Covers acquiring an isolated git worktree, committing in reviewable stages, validating locally, publishing, opening an evergreen PR, watching CI to green, and cleaning up the worktree. Trigger on "let's build this", "implement the plan", "start working on this feature/fix", "go ahead and make that change", "ship it", "ship the fix", "land this", "open a PR for this", or any request to write and land code in a repo.
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

- If a plan is provided, follow it exactly.
- If the repo (or the subdirectory you're working in) has an `UBIQUITOUS-LANGUAGE.md` glossary, read it and use its terms verbatim when naming code — types, functions, endpoints, tables, tests, and commit/PR prose. Don't coin synonyms for concepts the glossary already names. If implementation forces a new domain term or exposes a stale entry, update the glossary in the same PR.
- Commit work in stages if the scope is large, so history stays reviewable.
- Write tests as necessary, opting for E2E tests over small unit tests — test the functionality as closely to how a user would interact with it as possible.
- If unrelated out-of-scope bugs or improvements surface, don't fix them on the current branch. Flag them, then fix them on a separate worktree/branch/PR, following this same workflow.

## 3. Validate locally

- Run tests if they're available.
- Run lints.
- Audit affected documentation (the `doc-audit` skill) and, for changes with a runtime surface, exercise the change end-to-end (the `verify` skill).

## 4. Publish

Push the work to the branch once validation passes.

## 5. Open a PR when ready for review

The PR title follows `feat(...)`, `fix(...)` naming conventions.

Write the PR body per the `pr-describe` skill — an evergreen body covering problem, intent, changes, testing, additional testing required, and regressions, with no AI attribution or volatile version details.

Do not stop here — wait and watch the PR through CI.

## 6. Watch CI

- Wait for CI to complete.
- If it fails, investigate, fix, and push the fixes. Continue until CI is green.

## 7. Cleanup

- Remove the worktree once the PR has landed (or the work is abandoned), using the same tooling that created it:
  ```bash
  git worktree remove ../<short-description>
  ```
