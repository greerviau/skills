---
name: tdd
description: Use when a request explicitly calls for building test-first - pick the seam, write the failing test before any implementation, confirm it fails for the right reason, then the minimum code to green and refactor under green. Trigger on "TDD this", "test-drive this", "write the test first", "red, green, refactor".
---

# tdd

The test-first loop: pick the seam, write one failing test, confirm it fails for the right reason, minimum code to pass, refactor under green.
The defining rule: **the test is written before the implementation, every time** - writing the implementation first and the test afterward is not this skill, and describing that sequence as test-driven is a reporting failure.

## Procedure

1. **Pick the seam.** The point where the change's public boundary sits is also where the test attaches. Drive the real entry point (CLI, endpoint, flow), not an internal helper, per the E2E bias in `standards`. This is enough to execute the step alone; the `design` skill holds the fuller vocabulary (module depth, information hiding) for the harder calls.
2. **Build the harness if it doesn't exist.** No fixture, no runner, no way to drive the seam - building that is step zero, and it lands as its own commit. This is the step most often skipped, and skipping it is what pushes tests down to whatever unit is convenient instead of the real seam.
3. **Red.** Write one failing test that expresses the desired behavior. Run it. Confirm it fails *for the intended reason* - not an import error, not a missing fixture.
4. **Green.** Minimum implementation to pass. No extra scope.
5. **Refactor under green.** Structural cleanup beyond a tidy-up is a separate pass (the `refactor` skill, if you use it).
6. **Repeat per behavior.** Landing the change - staging commits, validating, opening the PR - is a separate step, done however you normally land changes (the `dev-workflow` skill, if you use it).

Policy (E2E bias, regression tests, flakiness is a defect) lives in `standards`; this skill supplies only the loop.

## Boundaries

- Applies retroactively too: if the implementation already exists, writing a test for it afterward and calling it test-driven is the same reporting failure.
- Against `debug`: a report of broken behavior is `debug`, which produces a failing reproduction - a red test by another name - and hands off to `dev-workflow` to land the fix; a request for new behavior is this skill. Each references the other rather than absorbing it.
- Against `dev-workflow`: `dev-workflow`'s own trigger surface ("any request to write and land code in a repo") is broad enough to also catch a test-first request, so this skill's own triggers stay narrow and explicit and never compete with that catch-all. A plain "implement this feature" lands on `dev-workflow` directly, which does the work itself without routing through this skill.
