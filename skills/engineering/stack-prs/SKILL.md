---
name: stack-prs
description: Use when splitting work into dependent pull requests, or when a stack is checked out. Builds, submits, syncs, and merges GitHub stacked PRs with the `gh stack` extension. Trigger on "stack these PRs", "split this into a stack", "dependent PRs", "gh stack".
---

# stack-prs

Build dependent PRs as a GitHub **stack**: branches chained bottom to top, each with one PR based on the branch below it.
Change the chain only with `gh stack` commands.
Do not set PR bases by hand or use `gh pr merge` on a stack PR.

## Preflight

1. Run `gh extension list`. If `github/gh-stack` is missing, run `gh extension install github/gh-stack` (needs `gh` 2.90.0+ and Git 2.36+).
2. Run `git config rerere.enabled true`.
3. With more than one remote, run `git config remote.pushDefault origin`.
4. Run `gh stack view --json`. Exit 9 means stacked PRs are not enabled on the repo: tell the user and stop.

## Commands

Bare `gh stack` commands open prompts or TUIs that block an agent. Use:

- `gh stack view --json`, not `view`
- `gh stack init <branch>...` and `gh stack add <branch>`, with the name given
- `gh stack submit --auto`
- `gh stack merge <target> --yes`
- `gh stack checkout <target>`, and `up`, `down`, `top`, `bottom` instead of `switch`

Never run `gh stack modify`.

## Procedure

1. Plan the layers before writing code. A layer may depend only on its own branch and those below it, and no command reorders a stack in place. Add a layer for each new concern that builds on the last. Name branches `<topic>/<concern>` unless the repo has a convention. Unrelated work gets its own stack.
2. Create the stack, then commit each layer on its own branch. Stage with `git add <files>` so each commit lands in its owning layer.

   ```bash
   gh stack init billing/schema
   git add <files> && git commit -m "..."
   gh stack add billing/api
   git add <files> && git commit -m "..."
   ```

3. To change a lower layer, check out its branch, commit there, then run `gh stack rebase --upstack` and `gh stack top`. Do not commit a lower layer's work on the top branch.
4. When the user asks for PRs, run `gh stack submit --auto`. PRs open as drafts; `--open` opens them ready. Replace each generated title and body with text for that layer's diff, following the repo's PR template: `gh pr edit <n> --title "..." --body-file <file>`.
5. After a trunk change or a merge, run `gh stack sync`. Add `--prune` to delete merged local branches. `sync` does not create PRs, so run `submit` again after adding a layer. A non-interactive `sync` that finds diverged stacks exits 0 with `Sync aborted`: read `references/recovery.md`.
6. A rebase conflict exits 3. After `rebase`, fix the files, `git add` them, and run `gh stack rebase --continue`. After `sync`, branches are already restored: run `gh stack rebase` to reproduce the conflict, then continue the same way.
7. Merge only when the user asks. When no user can answer, stop after step 4.

   ```bash
   gh stack merge <pr-number> --yes --squash   # that PR and every unmerged PR below it
   ```

   The merge is all-or-nothing and requires every PR to be open and not a draft (`gh pr ready <n>`). Branch protection cannot be bypassed.

Done when `gh stack view --json` shows every branch with `needsRebase: false` and, after submit, a `pr` in state `OPEN`.

Read `references/recovery.md` for divergence, reordering or removing layers, exit codes 6 and 8, and branches managed outside `gh stack`.
