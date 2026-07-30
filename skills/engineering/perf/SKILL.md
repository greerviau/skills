---
name: perf
description: Use when a change needs to get faster, cheaper, or higher-throughput and the improvement has to be proven, not asserted - baseline with a reproducible harness, profile before hypothesizing, change one thing with the test suite staying green, then re-measure on the same harness. Trigger on "make this faster", "optimize this", "reduce latency", "cut the cost of this", "improve throughput", "this is too slow", "profile this and speed it up".
---

# perf

Measure-first optimization: state a numeric target, baseline it with a reproducible harness, profile before guessing at a cause, change one thing, re-measure on the same harness. **A before/after measurement from that harness is the hard invariant**, the same way `refactor` is guarded by an unchanged test suite - this skill is guarded by a benchmark, and refusing to declare success without one is the whole point.

This is a deliberate, benchmark-guarded pass, distinct from a one-off timing check in a shell. Any change to correctness is out of scope for this skill; a report that something is slow is this skill, a report that something is wrong or crashes is `debug`.

## Procedure

1. **State the target.** Latency, throughput, or cost, with a number and a workload named. "Faster" is not a target; "P50 latency of the `/search` endpoint under 200ms at 50 req/s" is.
2. **Build the harness and take a baseline.** Reproducible, committed to the repo, and cheap enough to re-run on demand. A one-off `time` in a shell is not a baseline - if it can't be re-run unchanged later, it doesn't count as one.
3. **Profile before hypothesizing.** Find the bottleneck with a profiler, tracer, or instrumentation before touching code. A well-informed guess about what's slow is still a guess; the bottleneck is measured, never assumed.
4. **Change one thing.** One change per measurement cycle, so the delta is attributable to it. Behavior stays fixed: the existing test suite must stay green throughout - the guard against a change that quietly altered behavior along with speed.
5. **Re-measure on the same harness** built in step 2, and report before/after numbers with the workload named. Default the report to the PR body for a one-off optimization; once the harness is going to be re-run for future changes rather than just this one, promote it to a durable file under `docs/analysis/` (dated, kebab-case, the convention `spec` and `tech-research` already use) so the numbers outlive the PR.
6. **Keep the harness.** Commit it rather than deleting it once the change lands, so the next regression is detectable against the same baseline. Landing the change itself is a separate step, done however you normally land changes (the `dev-workflow` skill, if you use it).

**Interaction mode** (see `standards`): running autonomously, report the measured delta from step 5 and refuse to declare an optimization successful without it. If the target in step 1 is ambiguous - no number given, workload unclear - take the most defensible reading, record the assumption in the same report, and proceed rather than blocking on a prompt.

## Boundaries

- Against `debug`: this skill owns latency, throughput, and cost; `debug` owns wrong and broken. A report that something is slow is this skill; a report that something is wrong or crashes is `debug`.
- Don't smuggle a behavior change into a perf pass. If step 4 breaks a test, that's a bug or a feature change, not an optimization - flag it and land it on its own branch.
- No before/after number from the same harness means no finished pass. "This should be faster" without step 5's measurement isn't a result.
