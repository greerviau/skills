---
name: debug
description: Use when something is broken and the cause is unknown — a failing test, a crash, wrong output, a user-reported bug. Reproduces the bug end-to-end the way a user hits it before forming any fix hypothesis, localizes the root cause, and proves it with the reproduction; hands off to dev-workflow to land the fix as a regression-tested change. Trigger on "why is this failing", "reproduce this bug", "track down", "debug this", "what's causing", "it's broken when".
---

# debug

Turn a bug report into a confirmed root cause. The defining rule: **reproduce the bug end-to-end, as close to how a user hits it as possible, before forming any fix hypothesis.** A fix built on a guessed cause tends to address a symptom the real bug doesn't even go through; a fix built on a red reproduction addresses the thing that is actually broken.

This skill finds and proves the cause. Landing the fix is `dev-workflow`'s job — `debug` composes with it rather than opening worktrees or PRs itself.

## Procedure

1. **Reproduce.** Build the smallest reliable reproduction that exercises the bug the way an end user does — drive the real entry point (the CLI, the endpoint, the UI flow), not an isolated unit picked because it's convenient. The reproduction is the anchor for everything that follows.
   - If the bug can't be reproduced, that *is* the finding. Report what was tried and what's missing, and ask for the detail needed (environment, inputs, version) rather than guessing at a fix.
2. **Localize.** With a red reproduction in hand, narrow to the root cause: bisect the change history, add instrumentation, read the failing path. Distinguish the *symptom* (what the user sees) from the *cause* (why it happens).
3. **Confirm.** State the root cause plainly and explain how the reproduction proves it — not "this is probably it" but "the reproduction fails here because of this, and would pass if this were correct."
4. **Fix (only if asked).** Hand off to the `dev-workflow` skill:
   - The fix lands on an isolated worktree.
   - The reproduction becomes a regression test (E2E-weighted, per house style), so the bug can't return silently.
   - It goes through the normal validate → PR → CI flow.

## Boundaries

- `debug` proves the cause; `dev-workflow` lands the change. Don't inline worktree/commit/PR mechanics here.
- Don't fix a bug you haven't reproduced. A green reproduction after the change is the evidence the fix worked.
- If unrelated bugs surface while localizing, flag them for their own branch — don't fold them into this investigation.
