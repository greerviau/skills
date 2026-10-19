---
name: stack-prs
description: Use when splitting work into dependent pull requests, or when a stack is checked out. Builds, submits, syncs, and merges GitHub stacked PRs with the `gh stack` extension. Trigger on "stack these PRs", "split this into a stack", "dependent PRs", "stacked PRs", "gh stack".
---

# stack-prs

Build dependent pull requests as a GitHub **stack**: an ordered chain of branches where each branch has one PR based on the branch below it, and the bottom branch is based on the trunk (usually `main`).
Create and change the chain only with `gh stack` commands.
Do not set PR base branches by hand, and do not use `gh pr merge` on a stack PR.

`gh stack view` prints the stack bottom first: `(main) <- auth <- api <- frontend`.
`auth` merges first.
`up` moves toward the top, `down` toward the trunk.

## Preflight

1. Run `gh extension list`. If `github/gh-stack` is missing, run `gh extension install github/gh-stack`. The extension needs `gh` 2.90.0 or later and Git 2.36 or later.
2. Run `git config rerere.enabled true` so conflict resolutions replay across layers.
3. If the repo has more than one remote, run `git config remote.pushDefault origin`, or pass `--remote <name>` to every `push`, `submit`, `sync`, `rebase`, and `link`.
4. Run `gh stack view --json`. Exit code 2 means no stack is checked out. Exit code 9 means stacked PRs are not enabled on the repository, so tell the user and stop.

Stacks require every branch in one repository. Fork-based stacks are not supported.

## Interactive commands

`gh stack` opens prompts and full-screen editors when stdout is a TTY, and the harness may allocate one.
Use the non-interactive form of each command:

| Use | Instead of | Reason |
|---|---|---|
| `gh stack view --json` | `gh stack view` | opens a TUI |
| `gh stack init <branch>...` | `gh stack init` | prompts for names |
| `gh stack add <branch>` | `gh stack add` | prompts for a name |
| `gh stack submit --auto` | `gh stack submit` | opens an editor |
| `gh stack merge <target> --yes` | `gh stack merge` | opens a wizard |
| `gh stack checkout <target>` | `gh stack checkout` | opens a menu |
| `gh stack up`, `down`, `top`, `bottom` | `gh stack switch` | `switch` is menu-only |

Do not run `gh stack modify`.
It has no non-interactive path.

## 1. Plan the layers

Write the layer list before writing code, then put each layer's code on its own branch.
Code in one layer may depend only on its own branch and the branches below it.
No command reorders a stack in place, so a wrong order means rebuilding it (see `references/recovery.md`).

Add a layer when the next change is a different concern that depends on what exists: backend to frontend, core logic to tests, or a diff already large enough to review alone.
A layer that takes more than one sentence to describe is two layers.
Unrelated work gets a separate stack.

Name branches `<topic>/<concern>`, such as `billing/schema`, `billing/api`, `billing/ui`.
A repo or user branch convention overrides this.
Names are used verbatim.

When the work already exists as uncommitted changes, create the stack first and stage each layer's files separately.
`gh stack add <branch>` leaves the working tree untouched, so uncommitted changes carry into the new branch.

Done when the layer list names the branch and one-sentence purpose of every layer.

## 2. Build the stack

```bash
gh stack init billing/schema        # creates and checks out the first branch
git add <files> && git commit -m "..."
gh stack add billing/api            # next layer, branched from the current one
git add <files> && git commit -m "..."
```

Use `git add` and `git commit` instead of `gh stack add -Am` so each commit lands in the layer that owns it.
Several commits per layer are fine.

To change an earlier layer, check out the layer that owns the change, commit there, then replay everything above it:

```bash
gh stack checkout billing/schema    # or: gh stack down
git add <files> && git commit -m "..."
gh stack rebase --upstack
gh stack top
```

Never commit a lower layer's concern on the top branch.

Done when `gh stack view --json` lists every layer in order and every branch reports `needsRebase: false`.

## 3. Submit

```bash
gh stack submit --auto
```

This pushes every branch, opens one PR per layer with the correct base, and links the PRs as a stack on GitHub.
New PRs open as drafts.
Pass `--open` to open them ready for review.
Create PRs only when the user asked for them.

`submit` generates titles and bodies from the commits.
Replace each with text that covers only that layer's diff and follows the repo's PR template and title convention:

```bash
gh pr edit <number> --title "..." --body-file <file>
```

Do not repeat the other layers' content in a body.
GitHub shows the stack's order and links on every PR.

Done when `gh stack view --json` shows a `pr` with state `OPEN` on every branch.

## 4. Keep the stack current

Run `gh stack sync` after a trunk change, after any PR in the stack merges, and before resuming work on an older stack.
It fetches, pulls down branches for PRs added on GitHub, fast-forwards trunk, rebases every layer, pushes with `--force-with-lease`, and refreshes PR state.
It handles squash merges by rebasing the remaining layers onto the new trunk.
Add `--prune` to delete local branches of merged PRs.

`sync` never creates PRs.
`gh stack submit --auto` after adding a layer creates the PR for the new layer.

A rebase conflict exits 3:

- After `gh stack sync`, every branch is already restored. Run `gh stack rebase` to reproduce the conflict.
- After `gh stack rebase`, resolve the listed files, run `git add <files>`, then `gh stack rebase --continue`. Repeat until it completes. `gh stack rebase --abort` restores every branch in the stack.

A non-interactive `sync` that finds the local and GitHub stacks diverged changes nothing and exits 0 with `Sync aborted`.
Read the output for that message, then follow `references/recovery.md`.

After any local change, run `gh stack push` to push the active branches without touching PRs.

## 5. Merge

Merge only when the user asks. When no user can answer, stop after step 3.

```bash
gh stack merge <pr-number> --yes --squash   # that PR and every unmerged PR below it
gh stack merge <stack-number> --yes         # the whole stack
```

The merge is all-or-nothing: if any PR in the set cannot merge, none merge.
Each PR must be open and not a draft, so run `gh pr ready <number>` on drafts first.
Branch protection and repository rules apply to every PR in the stack and cannot be bypassed.
Without a method flag, the command reuses the last method used.
Pass `--squash`, `--merge`, or `--rebase` to set it.
When the base branch uses a merge queue, the stack joins the queue and the queue chooses the method.

PRs above the merged set stay open and retarget the trunk.
Run `gh stack sync` afterward.

Done when `gh stack view --json` reports `isMerged: true` for every merged layer.

## Reference

`gh stack <command> --help` lists the flags of the installed version.
Read `references/recovery.md` when `sync` aborts on divergence, when the layer order or membership must change, when a command exits 6 or 8, or when branches are managed with another tool such as Jujutsu, Sapling, or git-town.
