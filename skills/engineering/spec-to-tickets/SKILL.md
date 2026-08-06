---
name: spec-to-tickets
description: Turn a reviewed spec into GitHub Issues, choosing a ticket shape sized to its scope.
argument-hint: "Path to the spec (optional if inferable from context)"
disable-model-invocation: true
---

# spec-to-tickets

Turn a reviewed spec (the markdown a `spec` run produces) into GitHub Issues. Sits between `spec` (produces the plan) and `dev-workflow` (executes the work items).
Judges the ticket shape and the breakdown; each individual issue is written and filed per `open-issue`.

**This skill is explicit** — it creates external, hard-to-reverse artifacts other people see. Never fire on your own; never create anything before the user confirms the proposed breakdown.

## Preflight (do this first, every time)

1. **Confirm the target repo.** Issues land in the current git repo's GitHub remote, which `gh` resolves automatically. If the working directory isn't a GitHub repo, or the user wants issues filed against a different repo, ask for the `owner/repo` and pass it with `--repo`.
2. **Verify auth** with `gh auth status`. If it fails, **stop** and tell the user to run `gh auth login`.
3. Only once both pass, read the spec and propose a ticket shape.

## Choosing the ticket shape

The shape is **driven by the spec's scope**, not a fixed template. Read the whole spec, judge its weight, and pick one:

- **Single issue** — a small, self-contained spec (a one-file bug fix). No parent, no children.
- **A few flat issues** — a handful of independent work items with no coordinating parent. Create them as siblings.
- **Parent + sub-issues** — a large or multi-part spec (cross-file, cross-repo, staged rollout). A parent/epic captures the whole; children capture each work item.

The signal comes from the spec's own structure: the number of distinct work items under "Scope" and "Approach / design", whether it spans multiple repos, and whether the steps have ordering/dependencies a parent would coordinate. Propose the shape with your reasoning. Decide a clearly-small or clearly-large spec without asking; when the weight sits on the boundary (e.g. three-to-five items that could be flat siblings *or* a small epic), present the candidates and let the user choose.

## Creating the issues

Write and create each issue per the `open-issue` skill, which owns the title, body, and label conventions — a plain descriptive title, a short problem/acceptance-criteria body, labels picked from the repo's real labels. This skill owns only the shape and the breakdown.

Regardless of shape:

- **Titles and bodies use the spec's ubiquitous-language terms, verbatim** — no coined synonyms.
- **Every issue links back to the spec document.**
- **Nothing is created until the user confirms** the proposed shape and breakdown.

Without `open-issue`, create each with the `gh` CLI directly:

```bash
gh issue create --title "<title>" --body "<body linking the spec>" --label "<label>"
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
- Owns shape and breakdown, not issue conventions — those live in `open-issue`.
- Creates issues; does not execute them — that's `dev-workflow`, which references each issue in its commits and PR.
