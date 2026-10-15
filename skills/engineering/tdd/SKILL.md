---
name: tdd
description: Use whenever implementing or changing behavior in code, including every feature and bug fix - write the failing test first, confirm it fails for the right reason, then the minimum code to green, then refactor. Trigger on "TDD this", "test-drive this", "write the test first", "red, green, refactor".
---

# tdd

Write the test before the implementation, every time.
Writing the implementation first and the test afterward is not test-driven and is never reported as such, including when the implementation already exists.

## Loop

1. Pick the seam. Attach the test at the change's public boundary and drive the real entry point (CLI, endpoint, UI flow). Weight tests toward end to end over narrow unit tests.
2. Build the harness first when none exists: the fixture, runner, or driver for the seam, in its own commit. A missing harness is not an exemption.
3. Red. Write one failing test for the desired behavior and run it. Confirm it fails because the behavior is missing, not because of an import error or a missing fixture. Record the test name and failure message for the PR.
4. Green. Write the minimum code to pass.
5. Refactor while the tests stay green.
6. Repeat per behavior.

## Rules

- A bug fix starts from its reproduction, which becomes a regression test that fails before the fix and passes after.
- Changes with no behavior to test are exempt: documentation, comments, formatting, and renames the existing suite covers. Changes another guard proves are also exempt: dependency upgrades (the existing suite), refactors (characterization tests), performance work (a benchmark), and prototypes (discarded).
- Flakiness is a defect. Do not use unseeded randomness, real clocks, order-dependent tests, or un-stubbed network calls.
