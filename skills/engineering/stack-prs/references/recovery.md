# Stack recovery

## Local and GitHub stacks diverged

`gh stack sync` reports `Sync aborted` when the local stack and the stack on GitHub each gained different branches.
No PR or branch is deleted by either resolution.

Keep the GitHub version:

```bash
gh stack unstack --local            # drops local tracking only
gh stack checkout <stack-number>    # or a PR number
```

Keep the local version:

```bash
gh stack unstack                    # removes the grouping on GitHub
gh stack submit --auto              # recreates it from local state
```

PRs with auto-merge enabled or queued in a merge queue stay stacked after `unstack`.
Clear that state before retrying.

## Change the order or membership of layers

No non-interactive command reorders, renames, or removes a layer.
Changing stack metadata does not change Git ancestry, so reorder the commits first, then rebuild the stack from the existing branches.

To remove or rename a layer, fix the branches, then:

```bash
gh stack unstack
gh stack init --base main <bottom> ... <top>   # adopts existing branches
gh stack submit --auto                         # updates PR bases and relinks
```

To swap layers, record each old boundary before moving any branch, replay each layer's own commits onto its new parent, then rebuild.
For `main <- models <- migration <- ui` becoming `main <- migration <- models <- ui`:

```bash
old_models=$(git rev-parse models)
old_migration=$(git rev-parse migration)
git rebase --onto main "$old_models" migration
git rebase --onto migration main models
git rebase --onto models "$old_migration" ui
gh stack unstack
gh stack init --base main migration models ui
gh stack submit --auto
```

For another order, find each layer's range with `git log <old-parent>..<branch>` and replay the ranges bottom to top.

## Exit 6: branch belongs to several stacks

The current branch is the trunk of more than one stack.
Run `gh stack checkout <branch-unique-to-the-intended-stack>`, then rerun.
Commands that take an explicit stack number, such as `merge 7` and `unstack 7`, skip the lookup.

## Exit 8: stack file locked

Another `gh stack` process holds the lock.
Wait about 5 seconds and retry.
Do not delete lock files.

## Exit 10: interrupted modify session

Run `gh stack modify --abort`.

## Branches managed by another tool

`gh stack link` builds a stack on GitHub from branch names or PR numbers and writes no local tracking state.
Arguments run bottom to top:

```bash
gh stack link branch-a branch-b branch-c        # pushes branches, creates missing PRs
gh stack link 10 20 30                          # existing PRs by number
gh stack link 7 branch-d                        # append to existing stack #7
gh stack link --base develop --open a b c       # non-default trunk, ready for review
```

`link` only adds PRs to a stack.
`up`, `down`, `top`, and `bottom` do not work on a stack with no local tracking.
Run `gh stack checkout <stack-number>` to add local tracking.
