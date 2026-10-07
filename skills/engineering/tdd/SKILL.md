---
name: tdd
description: Use when building or changing behavior in code, including the build step of a feature or fix - pick the seam, write the failing test before any implementation, confirm it fails for the right reason, then the minimum code to green and refactor under green. Trigger on "TDD this", "test-drive this", "write the test first", "red, green, refactor".
---

# tdd

The test-first loop: pick the seam, write one failing test, confirm it fails for the right reason, write the minimum code to pass, refactor under green.
The test is written before the implementation every time. Writing the implementation first and the test afterward is not this skill, and reporting that sequence as test-driven is wrong. This holds when the implementation already exists too.

## Procedure

1. Pick the seam. The test attaches at the change's public boundary. Drive the real entry point (CLI, endpoint, flow), not an internal helper, per the E2E bias in `CODING-STANDARDS.md` (`standards`). The `design` skill has the fuller vocabulary (module depth, information hiding) for harder calls.
2. Build the harness if it does not exist. A missing fixture, runner, or way to drive the seam is step zero and lands as its own commit. Skipping it pushes tests down to whatever unit is convenient.
3. Red. Write one failing test that expresses the desired behavior and run it. Confirm it fails for the intended reason, not an import error or a missing fixture. Record the test name and failure message. The PR cites them as evidence that the test came first.
4. Green. Write the minimum implementation to pass, with no extra scope.
5. Refactor under green. Larger structural cleanup is a separate pass (the `refactor` skill, if you use it).
6. Repeat for each behavior. Land the change (commits, validation, PR) as you normally do (the `dev-workflow` skill, if you use it).

Testing policy (the test-first rule and its exemptions, E2E bias, regression tests, flakiness as a defect) is in `CODING-STANDARDS.md` (`standards`).

## Related skills

- A report of broken behavior goes to `debug`, which produces a red reproduction. A request for new behavior is this skill.
- `dev-workflow`, if you use it, runs this loop as its build step and owns the worktree, validation, and PR around it.
