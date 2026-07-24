---
name: debug
description: Use when something is broken and the cause is unknown — a failing test, a crash, wrong output, a user-reported bug. Reproduces the bug end-to-end the way a user hits it before forming any fix hypothesis, localizes the root cause, and proves it with the reproduction. Trigger on "why is this failing", "reproduce this bug", "track down", "debug this", "what's causing", "it's broken when".
---

# debug

Turn a bug report into a confirmed root cause. The defining rule: **reproduce the bug end-to-end, as close to how a user hits it as possible, before forming any fix hypothesis** — a fix built on a red reproduction targets what's actually broken, not a guessed symptom.

This skill finds and proves the cause. Landing the fix is a separate step — do it however you normally land changes (the `dev-workflow` skill, if you use it).

## Procedure

1. **Reproduce.** Build the smallest reliable reproduction that drives the real entry point (CLI, endpoint, UI flow), not a convenient unit. This is the anchor for everything that follows. If the bug can't be reproduced, that *is* the finding — report what was tried and ask for the missing detail (environment, inputs, version) rather than guessing at a fix.
2. **Localize.** With a red reproduction, narrow to the root cause: bisect history, add instrumentation, read the failing path. Distinguish symptom (what the user sees) from cause (why it happens).
3. **Confirm.** State the root cause plainly and explain how the reproduction proves it — "the reproduction fails here because of this, and would pass if this were correct," not "this is probably it."
4. **Fix (only if asked).** Land the fix however you normally land changes (the `dev-workflow` skill, if you use it): the reproduction becomes an E2E-weighted regression test so the bug can't return silently.

## Boundaries

- Don't fix a bug you haven't reproduced. A green reproduction after the change is the evidence the fix worked.
- Don't inline worktree/commit/PR mechanics — landing the fix is a separate step.
- Flag unrelated bugs found while localizing for their own branch.
