---
name: spec-to-tickets
description: Turn a reviewed spec into GitHub Issues, choosing a ticket shape sized to its scope.
argument-hint: "Path to the spec (optional if inferable from context)"
disable-model-invocation: true
---

# spec-to-tickets

Run `/spec-to-tickets` to turn a reviewed spec (the human-facing markdown a `spec` run produces) into GitHub Issues. It sits between `spec`, which produces the spec, and `dev-workflow`, which executes the work items.
This skill picks the ticket shape and the breakdown. Each issue is written and filed per `open-issue`.

Issues are external and hard to reverse, and other people see them. Run only on explicit request, and create nothing until the user confirms the proposed breakdown.

## Preflight

Run this every time, before anything else.

1. Confirm the target repo. Issues land in the current git repo's GitHub remote, which `gh` resolves automatically. If the working directory is not a GitHub repo, or the user wants a different repo, ask for the `owner/repo` and pass it with `--repo`.
2. Run `gh auth status`. If it fails, stop and tell the user to run `gh auth login`. Never guess a destination.
3. When both pass, read the spec and propose a ticket shape.

## Choosing the ticket shape

Read the whole spec, judge its scope, and pick one shape:

- Single issue: a small, self-contained spec such as a one-file bug fix. No parent, no children.
- A few flat issues: a handful of independent work items with no coordinating parent, created as siblings.
- Parent plus sub-issues: a large or multi-part spec (cross-file, cross-repo, staged rollout). The parent or epic captures the whole and each child captures one work item.

The signal is the spec's structure: the number of distinct work items under "Scope" and "Approach", whether it spans repos, and whether the steps have an ordering or dependencies a parent would coordinate.
Propose the shape with your reasoning. Decide a small or large spec without asking. When the weight is on the boundary (for example, three to five items that could be flat siblings or a small epic), present the candidates and let the user choose.

## Creating the issues

Write and create each issue per `open-issue`, which owns title, body, and label conventions. This skill owns only the shape and breakdown.

For every shape:

- Titles and bodies use the spec's ubiquitous-language terms verbatim, with no coined synonyms.
- An issue links the spec only when the spec is reachable (see Linking the spec).
- Nothing is created until the user confirms the shape and breakdown.

Without `open-issue`, create each issue with the `gh` CLI:

```bash
gh issue create --title "<title>" --body "<body>" --label "<label>"
```

Pass `--repo <owner/repo>` when filing against a repo other than the working directory's.

### Linking the spec

An issue references the spec only as a URL every reader of the issue can open. Link the human-facing spec and never the implementation plan, which lives at a scratch or git-ignored path and has no URL.

Verify the URL against the repo that holds the spec:

```bash
gh api "repos/<owner>/<repo>/contents/<path-from-repo-root>?ref=<default-branch>" -q .html_url
```

A returned `html_url` is the link, provided the issue's readers can read that repo. The call proves the file exists, not that they can see it.
Any other result means the spec is unreachable: it is outside any repo, uncommitted, or committed only on a branch that was never pushed.

Never substitute a path for the URL. A filesystem path, a workspace-relative path, a repo-relative path, or a bare filename resolves on one machine and tells other readers nothing.

When the spec is unreachable, omit the reference. The implementer works from the issue's own Problem and Acceptance criteria, which `open-issue` makes self-contained, so a linkless issue is complete.
When you propose the breakdown, say which issues carry a link, so the user sees the reference was decided and not forgotten.

### Parent and sub-issues

For the parent plus sub-issues shape, link the children with GitHub's native Sub-issues relationship, not a markdown checklist. The native link gives the parent a progress bar and Sub-issues panel and rolls child completion up to the parent.

1. Create the parent issue, then each child issue.
2. For each child, get its REST database id (the `id` field, not the issue number):

   ```bash
   child_id=$(gh api repos/<owner>/<repo>/issues/<child_number> -q .id)
   ```

3. Link it under the parent through the sub-issues endpoint:

   ```bash
   gh api --method POST repos/<owner>/<repo>/issues/<parent_number>/sub_issues -F sub_issue_id=$child_id
   ```

Do not use a `- [ ] #123` task list in the parent body. It creates no parent/child relationship and does not close the parent when the children close.

## Idempotency

After creating issues, write a "Tickets" section into the spec doc listing each work item with its issue URL.
On a re-run, read that section first, skip work items that already have an issue (or offer to update them), and create only the new ones. This prevents duplicate issues when a spec is ticketed twice.

## Scope

- Never commit, move, or publish the spec to manufacture a URL. Where the spec lives is the user's decision.
- This skill creates issues and does not execute them. `dev-workflow` executes them and references each issue in its commits and PR.
