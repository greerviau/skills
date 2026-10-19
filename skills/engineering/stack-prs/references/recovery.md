# Stack recovery

## Local and GitHub stacks diverged

Keep the GitHub version:

```bash
gh stack unstack --local
gh stack checkout <stack-number>
```

Keep the local version:

```bash
gh stack unstack
gh stack submit --auto
```

PRs with auto-merge enabled or in a merge queue stay stacked after `unstack`. Clear that state first.

## Reorder, rename, or remove layers

Metadata changes do not change Git ancestry. Fix the branches first, then rebuild:

```bash
gh stack unstack
gh stack init --base main <bottom> ... <top>   # adopts existing branches
gh stack submit --auto
```

To swap layers, record each old boundary SHA before moving any branch, then replay each layer's commits onto its new parent.
For `main <- models <- migration <- ui` to `main <- migration <- models <- ui`:

```bash
old_models=$(git rev-parse models)
old_migration=$(git rev-parse migration)
git rebase --onto main "$old_models" migration
git rebase --onto migration main models
git rebase --onto models "$old_migration" ui
```

Then run the `unstack`, `init`, and `submit` commands above.

## Exit codes

- 6: the current branch is the trunk of several stacks. Run `gh stack checkout <branch-unique-to-the-intended-stack>`, or pass an explicit stack number, as in `merge 7`.
- 8: another `gh stack` process holds the lock. Retry after about 5 seconds. Do not delete lock files.

## Branches managed outside gh stack

`gh stack link` builds a stack on GitHub from branch names or PR numbers, bottom to top, with no local tracking:

```bash
gh stack link branch-a branch-b branch-c
gh stack link 7 branch-d          # append to existing stack #7
```

`up`, `down`, `top`, and `bottom` do not work on a linked stack until `gh stack checkout <stack-number>` adds local tracking.
