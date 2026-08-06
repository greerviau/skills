---
name: open-issue
description: Use when filing a GitHub issue — standalone ("open an issue for this", "file a bug for X") or as the issue-first step before any code change. Checks for duplicates, honors `.github/ISSUE_TEMPLATE/`, writes a plain descriptive title and a short body (Problem, Reproduction, Acceptance criteria), and labels from the repo's real labels read with `gh label list`, then creates the issue. Trigger on "open an issue", "file a bug", "create a ticket for this", "write the issue for this work".
---

# open-issue

File a GitHub issue: write its title, body, and labels, then create it.
This is the single source of truth for issue conventions — invoked standalone, as the issue-first step of `dev-workflow`, or per-issue by `spec-to-tickets`.

## Preflight

1. **Verify auth** with `gh auth status`. If it fails, stop and tell the user to run `gh auth login`.
2. **Confirm the destination.** The issue lands in the current repo's GitHub remote, which `gh` resolves automatically. Pass `--repo <owner/repo>` to file against a different repo.
3. **Check for duplicates** before drafting:

   ```bash
   gh issue list --search "<key terms>" --state all --limit 20
   ```

   When an existing issue already covers it, say so and offer to comment on that one instead of filing a second.
4. **Read the repo's issue template** if `.github/ISSUE_TEMPLATE/` holds one that fits, and follow it, adding anything else valuable.

## Write the issue

**Title** — a plain descriptive sentence naming the observed problem or the requested change: `Worktree is removed while the PR is still open`.
No `feat(...)` prefix and no `[Bug]` tag: the type lives in the label, and conventional-commit form belongs on the commit and PR.

**Body** — one screen, roughly 200 words:

- **Problem / request** — what is wrong or what is wanted, and who it affects.
- **Reproduction** (bugs) — the smallest steps that trigger it, expected versus actual behavior, and the environment it shows up in.
- **Proposed approach** (optional) — one or two sentences, only where a direction is already known. Leave it out rather than guess; the issue states the problem, the spec or PR decides the solution.
- **Acceptance criteria** — a numbered list of what has to be true to close this. Concrete and checkable, not "works correctly". Numbered rather than checkboxes: nothing in the workflow ticks a box, and the numbers give `review`'s conformance pass a handle ("criterion 3 unmet").
- **Links** — the spec doc, related issues, the failing CI run, a log excerpt.

Cut background essays, alternatives considered, and speculation about the cause.
Use the terms the repo's glossary already names, verbatim (`standards`).

## Label from the repo's real labels

Read what exists rather than guessing at names:

```bash
gh label list --limit 100
```

Pick from that set: a type label (bug, feature, chore, or the repo's equivalent) plus any area or priority label that clearly applies.
Two or three labels beat a full sweep.

When nothing in the set fits, propose a new label with a name, color, and description, and create it only once the user confirms:

```bash
gh label create <name> --color <hex> --description "<description>"
```

## Create it

```bash
gh issue create --title "<title>" --body "<body>" --label "<label>,<label>"
```

Add `--assignee`, `--milestone`, or `--project` when the user names one.
Report the issue number and URL back: the number is what the branch and the PR's closing reference need.

**Nothing is created until the user confirms** the drafted title, body, and labels.
Per the interaction contract in `standards`, an autonomous run granted autonomy files without asking and records any assumption it had to make in the issue body.
