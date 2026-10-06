---
name: open-issue
description: Use when filing a GitHub issue, either standalone ("open an issue for this", "file a bug for X") or as the issue-first step before any code change. Checks for duplicates, honors `.github/ISSUE_TEMPLATE/`, writes a plain descriptive title and a short body (Problem, Reproduction, Acceptance criteria), and labels from the repo's real labels read with `gh label list`, then creates the issue. Trigger on "open an issue", "file a bug", "create a ticket for this", "write the issue for this work".
---

# open-issue

File a GitHub issue: write its title, body, and labels, then create it.
This skill is the single source of truth for issue conventions, whether invoked directly, as the issue-first step of `dev-workflow`, or per issue by `spec-to-tickets`.

## Preflight

1. Run `gh auth status`. If it fails, stop and tell the user to run `gh auth login`.
2. The issue lands in the current repo's GitHub remote, which `gh` resolves automatically. Pass `--repo <owner/repo>` to file against another repo.
3. Check for duplicates before drafting:

   ```bash
   gh issue list --search "<key terms>" --state all --limit 20
   ```

   If an existing issue covers it, say so and offer to comment there instead of filing a second.
4. If `.github/ISSUE_TEMPLATE/` holds a template that fits, read it and follow it, keeping any section below that it lacks.

## Write the issue

Title: a plain descriptive sentence naming the observed problem or requested change, such as `Worktree is removed while the PR is still open`.
Use no `feat(...)` prefix and no `[Bug]` tag. The type goes in the label, and conventional-commit form belongs on the commit and PR.

Body: human-facing, held to the budget and cuts in *Artifact audience* (`standards`).

- Problem / request: what is wrong or wanted, and who it affects.
- Reproduction (bugs): the smallest steps that trigger it, expected versus actual behavior, and the environment.
- Proposed approach (optional): one or two sentences, only where a direction is already known. Otherwise omit it; the issue states the problem and the spec or PR decides the solution.
- Acceptance criteria: a numbered list of what must be true to close the issue. Each is concrete and checkable ("works correctly" is not). Use numbers, not checkboxes, because nothing in the workflow ticks a box and numbers let `review`'s conformance pass cite "criterion 3 unmet".
- Links: the spec doc, related issues, the failing CI run, a log excerpt.

Cut speculation about the cause.
Use the repo glossary's terms verbatim (`standards`).

## Labels

Read the existing labels instead of guessing names:

```bash
gh label list --limit 100
```

Pick a type label (bug, feature, chore, or the repo's equivalent) plus any area or priority label that applies. Two or three labels are enough.

When none fits, propose a new label with a name, color, and description, and create it only after the user confirms:

```bash
gh label create <name> --color <hex> --description "<description>"
```

## Create it

Run the concision pass (`standards`) over the drafted body unless it is well inside the budget, and apply the result. The pass leaves acceptance criteria alone.

```bash
gh issue create --title "<title>" --body "<body>" --label "<label>,<label>"
```

Add `--assignee`, `--milestone`, or `--project` when the user names one.
Report the issue number and URL. The branch and the PR's closing reference need the number.

Create nothing until the user confirms the title, body, and labels.
When no user can answer (`standards`), file without asking and record any assumption in the issue body.
