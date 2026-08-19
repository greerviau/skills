---
name: merge-conflict
description: Use when a Git merge or rebase has conflicts that need semantic resolution. Inspects both changes and their intent, resolves each conflict without inventing behavior, reruns the repository checks, and completes the operation. Trigger on "resolve this merge conflict", "I'm in a merge conflict", "fix these rebase conflicts", "the rebase is stuck", "continue this rebase", "finish this merge".
---

Resolve an active Git merge or rebase by preserving the intent of both sides where they are compatible and choosing the behavior required by the integration target when they are not.
Do not resolve a conflict by picking a side because its markers appear first, and do not declare success until the repository checks pass after the resolution.

## Procedure

1. **Capture the integration state.** Run `git status`, `git branch --show-current`, and `git log --oneline --decorate -10`.
   Identify whether Git is in a merge, rebase, or another sequenced operation, the target branch, the current commit, and every unmerged path.
   If no operation is active, identify the target branch and choose the integration method from the repository policy: rebase a private branch when its history may be rewritten, and merge a shared or reviewed branch when its published history must remain stable.
   Do not switch from merge to rebase, or from rebase to merge, after conflicts appear.

2. **Read the integration contract.** Check the repository's contribution guide, branch policy, pull-request description, linked issue, and relevant CI configuration.
   Record constraints such as required generated files, supported versions, public API compatibility, migration order, and required checks.
   If the repository defines no policy, preserve the existing operation and use the integration target's current behavior as the contract.

3. **Trace both intents for each conflict.** Start with the conflict file and its surrounding code.
   Use the merge base and commit history to understand why each side changed:

   ```bash
   git diff --name-only --diff-filter=U
   git merge-base HEAD <target-branch>
   git log --oneline --left-right --merge -- <path>
   git show <commit> -- <path>
   git diff :1:<path> :2:<path>
   git diff :1:<path> :3:<path>
   ```

   For a rebase, inspect the commit being replayed and the target branch separately; do not assume Git's `ours` and `theirs` labels match the branch names in your head.
   Read the originating pull request and issue with `gh pr view` and `gh issue view` when the repository uses GitHub and the links are available.
   Treat the conflict markers as evidence of overlapping text, not as an explanation of the desired behavior.

4. **Resolve each hunk semantically.** State the behavior each side adds, removes, or changes before editing the file.
   Preserve both changes when they address independent behavior.
   When they are incompatible, choose the behavior that satisfies the integration target and the repository contract, and record the rejected behavior in the resolution notes or handoff.
   Keep surrounding invariants intact, including ordering, validation, error handling, generated output, and public interfaces.
   Do not use `git checkout --ours` or `git checkout --theirs` for a whole file unless the primary-source review proves that the whole file belongs to that side.
   Do not introduce new behavior to make the hunk compile.

5. **Check the resolved tree before staging.** Run:

   ```bash
   git diff --check
   git grep -n -E '^(<{7}|={7}|>{7})( |$)' -- . ':!*.lock' || true
   git diff -- <resolved-paths>
   git status
   ```

   Inspect the complete resolved files, not only the former conflict hunks.
   Stage each resolved path with `git add` and confirm that `git diff --cached` contains no conflict markers or accidental unrelated changes.

6. **Run the repository's checks.** Discover the commands from `README` or `CONTRIBUTING` files, package scripts, task configuration, and CI workflows.
   Run the formatter or linter, type checker when present, focused checks for the resolved paths, and the full test suite.
   Run the checks against the post-resolution tree, even when the conflict appears to affect documentation only.
   If a check fails, determine whether the resolution caused it by comparing the failure with the pre-integration side and the target branch; fix only merge-induced failures in this operation.
   Do not hide an unrelated failure in the conflict resolution.

7. **Complete the operation.** For a merge, run `git commit` or `git merge --continue` according to the repository's Git version and hooks.
   For a rebase, run `git rebase --continue` and repeat steps 3 through 7 for every remaining commit and conflict.
   After completion, run `git status`, inspect the final graph, and rerun the full checks if the operation replayed additional commits after the last check.
   Do not use `--skip` or `--abort` as a substitute for understanding a conflict; if the chosen operation or target is wrong, stop and report that decision rather than silently discarding work.

## Report

Return a structured report:

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

**Interaction mode** (see `standards`): running autonomously, proceed using the repository's documented policy and the integration target's current behavior when no human decision is required.
When two incompatible behaviors both satisfy the available contract and the choice changes a public interface, migration, data format, or security boundary, stop before editing that hunk and report the decision required.

## Boundaries

- This skill resolves conflicts and completes the active Git operation; it does not invent a feature, silently skip a commit, or discard a side without evidence.
- It does not replace the repository's normal validation or PR workflow; resume that workflow after completion.
- A deterministic test failure caused by the resolved code belongs to `debug`, if you use it; an intermittent failure belongs to `flake-hunt`, if you use it.
- Flag unrelated bugs or pre-existing check failures for their own issue and branch.
