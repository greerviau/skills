---
name: benchmark
description: Use when measuring performance, running a benchmark, or reporting or acting on a measured speedup, regression, throughput, or latency, including choosing a library or configuration by measurement.
---

# benchmark

Vet a performance number before you report or act on it.
Answer each question below with evidence from a run, never from reading the code.

For a quick ballpark the user asks for, one run is enough: check questions 4 and 7, report the number as a one-run ballpark with no verdict, and skip the other questions and the analysis file unless the run looks wrong.
A choice between options is never a ballpark.

## Before running

1. Write the claim you expect to make, in the words you would ship, such as "export is 30% faster at p50 on the 60k-row dataset", and the result that would change a decision. The questions test that sentence.
2. Read the measurement script and note what it times, counts, and ignores.
3. Check load with `uptime` and cores with `nproc`. When the machine is busy and you cannot stop what runs, say so in the report.

## Questions

1. Why not double? Name the **limiter**: the core, lock, disk, network, or load generator that bounds the result. Find it in a separate profiling run, and do not report that run's timings: CPU per process (`top`, `pidstat`), a runtime profiler (`node --cpu-prof`, `py-spy`, `perf`), I/O wait, and syscall counts (`strace -c`). Map the hot spot to source. When the load generator saturates first, the run measured the load generator. When a change did not move the number, find the limiter before calling the change useless.
2. Was each side tuned? Run every side the way production runs it: release builds, production flags and environment, batching and transaction settings, connection pools, caches as warm or cold as production sees them, and the same versions and data. A limiter that is a setting (a commit per row, a debug build, a missing index) means that side is untuned. Tune it and measure again before picking a winner. When the user is choosing what to adopt, narrowing the claim to today's settings does not excuse an untuned side.
3. Does it break a limit? Compare bytes per second with disk and network bandwidth, operations per second times the cost per operation with available cores, and the time saved with the time the changed piece took. Removing a piece that takes 10% of the run cuts the run time by at most 10%. A result past a limit measured a cache, a no-op, or a bug.
4. Did it error? Count failures and non-success responses, and check that outputs are correct, not only present. When the script does not count errors, add the count.
5. Does it reproduce? Run each side at least 5 times, alternating A, B, A, B so warmup, caches, and drift favor neither. Report the median and range. A gap smaller than the run-to-run spread is no measurable difference. For a close call, use a rank-sum test or the harness's own statistics.
6. Does it matter? Next to a micro result, measure the end-to-end path a user waits on, with realistic data sizes and concurrency, and report the micro result as a share of the whole.
7. Did the work happen? Confirm the work ran inside the timed region: the request reached the server, the rows were written, the bytes were read, and the code used the result. Unconsumed generators, unawaited promises, results the compiler or JIT discards, and timeouts produce numbers for work that never ran.

## Report

Lead with the verdict: faster, slower, no measurable difference, or inconclusive.
Give the number with its unit, the run count, the range, and the limiter, for example "p50 41 ms to 33 ms, median of 7 runs per side, range 32 to 35 ms after, bound by JSON parsing on one core."
The verdict is inconclusive when the limiter is unnamed, a side ran untuned, or question 4 or 7 went unchecked. Name the gap.
Write the runs, ranges, and limiter evidence to `docs/analysis/<date>-<name>.md`, or to the OS temporary directory when the user or the repo's agent instructions (`AGENTS.md` or equivalent) say not to write documents to the repo.
A PR body carries one primary number and points to that file.
