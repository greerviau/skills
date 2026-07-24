---
name: open-pr
description: Use when opening a pull request or writing/rewriting its title and body — standalone ("open a PR for this branch", "write the PR description") or as the PR step of the dev workflow. Produces a `feat(...)`/`fix(...)` title and an evergreen body (Problem, Intent, Changes, Testing, Additional testing required, Regressions) with no AI attribution, no co-author lines, and no volatile version details, then opens the PR. Trigger on "open a PR", "open a PR for this branch", "write the PR description", "describe this PR", "PR title and body for this branch".
---

# open-pr

Open a pull request: write its title and body, then create it. This is the single source of truth for PR title and body conventions — invoked standalone or as the PR step of `dev-workflow`.

## Procedure

1. **Scope the branch.** Diff against the base to see what actually changed. The title and body describe the branch as it stands, not how it got there.
2. **Write the title.** `feat(...)` / `fix(...)` conventional-commit form with a concise scope and summary (e.g. `fix(worktree): keep worktree alive until PR merges`).
3. **Write an evergreen body** covering:
   - **Problem / request** — the problem or feature being requested.
   - **Intent** — the goal of the change.
   - **Changes** — a concise summary of what was done.
   - **Testing** — how it was tested.
   - **Additional testing required** — anything a reviewer or QA should still exercise.
   - **Regressions** — known or potential regressions to watch for.

   Follow the repo's PR template where one exists, adding anything else valuable.
4. **Keep it evergreen.** Per the PR and commit hygiene rules in `standards`: written once and kept accurate as the branch evolves, no AI attribution of any kind, no volatile details (version bumps and the like) that go stale.
5. **Open the PR** with the title and body (e.g. `gh pr create`).
