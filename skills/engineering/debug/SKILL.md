---
name: debug
description: Use when something is broken and the cause is unknown (a failing test, a crash, wrong output, a user-reported bug). Reproduces the bug end-to-end the way a user hits it before forming any fix hypothesis, localizes the root cause, and proves it with the reproduction. Trigger on "why is this failing", "reproduce this bug", "track down", "debug this", "what's causing", "it's broken when".
---

# debug

Turn a bug report into a confirmed root cause.
Reproduce the bug end to end, as a user hits it, before forming any fix hypothesis. A fix built on a red reproduction targets the real defect instead of a guessed symptom.

This skill finds and proves the cause. Landing the fix is a separate step (the `dev-workflow` skill, if you use it).

## Procedure

1. Reproduce. Build the smallest reliable reproduction that drives the real entry point (CLI, endpoint, UI flow), not a convenient unit. If the bug does not reproduce, report what you tried and ask for the missing detail (environment, inputs, version) instead of guessing at a fix.
2. Localize. With the reproduction red, narrow to the root cause: bisect history, add instrumentation, read the failing path. Separate the symptom (what the user sees) from the cause (why it happens).
3. Confirm. State the root cause and how the reproduction proves it: the reproduction is red at this point because of this cause, and would go green if the cause were corrected.
4. Fix, only if asked. The reproduction becomes an E2E-weighted regression test, and the fix lands through your normal process.

Do not fix a bug you have not reproduced. A green reproduction after the change is the evidence the fix worked.
Flag unrelated bugs found while localizing for their own branch.

A reproduction here is a red test, as in `tdd`. This skill handles reports of broken behavior and `tdd` handles requests for new behavior.
