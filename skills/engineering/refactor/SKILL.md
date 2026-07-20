---
name: refactor
description: Use when improving the structure of working code without changing its behavior — reducing duplication, clarifying names, simplifying control flow, aligning with conventions — guarded by an unchanged test suite. Adds characterization tests first when coverage is thin, refactors in small behavior-preserving steps, and lands via dev-workflow. Trigger on "clean this up", "refactor this", "reduce duplication", "simplify this code", "tidy up", "make this more maintainable".
---

# refactor

Improve the structure of working code without changing its behavior — reduce duplication, clarify naming, simplify control flow, align with conventions. **Behavior preservation is the hard invariant**, and an unchanged, passing test suite is the proof.

This is a deliberate, test-guarded pass you can point at any code, distinct from the one-shot `/simplify` on the current diff. Any change that alters observable behavior is out of scope: that's a feature (`dev-workflow`) or a fix (`debug`), not a refactor.

## Procedure

1. **Establish a safety net.** Confirm the affected code has passing tests that cover the behavior you're about to restructure. If coverage is thin, write **characterization tests** capturing the current behavior *before* touching structure — you can't preserve what you haven't pinned down.
2. **Refactor in small behavior-preserving steps.** Keep the tests green throughout. No functional change rides along. If a bug surfaces mid-refactor, flag it for a separate branch — do not fix it here, because a behavior change hidden inside a refactor is exactly what this skill exists to prevent.
3. **Validate.** Full test suite green and unchanged in intent; lint clean; `verify` the runtime surface if there is one.
4. **Land via `dev-workflow`.** Isolated worktree, staged commits, and a PR whose description makes the behavior-preserving guarantee explicit (so a reviewer knows to check *nothing changed*, not *what changed*).

## Boundaries

- Behavior is the invariant. If observable behavior must change, it's not this skill.
- Don't smuggle fixes or features into a refactor. Flag them; land them separately.
- The test suite is the contract. If you can't prove behavior is preserved, add the tests that would prove it before proceeding.
