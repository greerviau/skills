---
name: opinions
description: Use before making a subjective call the user may have a standing preference about. Reads ~/OPINIONS.md and offers to record new durable preferences.
---

# opinions

`~/OPINIONS.md` is the user's running record of opinions on how to build things — an evolving document, not a fixed spec.

## Before deciding on your own default

When a task involves a judgment call that benefits from the user's informed opinion (UI/UX conventions, tooling choices, code style, workflow shape, etc.), read `~/OPINIONS.md` first and follow any guidance that applies.

- **Don't infer an opinion that isn't written down.** If the document is silent on the specific situation and it's genuinely ambiguous, ask the user rather than guessing what they'd want.
- Treat entries as durable defaults for their stated domain, not one-off notes — apply them without being asked again.

## When the user gives an opinion mid-task

If the user states an opinion that generalizes beyond the immediate task — a preference, a correction, a "no, do it this way" — ask whether to capture it in `~/OPINIONS.md`. Confirm first; never add unprompted.

When adding an entry:
- Create `~/OPINIONS.md` with a short header if it doesn't exist yet.
- File it under the section it belongs to (e.g. `## UI/UX`), or create a new section for a new domain.
- Write it as a direct, standalone rule someone else could follow without extra context — include the reasoning if it clarifies when the rule applies.
