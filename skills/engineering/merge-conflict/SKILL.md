---
name: merge-conflict
description: Use when a Git merge or rebase has conflicts that need semantic resolution. Inspects both changes and their intent, resolves each conflict without inventing behavior, reruns the repository checks, and completes the operation. Trigger on "resolve this merge conflict", "I'm in a merge conflict", "fix these rebase conflicts", "the rebase is stuck", "continue this rebase", "finish this merge".
---

Resolve an active Git merge or rebase by keeping the intent of both sides where they are compatible and choosing the behavior the integration target requires where they are not.
Do not pick a side because its markers appear first, and do not declare success until the repository checks pass on the resolved tree.

## Procedure

1. Capture the integration state. Run `git status`, `git branch --show-current`, and `git log --oneline --decorate -10`.
   Identify whether Git is in a merge, rebase, or another sequenced operation, the target branch, the current commit, and every unmerged path.
   If no operation is active, identify the target branch and choose the method from repository policy: rebase a private branch whose history may be rewritten, and merge a shared or reviewed branch whose published history must stay stable.
   Do not switch between merge and rebase after conflicts appear.

2. Read the integration contract: the contribution guide, branch policy, PR description, linked issue, and relevant CI configuration.
   Record constraints such as required generated files, supported versions, public API compatibility, migration order, and required checks.
   If the repository defines no policy, keep the existing operation and treat the integration target's current behavior as the contract.

3. Trace both intents for each conflict. Start with the conflicted file and its surrounding code, then use the merge base and commit history to see why each side changed:

   ```bash
   git diff --name-only --diff-filter=U
   git merge-base HEAD <target-branch>
   git log --oneline --left-right --merge -- <path>
   git show <commit> -- <path>
   git diff :1:<path> :2:<path>
   git diff :1:<path> :3:<path>
   ```

   For a rebase, inspect the commit being replayed and the target branch separately. Git's `ours` and `theirs` labels may not match the branch names you expect.
   When the repository uses GitHub and the links are available, read the originating PR and issue with `gh pr view` and `gh issue view`.
   Conflict markers show overlapping text. They do not explain the desired behavior.

4. Resolve each hunk semantically. State the behavior each side adds, removes, or changes before editing.
   Keep both changes when they address independent behavior.
   When they are incompatible, choose the behavior that satisfies the integration target and repository contract, and record the rejected behavior in the resolution notes or handoff.
   Keep surrounding invariants intact: ordering, validation, error handling, generated output, and public interfaces.
   Use `git checkout --ours` or `--theirs` on a whole file only when review of the primary sources shows the whole file belongs to that side.
   Do not add new behavior to make a hunk compile.

5. Check the resolved tree before staging:

   ```bash
   git diff --check
   git grep -n -E '^(<{7}|={7}|>{7})( |$)' -- . ':!*.lock' || true
   git diff -- <resolved-paths>
   git status
   ```

   Read the complete resolved files, not only the former conflict hunks.
   Stage each resolved path with `git add` and confirm `git diff --cached` has no conflict markers or unrelated changes.

6. Run the repository's checks. Find the commands in `README` or `CONTRIBUTING` files, package scripts, task configuration, and CI workflows.
   Run the formatter or linter, the type checker if present, focused checks for the resolved paths, and the full test suite.
   Run them on the post-resolution tree even when the conflict looks documentation-only.
   If a check fails, compare the failure with the pre-integration side and the target branch to see whether the resolution caused it. Fix only merge-induced failures in this operation.
   Do not bury an unrelated failure in the conflict resolution.

7. Complete the operation. For a merge, run `git commit` or `git merge --continue`, depending on the Git version and hooks.
   For a rebase, run `git rebase --continue` and repeat steps 3 through 7 for each remaining commit and conflict.
   Afterward, run `git status`, inspect the final graph, and rerun the full checks if the operation replayed commits after the last check.
   Do not use `--skip` or `--abort` instead of understanding a conflict. If the chosen operation or target is wrong, stop and report that decision instead of discarding work.

## Report

```text
Operation: <merge|rebase>
Target: <branch or commit>
Conflicts: <resolved paths>
Sources reviewed: <commits, pull requests, issues, or repository policy>
Resolution: <behavior preserved or trade-off chosen for each incompatible hunk>
Checks: <commands and results>
Completion: <completed operation and resulting commit, or remaining blocker>
Confidence: <high|moderate|low>
```

Autonomous runs (`standards`) resolve using the repository's documented policy and the integration target's current behavior when no human decision is needed.
When two incompatible behaviors both satisfy the contract and the choice changes a public interface, migration, data format, or security boundary, stop before editing that hunk and report the decision required.

## Scope

- This skill resolves conflicts and completes the active Git operation. It does not invent a feature, skip a commit, or discard a side without evidence.
- Resume the repository's normal validation and PR workflow after completion.
- A deterministic test failure caused by the resolved code belongs to `debug`, if you use it. An intermittent failure belongs to `flake-hunt`, if you use it.
- Flag unrelated bugs and pre-existing check failures for their own issue and branch.
