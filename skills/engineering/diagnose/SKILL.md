---
name: diagnose
description: 'Use when investigating or fixing a failure whose cause is unknown, including crashes, incorrect output, and flaky tests.'
---

# diagnose

Turn a symptom into a confirmed root cause before changing any code.

## Procedure

1. Reproduce. Build the smallest reliable reproduction that drives the real entry point the way a user hits it. When it does not reproduce, report what you tried and ask for the missing detail (environment, inputs, version). Do not guess at a fix.
2. Characterize. For an intermittent failure, rerun a fixed number of times and record the failure rate. Vary one factor at a time: seed, test order, environment, base versus changed code.
3. Narrow. Bisect history (`git bisect run`), bisect inputs, add instrumentation, and read the failing path. List the candidate causes, and for each name the observation that would rule it out.
4. Confirm. State the cause and the evidence: the reproduction fails because of this cause, and removing the cause makes it pass. A cause that no observation distinguishes from the alternatives is a hypothesis, so say so.
5. Report the symptom, the cause, the evidence, and the proposed fix. Fix only when asked. The reproduction becomes the failing regression test that the fix turns green.

Leave unrelated defects found along the way unfixed, list them for the user, and ask which to open as GitHub issues. When no user can answer, list them in the report.
Quarantine a flaky test only after diagnosis shows the cause is outside the code under test, and keep the quarantine visible and time-bounded.
