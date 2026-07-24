---
name: spec-to-tickets
description: Use when turning a reviewed spec into GitHub Issues — explicitly, never automatically, since it creates work items other people see. Reads the spec, judges its scope to pick a ticket shape (a single issue, a few flat issues, or a parent with sub-issues) using the spec's own vocabulary and asking when the shape is ambiguous, creates them with the `gh` CLI, and records the issue URLs back in the spec so re-runs don't duplicate. Trigger on "/spec-to-tickets", "turn this spec into tickets", "create tickets/issues for this plan", "file issues for this".
---

# spec-to-tickets

Turn a reviewed spec (the markdown a `spec` run produces) into GitHub Issues. This skill sits between `spec` and `dev-workflow`: `spec` produces the plan, `spec-to-tickets` breaks it into trackable work items, `dev-workflow` executes them.

**This skill is explicit.** It creates external, hard-to-reverse artifacts that other people see, so it never fires on its own and never creates anything before the user confirms the proposed breakdown.

## Preflight (do this first, every time)

1. **Confirm the target repo.** Issues land in the current git repo's GitHub remote, which `gh` resolves automatically. If the working directory isn't a GitHub repo, or the user wants issues filed against a different repo, ask for the `owner/repo` and pass it with `--repo`.
2. **Verify auth** with `gh auth status`. If it fails, **stop** and tell the user to run `gh auth login`.
3. Only once both pass, read the spec and propose a ticket shape.

## Choosing the ticket shape

The output shape is **driven by the spec's scope**, not a fixed template. Read the whole spec, judge its weight, and pick one:

- **Single issue** — a small, self-contained spec (a one-file bug fix, a lone change). One issue captures it; no parent, no children.
- **A few flat issues** — a handful of independent work items that don't need a coordinating parent. Create them as siblings.
- **Parent + sub-issues** — a large or multi-part spec (cross-file, cross-repo, staged rollout). A parent/epic issue captures the whole; children capture each work item.

**Deciding.** The signal comes from the spec's own structure: the number of distinct work items under "Scope" and "Approach / design", whether it spans multiple repos, and whether the steps have ordering/dependencies a parent would coordinate. Propose the shape with your reasoning.

**Ambiguity → ask.** A clearly-small or clearly-large spec is decided without a question. When the weight genuinely sits on the boundary (e.g. three-to-five loosely related items that could be flat siblings *or* a small epic), present the candidate shapes and let the user choose before creating anything.

## Creating the issues

Regardless of shape:

- **Titles and bodies use the spec's ubiquitous-language terms, verbatim** — no coined synonyms.
- **Every issue links back to the spec document.**
- **Nothing is created until the user confirms** the proposed shape and breakdown.

Create with the `gh` CLI. For each issue:

```bash
gh issue create --title "<title>" --body "<body linking the spec>"
```

Pass `--repo <owner/repo>` when filing against a repo other than the working directory's.

### Parent + sub-issues: use GitHub's native Sub-issues

For a parent + sub-issues shape, wire the children with GitHub's **native Sub-issues relationship**, not a plain markdown checklist. The native link gives the parent a real progress bar and Sub-issues panel, and rolls child completion up to the parent.

1. Create the parent issue, then each child issue.
2. For each child, resolve its REST database id (this is the `id` field, **not** the issue number):

   ```bash
   child_id=$(gh api repos/<owner>/<repo>/issues/<child_number> -q .id)
   ```

3. Link it under the parent via the sub-issues endpoint:

   ```bash
   gh api --method POST repos/<owner>/<repo>/issues/<parent_number>/sub_issues -F sub_issue_id=$child_id
   ```

Do not fall back to a `- [ ] #123` task list in the parent body — the markdown checklist does not create the real parent/child relationship and does not close the parent when the children close.

## Idempotency

After creating issues, write a **"Tickets" section back into the spec doc** listing each work item → its issue URL. On a re-run, read that section first: skip work items that already have an issue (or offer to update them), and create only the new ones. This prevents the duplicate-flood failure mode of re-running against an already-ticketed spec.

## Boundaries

- Explicit only — never auto-fire, never create before the user confirms.
- Missing auth → stop and instruct (`gh auth login`). Never guess a destination.
- Creates issues; does not execute them — that's `dev-workflow`, which references each issue in its commits and PR.
