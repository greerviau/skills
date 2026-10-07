---
name: open-pr
description: Use when opening or writing a pull request. Produces a concise conventional-commit title and evergreen body with problem, changes, testing, additional testing, and regressions.
---

# open-pr

Write a pull request's title and body, then create it. This skill is the single source of truth for PR title and body conventions, whether invoked directly or as the PR step of `dev-workflow`.

## Procedure

1. Scope the branch. Diff against the base to see what changed. The title and body describe the branch as it stands, not how it got there.
2. Write the title in conventional-commit form, `feat(...)` or `fix(...)`, with a concise scope and summary, such as `fix(worktree): keep worktree alive until PR merges`.
3. Link the issue. If the request or branch context provides a GitHub issue (the issue-first step of `dev-workflow` supplies one), add a closing reference to the body, such as `Fixes #123`.
   For a same-repository issue, the PR appears in the issue's Development section and closes the issue when it merges into the default branch. The branch alone does not close it.
   Use `Fixes owner/repo#123` for an issue in another repository, and `Related to #123` when the PR should not close the issue.
4. Write an evergreen body with these sections, following the repo's PR template where one exists:
   - Problem / request: the problem or requested feature, and what this PR does about it. State the goal separately only when the scope is deliberately narrower or broader than the problem, or the goal is not obvious.
   - Changes: a concise summary of what was done.
   - Testing: how it was tested. For a behavior change, name a test that failed before the change and its failure message.
   - Additional testing required: what a reviewer or QA should still exercise.
   - Regressions: known or potential regressions to watch for.
5. Keep it short. The body is human-facing, so hold it to the budget and cuts in *Artifact audience* (`standards`):
   - Write one or two sentences per section. Changes may be a bullet list with one line per meaningful change, grouped instead of file by file.
   - Cut what the diff already shows: file walkthroughs, function signatures, line counts, quoted code.
   - Link to the spec or issue for a design decision or migration that needs depth.
6. Keep it evergreen per the PR and commit hygiene rules in `standards`: accurate as the branch changes, no AI attribution, no volatile details such as version bumps.
7. Measure the draft. Run `wc -w` on the body and compare it to the budget in *Artifact audience* (`standards`), because authors read their own drafts as short. Inside the budget, go to step 8. Over it, run the concision pass (`standards`) and apply the result. If it is still over the ceiling, cut again or move the depth into the linked issue or spec.
8. Open the PR with the title and body, for example with `gh pr create`.
