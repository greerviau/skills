---
name: implement
description: Use for development work in a git repo - implementing a feature or fix from a prompt, issue, ticket, or spec, executing a plan, or shipping a change as a pull request.
---

# implement

Implement the request in an isolated worktree, build it test-first, open a PR, and finish when CI passes.
The request can be a one-line prompt, an issue, a ticket, or a spec. Do not require an issue and do not create one.

## 1. Ground

Read the request and the code it touches. Read the repo's `CODING-STANDARDS.md` and `UBIQUITOUS-LANGUAGE.md` when they exist, and use the glossary's terms verbatim.
For a bug, reproduce it end to end the way a user hits it before changing code.
When the approach is uncertain, answer the question with a throwaway experiment before building.
Follow a provided plan or spec exactly.

## 2. Create a worktree

Work in `.worktrees/<short-description>` under the main checkout, on a `feat/` or `fix/` branch.
The commands add `.worktrees/` to the repo's local exclude file, so `.gitignore` stays unchanged:

```bash
common=$(git rev-parse --path-format=absolute --git-common-dir)
grep -qxF '.worktrees/' "$common/info/exclude" || echo '.worktrees/' >> "$common/info/exclude"
wt="$(dirname "$common")/.worktrees/<short-description>"
git fetch origin
git worktree add "$wt" -b <feat|fix>/<short-description> origin/<default-branch>
cd "$wt"
```

## 3. Build test-first

Every behavior change is test-driven: write a failing test at the real entry point, confirm it fails because the behavior is missing, write the minimum code to pass, then refactor under green.
Record each red run's test name and failure message for the PR.
Run the typechecker and the test file you are changing after each edit.

## 4. Validate

Run the full test suite, the linter, and the typechecker.
Exercise a change with a runtime surface end to end through its real entry point.
Audit every comment the change adds and every documentation surface it touches, and rewrite what went stale.

## 5. Review

Commit, then have a subagent that did not write the change review the diff against `origin/<default-branch>`.
Pass it the base ref and the request, and leave out the conversation that produced the change.
Review inline when no subagent is available.
Fix every finding in the change, then rerun step 4. Reject a finding only when it misreads the change's intent, and say why in the final report.
Fix every lint error, failing test, and flaky test the change causes.
Leave defects outside the change unfixed, including pre-existing lint errors and test failures.
List them for the user and ask which to open as GitHub issues. When no user can answer, list them in the final report.

## 6. Open the PR and watch CI

Push, open the PR, and link the related issue whenever one exists. Use a closing reference when the PR should close it.
Link specs, plans, and other files only when they are committed and have a remote URL PR readers can access. Omit local paths, uncommitted files, and unpushed branches; summarize relevant details in the PR instead.
Wait for CI. On failure, investigate, fix, and push until it passes.
When the failure predates the change, stop and ask the user how to proceed. When no user can answer, report the failure and stop.
CI passing finishes the work. Do not keep watching the PR.

## 7. Clean up

When the PR is merged by the time you finish, or the user later says it merged, remove the worktree and its local branch:

```bash
common=$(git rev-parse --path-format=absolute --git-common-dir)
git -C "$(dirname "$common")" worktree remove .worktrees/<short-description>
git -C "$(dirname "$common")" branch -D <feat|fix>/<short-description>
```

Otherwise leave the worktree in place for follow-up feedback.
