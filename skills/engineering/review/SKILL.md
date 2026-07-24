---
name: review
description: Use when reviewing changes before they land — a working-tree diff, a branch, or a GitHub PR — against the user's own engineering standards (lint clean, tests present and green, no flakiness, simplicity and correctness over development cost). Complements the built-in code review by adding the standards layer and flagging incidental lint/test/flakiness defects even when unrelated. Trigger on "review this", "review my changes", "look over this PR", "check this before I push", "is this ready to ship".
---

# review

Review a diff, branch, or PR against a specific engineering bar — not a generic checklist. This skill encodes standards so they get applied consistently: lint must be clean, tests must exist and pass, flakiness is a defect, and correctness/simplicity/maintainability outweigh development cost.

It **complements** the built-in `/code-review` (which hunts correctness bugs) by adding the standards layer and the "fix it even if incidental" rule. It reviews and reports; it does not land changes.

## Procedure

1. **Scope the diff.** Identify exactly what changed — working tree, branch vs. its base, or a GitHub PR. Review that, not the whole codebase.
2. **Correctness pass.** Defer to `/code-review` for deep bug-hunting where it helps; summarize its findings rather than re-deriving them by hand.
3. **Standards pass.** Check the change against the bar defined in the `standards` skill — lint clean, E2E-weighted tests that pass and exercise the change, no flakiness, simplicity over the cheapest path, ubiquitous-language terms used verbatim, and the touched documentation surface audited (the `doc-audit` skill).
4. **Incidental-defect rule.** If a lint error, test failure, or flakiness is spotted — *even when unrelated to the change under review* — flag it. Note that it belongs on its own branch, not folded into this one (see branch hygiene in `standards`).
5. **Report.** Findings ranked most-severe first, each concrete and actionable, ending in a clear ship / don't-ship call.

**Interaction mode** (see `standards`): interactively, the report ends in a conversational ship / don't-ship call. Run autonomously (as a gate in a runner), emit a machine-consumable verdict plus the ranked findings list so the caller can gate on it, rather than a conversational exchange.

## Boundaries

- Reviews and reports only. If asked to apply findings, hand off to `dev-workflow`.
- Incidental defects get flagged, not fixed in place — surfacing them is the job here; fixing them is separate work.
