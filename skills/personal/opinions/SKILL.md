---
name: opinions
description: Use before making a subjective call the user may have a standing preference about. Reads ~/OPINIONS.md and offers to record new durable preferences.
---

# opinions

`~/OPINIONS.md` is the user's running record of opinions on how to build things.

## Before choosing a default

For a judgment call where the user's opinion matters (UI/UX conventions, tooling choices, code style, workflow shape), read `~/OPINIONS.md` first and follow any entry that applies.
Entries are durable defaults for their stated domain. Apply them without being asked again.

If the document is silent on the situation and the answer is ambiguous, ask the user. Do not infer an opinion that is not written down.

## When the user states an opinion

If the user states an opinion that generalizes beyond the current task (a preference, a correction, "no, do it this way"), ask whether to record it in `~/OPINIONS.md`. Never add one without confirmation.

To add an entry:

- Create `~/OPINIONS.md` with a short header if it does not exist.
- File the entry under its section (for example `## UI/UX`), or create a section for a new domain.
- Write a direct, standalone rule someone could follow without extra context. Include the reasoning when it clarifies where the rule applies.
