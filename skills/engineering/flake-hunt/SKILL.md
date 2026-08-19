---
name: flake-hunt
description: Use when a test failure may be intermittent, order-dependent, seed-dependent, or limited to CI. Reruns the failure, separates the change from the base, bisects seeds and test order, and applies a time-bounded quarantine only when the evidence supports it. Trigger on "find the flake", "hunt down the flaky test", "this test only fails sometimes", "CI is flaky", "quarantine this test", "why did this pass on retry".
---

# flake-hunt

Determine whether a test failure is nondeterministic, identify the condition that triggers it, and keep CI's signal visible while the cause is fixed.
Do not call a test flaky because one retry passes.

This skill investigates flakiness and produces a verdict.
Fixing the cause or landing a quarantine is a separate step, done however you normally land changes (the `dev-workflow` skill, if you use it).

## Procedure

1. **Capture the original failure.** Preserve the first failing run before retrying it.
   Record the test identifier, exact command, commit SHA, merge base when known, runner and platform, dependency state, worker count, parallelism, test order, random seeds, and relevant logs.
   If the failure is in CI, save the job URL and artifact links.
   If the failure is not reproducible from the recorded inputs, mark the investigation inconclusive rather than inventing a reproduction.

2. **Rerun a fixed number of independent processes.** Choose `N` before the rerun and record it.
   Use the repository's real test command and start a fresh process for each run; a test-runner retry inside one process does not expose process state leaks.
   Use `N=20` by default for a cheap test, or the repository's existing flake threshold when it defines one.
   Record every pass and failure, the failure rate, and the environment for each run.

   Classify the result:

   - Every run fails under equivalent conditions: the failure is deterministic under those conditions; use the `debug` skill, if you use it.
   - At least one run passes and one run fails: the test is a confirmed flake candidate; continue the investigation.
   - No rerun reproduces the failure: the result is inconclusive; do not quarantine on this evidence alone.

   A rerun count measures evidence, not certainty.
   Report the count and failure rate instead of reducing the result to "passed on retry."

3. **Separate the change from the base.** Identify the merge base or the last known-good commit.
   Run the same command with the same inputs, seeds, order, worker settings, and external environment against both the base and the changed commit.
   Use each commit's declared dependency state and record lockfile or dependency changes as part of the comparison.
   Keep local and CI results separate when their environments differ.

   Interpret the matrix as follows:

   - The base and changed commit fail at comparable rates: the flake predates the change.
   - Only the changed commit fails: the change introduces the failure; fix the change instead of hiding it.
   - Both fail, but the changed commit has a higher rate: the change worsens an existing flake; treat the regression as part of the change.
   - CI fails while the equivalent local run does not: compare runner resources, platform, dependency state, clock, network, and parallelism before assigning blame to the test or the change.

4. **Control randomness and order.** Record every seed the runner exposes.
   Rerun a failing seed unchanged to test whether it reproduces, then vary seeds to test whether the failure depends on generated input.
   Do not binary-search arbitrary seed integers; numeric distance between seeds does not imply similarity between their generated inputs.
   When the seed generates a sequence, minimize the generated sequence by bisecting its prefix or input list while keeping the failing seed and test fixed.

   If the failure appears only in a suite, replay the original test order with parallelism disabled.
   Isolate the target test to distinguish an intrinsic failure from state left by another test.
   If the suite-only failure remains, bisect the ordered predecessor list: keep the target test fixed, split its predecessors into halves, run each half in the original order, and retain the half that preserves the failure.
   Repeat until the smallest triggering prefix is known.
   If the failure needs an interaction between two predecessors, minimize that pair after the prefix bisection rather than assuming one predecessor is sufficient.
   Compare serial and parallel runs to distinguish shared state from a race.

5. **Localize the trigger.** Use the smallest failing input, seed, order, and environment to test one suspected source at a time.
   Check shared mutable state, leaked files or processes, real clocks, timeouts, unseeded randomness, resource exhaustion, concurrency, test order, and un-stubbed network or other external services.
   Add temporary instrumentation when the existing output cannot distinguish these causes.
   Remove instrumentation that does not become a required test or diagnostic tool.

6. **Issue a verdict.** Use one of these labels:

   - `deterministic-failure`
   - `confirmed-flake`
   - `base-flake`
   - `change-introduced-flake`
   - `environment-instability`
   - `inconclusive`

   State the evidence, the triggering variable, the suspected root cause, and the confidence level.
   Use `confirmed-flake` when controlled reruns are mixed but the source is not yet attributed, `base-flake` when the same mixed result exists on the base, `change-introduced-flake` when the changed commit introduces or worsens it, and `environment-instability` when controlled comparison limits the failure to the runner or external environment.
   A suspected cause remains a hypothesis until a controlled change removes the failure.

7. **Quarantine only when necessary.** Do not quarantine a deterministic failure from the changed commit.
   Quarantine a confirmed flake or an identified environment failure only when it blocks the main signal and the repository has a way to keep running it outside the blocking path.

   A quarantine record names the test, observed failure rate, reproduction command, seeds or order, suspected cause, owner, tracking issue, entry date, expiry date, and removal condition.
   Set an expiry date according to repository policy; use 14 days when no policy exists.
   Keep the test running in a visible non-blocking or diagnostic lane that reports failures and unexpected passes.
   If the repository has no such lane, keep the test blocking and fix the cause rather than silently skipping it.
   Review quarantines before expiry and remove them after the cause is fixed, the original reproduction is green, the prior failing seeds or orders are green, and at least `N=20` independent runs are clean.

## Report

Return a structured report rather than a narrative retry result:

```text
Verdict: <label>
Confidence: <high|moderate|low>
Test: <identifier>
Command: <exact command>
Commits: base <SHA>, changed <SHA>
Runs: <failures>/<N> on base; <failures>/<N> on changed
Environment: <runner, platform, dependencies, workers, parallelism>
Seeds and order: <values or unavailable>
Trigger: <smallest known condition>
Cause: <confirmed cause, suspected cause, or unknown>
Action: <fix, continue investigation, or bounded quarantine>
Tracking: <issue or CI job URL, if any>
```

**Interaction mode** (see `standards`): running autonomously, do not block on a missing rerun count or quarantine decision.
Use `N=20`, the 14-day quarantine expiry, and the visible diagnostic-lane requirement as defaults when the repository gives no policy, and record those assumptions in the report.
Emit the verdict and structured fields even when the result is inconclusive.

## Boundaries

- Against `debug`: this skill owns intermittent, order-dependent, seed-dependent, and environment-dependent failures; `debug` owns failures that reproduce deterministically or whose cause is unknown without an intermittent signal.
- Against `perf`: this skill investigates inconsistent test outcomes; `perf` measures latency, throughput, or cost.
- Never delete, disable, or silently skip a test to make CI green.
- Do not use retries as proof that a change is correct; preserve the original failure and report the failure rate.
- Flag unrelated deterministic bugs or infrastructure defects for their own issue and branch.
