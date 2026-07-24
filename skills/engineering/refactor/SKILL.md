---
name: refactor
description: Use when improving the structure of working code without changing its behavior — reducing duplication, clarifying names, simplifying control flow, aligning with conventions — guarded by an unchanged test suite. Adds characterization tests first when coverage is thin, then refactors in small behavior-preserving steps. Trigger on "clean this up", "refactor this", "reduce duplication", "simplify this code", "tidy up", "make this more maintainable".
---

# refactor

Improve the structure of working code without changing its behavior — reduce duplication, clarify naming, simplify control flow, align with conventions. **Behavior preservation is the hard invariant**, and an unchanged, passing test suite is the proof.

This is a deliberate, test-guarded pass you can point at any code, distinct from the one-shot `/simplify` on the current diff. Any change to observable behavior is out of scope — that's feature work or a fix (`debug`).

## Procedure

1. **Establish a safety net.** Confirm the affected code has passing tests covering the behavior you're about to restructure. If coverage is thin, write **characterization tests** capturing current behavior *before* touching structure.
2. **Refactor in small behavior-preserving steps.** Keep tests green throughout; no functional change rides along. If a bug surfaces mid-refactor, flag it for a separate branch — don't fix it here.
3. **Validate.** Full suite green and unchanged in intent; lint clean; `verify` the runtime surface if there is one.
4. **Land the change** however you normally do (the `dev-workflow` skill, if you use it), with a PR description that makes the behavior-preserving guarantee explicit — so a reviewer checks *nothing changed*.

## Boundaries

- Behavior is the invariant. If observable behavior must change, it's not this skill.
- Don't smuggle fixes or features into a refactor — flag them, land them separately.
- If you can't prove behavior is preserved, add the tests that would prove it first.
