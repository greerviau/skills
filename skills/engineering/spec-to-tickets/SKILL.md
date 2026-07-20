---
name: spec-to-tickets
description: Use when turning a reviewed spec into tickets in your tracker — explicitly, never automatically, since it creates work items other people see. Requires a configured tracker (.claude/ticket-tracker.yml in the repo, or ~/.claude/ticket-tracker.yml globally) and refuses to run without one. Reads the spec, judges its scope to pick a ticket shape (a single ticket, a few flat tickets, or a parent with sub-issues) using the spec's own vocabulary and asking when the shape is ambiguous, creates them in GitHub Issues / Linear / Trello via the configured adapter, and records the ticket IDs back in the spec so re-runs don't duplicate. Trigger on "/spec-to-tickets", "turn this spec into tickets", "create tickets/issues for this plan", "file tickets for this".
---

# spec-to-tickets

Turn a reviewed spec (the markdown a `spec` run produces) into concrete tickets in the user's tracker. This skill sits between `spec` and `dev-workflow`: `spec` produces the plan, `spec-to-tickets` breaks it into trackable work items, `dev-workflow` executes them.

**This skill is explicit.** It creates external, hard-to-reverse artifacts that other people see, so it never fires on its own and never creates anything before the user confirms the proposed breakdown. It also **hard-requires a configured tracker** — its first action is a preflight that stops if none is set.

## Preflight (do this first, every time)

1. **Resolve the tracker config**, in order:
   - Repo-scoped: `.claude/ticket-tracker.yml` at the repo root (primary — trackers are almost always project-scoped).
   - Global fallback: `~/.claude/ticket-tracker.yml`.

   If neither exists, **stop** and tell the user to create one — show the shape below. Do not assume a tracker or fall back to a default.
2. **Verify auth** for the resolved tracker (`gh auth status` for GitHub; `LINEAR_API_KEY` or the Linear MCP server; `TRELLO_KEY`/`TRELLO_TOKEN` for Trello). If auth is missing, **stop** and tell the user what to set.
3. Only once both pass, read the spec and propose a ticket shape.

### Tracker config shape

```yaml
tracker: github            # github | linear | trello
github:
  repo: owner/repo         # for gh issue create
linear:
  team: ENG                # team key; auth via LINEAR_API_KEY env or the Linear MCP server
trello:
  board_id: abc123         # auth via TRELLO_KEY / TRELLO_TOKEN env
```

Only the block matching `tracker:` is required. Secrets live in env vars, never in the file. The global `~/.claude/ticket-tracker.yml` should be kept out of version control.

## Choosing the ticket shape

The output shape is **driven by the spec's scope**, not a fixed template. Read the whole spec, judge its weight, and pick one:

- **Single ticket** — a small, self-contained spec (a one-file bug fix, a lone change). One issue captures it; no parent, no children.
- **A few flat tickets** — a handful of independent work items that don't need a coordinating parent. Create them as siblings.
- **Parent + sub-issues** — a large or multi-part spec (cross-file, cross-repo, staged rollout). A parent/epic captures the whole; children capture each work item.

**Deciding.** The signal comes from the spec's own structure: the number of distinct work items under "Scope" and "Approach / design", whether it spans multiple repos, and whether the steps have ordering/dependencies a parent would coordinate. Propose the shape with your reasoning.

**Ambiguity → ask.** A clearly-small or clearly-large spec is decided without a question. When the weight genuinely sits on the boundary (e.g. three-to-five loosely related items that could be flat siblings *or* a small epic), present the candidate shapes and let the user choose before creating anything.

## Creating the tickets

Regardless of shape:

- **Titles and bodies use the spec's ubiquitous-language terms, verbatim** — no coined synonyms.
- **Every ticket links back to the spec document.**
- **Nothing is created until the user confirms** the proposed shape and breakdown.

Create via the adapter matching the config's `tracker:` value. The flow is identical across trackers; only the mechanics differ.

### Adapter: GitHub Issues

Deterministic via the `gh` CLI. For each ticket:

```bash
gh issue create --repo <owner/repo> --title "<title>" --body "<body linking the spec>"
```

For a parent + sub-issues shape, create the parent first, then reference its number from each child (and, where the repo uses task lists, check the children off in the parent body).

### Adapter: Linear

Use the Linear MCP server if present; otherwise a Linear API call with `LINEAR_API_KEY`. Create issues under the configured `team`. Model parent + sub-issues with Linear's parent/sub-issue relation.

### Adapter: Trello

Use the Trello API with `TRELLO_KEY`/`TRELLO_TOKEN` on the configured `board_id`. Model a flat set as cards on a list; model parent + children as a card with a checklist, or an epic card plus child cards, per the board's convention.

## Idempotency

After creating tickets, write a **"Tickets" section back into the spec doc** listing each work item → its ticket ID/URL. On a re-run, read that section first: skip work items that already have a ticket (or offer to update them), and create only the new ones. This prevents the duplicate-flood failure mode of re-running against an already-ticketed spec.

## Boundaries

- Explicit only — never auto-fire, never create before the user confirms.
- No configured tracker, or missing auth → stop and instruct. Never guess a destination.
- The tracker is data (the config value), not branches hardcoded here. Add a tracker by adding an adapter, not by rewriting the flow.
- Creates tickets; does not execute them — that's `dev-workflow`, which references each ticket in its commits and PR.
