---
name: refactor
description: >-
  Use when restructuring working code while preserving observable behavior, including deduplication, renaming, and control-flow simplification.
  Trigger on "refactor", "clean up this code", "reduce duplication", and "make this more maintainable".
  Exclude behavior changes and prose cleanup.
---

# refactor

Improve the structure of working code without changing its behavior: reduce duplication, clarify names, simplify control flow, align with conventions.
Observable behavior must not change, and an unchanged passing test suite is the proof.

This is a test-guarded pass over any code you point it at, not a cleanup of the current diff.
A change to observable behavior is feature work or a fix and is out of scope.

## Procedure

1. Confirm the affected code has passing tests covering the behavior you will restructure. If coverage is thin, write **characterization tests** that capture current behavior before changing structure.
2. Refactor in small steps, keeping tests green throughout. If you find a bug, leave it unfixed, list it for the user, and ask whether to open a GitHub issue for it. When no user can answer, list it in the PR description.
3. Validate: the full suite passes with unchanged intent, lint is clean, and the runtime surface works through its real entry point if there is one.
4. Land the change through the normal PR process. The PR description states that behavior is preserved, so the reviewer checks that nothing changed.

If you cannot prove behavior is preserved, add the tests that would prove it first.
