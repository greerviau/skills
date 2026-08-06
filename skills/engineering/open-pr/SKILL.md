---
name: open-pr
description: Use when opening a pull request or writing/rewriting its title and body — standalone ("open a PR for this branch", "write the PR description") or as the PR step of the dev workflow. Produces a `feat(...)`/`fix(...)` title and a short, evergreen body (Problem, Changes, Testing, Additional testing required, Regressions) that fits on one screen, with no AI attribution, no co-author lines, and no volatile version details, then opens the PR. Trigger on "open a PR", "open a PR for this branch", "write the PR description", "describe this PR", "PR title and body for this branch".
---

# open-pr

Open a pull request: write its title and body, then create it. This is the single source of truth for PR title and body conventions — invoked standalone or as the PR step of `dev-workflow`.

## Procedure

1. **Scope the branch.** Diff against the base to see what actually changed. The title and body describe the branch as it stands, not how it got there.
2. **Write the title.** `feat(...)` / `fix(...)` conventional-commit form with a concise scope and summary (e.g. `fix(worktree): keep worktree alive until PR merges`).
3. **Link a provided issue.** If the request or branch context provides a GitHub issue — the issue-first step of the development workflow supplies one — add a closing reference such as `Fixes #123` to the PR body.
   For a same-repository issue, this puts the PR in the issue's **Development** section and closes the issue when the PR merges into the default branch.
   The branch itself does not close the issue; the closing reference on the PR does.
   Use `Fixes owner/repo#123` for an issue in another repository.
   Use `Related to #123` instead when the PR should not close the issue.
4. **Write an evergreen body** covering:
   - **Problem / request** — the problem or feature being requested, and what this PR does about it.
     State the goal separately only when the scope is deliberately narrower or broader than the problem, or when the goal isn't the obvious one.
   - **Changes** — a concise summary of what was done.
   - **Testing** — how it was tested.
   - **Additional testing required** — anything a reviewer or QA should still exercise.
   - **Regressions** — known or potential regressions to watch for.

   Follow the repo's PR template where one exists, adding anything else valuable.
5. **Keep it short.** A PR body is human-facing: hold it to the budget and the cuts in *Artifact audience* (`standards`). Applied here:
   - One or two sentences per section. **Changes** may be a bullet list, one line per meaningful change, grouped rather than file-by-file.
   - Cut what the diff already says: file walkthroughs, function signatures, line counts, quoted code.
   - Where a design decision or migration needs real depth, link to the spec or issue instead of inlining it.
6. **Keep it evergreen.** Per the PR and commit hygiene rules in `standards`: written once and kept accurate as the branch evolves, no AI attribution of any kind, no volatile details (version bumps and the like) that go stale.
7. **Run the concision pass** (`standards`) over the drafted body unless it's already well inside the budget, and apply what it returns.
8. **Open the PR** with the title and body (e.g. `gh pr create`).
