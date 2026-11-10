---
name: implement
description: Use for any request to implement a feature, fix a bug or issue, resolve a ticket, or execute a plan or spec in a Git repo, including "ship a PR" and work delegated from another thread. Use before editing code. Not for review-only or refactor-only requests.
---

# implement

Implement the request in an isolated worktree, build behavior changes test-first, and open a PR.
The request can be a one-line prompt, an issue, a ticket, or a spec. Do not require an issue and do not create one.

## 1. Ground

Read the request and the code it touches. Read the repo's `CODING-STANDARDS.md` and `UBIQUITOUS-LANGUAGE.md` when they exist, and use the glossary's terms verbatim.
Identify every requested outcome, including the acceptance criteria in a linked issue or spec.
Splitting work across PRs does not narrow the original request.
For a bug, reproduce it end to end the way a user hits it before changing code.
When the approach is uncertain, answer the question with a throwaway experiment before building.
Follow a provided plan or spec exactly.

## 2. Select a worktree

Use the requested worktree, or continue in the current linked worktree, including one created by an agent manager.
Preserve its path, branch, changes, and commits.
Otherwise, check `git worktree list --porcelain` for a worktree belonging to the request before creating one in `.worktrees/<short-description>` on a `feat/` or `fix/` branch:

```bash
common=$(git rev-parse --path-format=absolute --git-common-dir)
grep -qxF '.worktrees/' "$common/info/exclude" || echo '.worktrees/' >> "$common/info/exclude"
wt="$(dirname "$common")/.worktrees/<short-description>"
git fetch origin
git worktree add "$wt" -b <feat|fix>/<short-description> origin/<default-branch>
cd "$wt"
```

Work from the selected worktree's root, record its path as `wt` and branch as `branch`, and track whether this invocation created them.

## 3. Build test-first

Every behavior change is test-driven: write a failing test at the real entry point, confirm it fails because the behavior is missing, write the minimum code to pass, then refactor under green.
Record each red run's test name and failure message for the PR.
Run the typechecker and the test file you are changing after each edit.

## 4. Validate

Run the full test suite, the linter, and the typechecker.
Exercise a change with a runtime surface end to end through its real entry point.
Audit every comment the change adds and every documentation surface it touches, and rewrite what went stale.
Before opening the PR, map each requested outcome to its implementation and verification.
Report blocked outcomes and user-approved scope changes without describing unfinished scope as complete.

## 5. Review

Commit, then have a fresh subagent that did not write the change review the diff against `origin/<default-branch>` when delegation is available and permitted.
Pass it the base ref and the request, and leave out the conversation that produced the change.
When delegation is prohibited or no reviewer can start, review inline and state in the PR that independent review remains unperformed.
Continue other validation and report the restriction.
Fix every finding in the change, then rerun step 4. Reject a finding only when it misreads the change's intent, and say why in the final report.
Fix every lint error, failing test, and flaky test the change causes.
Leave defects outside the change unfixed, including pre-existing lint errors and test failures.
List them for the user and ask which to open as GitHub issues. When no user can answer, list them in the final report.

## 6. Open the PR and watch CI

Push, open the PR, and link the related issue whenever one exists. Use a closing reference when the PR should close it.
Link specs, plans, and other files only when they are committed and have a remote URL PR readers can access. Omit local paths, uncommitted files, and unpushed branches; summarize relevant details in the PR instead.
Inspect workflow event triggers and path filters, required checks, and checks on the pushed PR head.
Workflow files with only manual or release triggers do not imply PR checks will appear.
Wait for checks that are required or expected for this PR, using the host's supported wait mechanism.
When a required check cannot trigger, report the configuration blocker instead of waiting for it to appear.
When no checks are expected and none are pending or required, report that state and skip the wait.
On failure caused by the change, investigate, fix, and push until it passes.
When the failure predates the change, stop and ask the user how to proceed. When no user can answer, report the failure and stop.
Finish when the requested outcomes are covered, required validation passes, and the PR is open.
Report any blocked outcome or validation without claiming completion.
Do not keep watching the PR after its checks finish, or when no checks are expected.

## 7. Clean up

After the PR merges, remove the worktree and branch only if this invocation created them and the worktree is clean.
Leave reused worktrees, including agent-managed ones, in place unless the user asks to remove them.

```bash
common=$(git rev-parse --path-format=absolute --git-common-dir)
cd "$(dirname "$common")"
git worktree remove "$wt"
git branch -d "$branch"
```

Otherwise leave the worktree in place for follow-up feedback.
