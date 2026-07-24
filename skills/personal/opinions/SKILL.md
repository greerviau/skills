---
name: opinions
description: Use whenever a task involves a subjective or stylistic call the user has likely already formed a view on — UI/UX conventions, tooling choices, code style, workflow preferences — before deciding on your own default. Reads ~/OPINIONS.md for standing guidance, and offers to record any new opinion the user states mid-task so the document keeps growing. Trigger before making a judgment call in an area covered by ~/OPINIONS.md, and whenever the user gives feedback that reads as a general opinion rather than a one-off instruction.
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
