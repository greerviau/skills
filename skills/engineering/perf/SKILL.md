---
name: perf
description: Use when a change needs to get faster, cheaper, or higher-throughput and the improvement has to be proven, not asserted - baseline with a reproducible harness, profile before hypothesizing, change one thing with the test suite staying green, then re-measure on the same harness. Trigger on "make this faster", "optimize this", "reduce latency", "cut the cost of this", "improve throughput", "this is too slow", "profile this and speed it up".
---

# perf

Measure-first optimization: state a numeric target, baseline it with a reproducible harness, profile before guessing at a cause, change one thing, and re-measure on the same harness.
An optimization is not done without a before/after measurement from that harness. `refactor` is guarded by an unchanged test suite; this skill is guarded by a benchmark.

This is a benchmark-guarded pass, separate from a one-off timing in a shell.

## Procedure

1. State the target: latency, throughput, or cost, with a number and a named workload. "Faster" is not a target. "P50 latency of the `/search` endpoint under 200ms at 50 req/s" is.
2. Build the harness and take a baseline. The harness is reproducible, committed to the repo, and cheap to re-run. A one-off `time` in a shell does not count, because it cannot be re-run unchanged later.
3. Profile before hypothesizing. Find the bottleneck with a profiler, tracer, or instrumentation before touching code, even when reading the code makes it look obvious.
4. Change one thing per measurement cycle, so the delta is attributable. Keep the existing test suite green throughout, which catches a change that altered behavior along with speed.
5. Re-measure on the step 2 harness and report before/after numbers with the workload named. For a one-off optimization, put the report in the PR body. When the harness will be re-run for future changes, put it in a dated kebab-case file under `docs/analysis/` (the convention `spec` and `tech-research` use) so the numbers outlive the PR.
6. Commit the harness, so the next regression is detectable against the same baseline. Land the change as you normally do (the `dev-workflow` skill, if you use it).

Autonomous runs (`standards`) report the step 5 delta and do not declare success without it. If the step 1 target is ambiguous (no number, unclear workload), take the most defensible reading, record the assumption in the report, and proceed.

## Related skills

- This skill owns latency, throughput, and cost. `debug` owns wrong or crashing behavior.
- A step 4 change that breaks a test is a bug or feature change, not an optimization. Flag it and land it on its own branch.
