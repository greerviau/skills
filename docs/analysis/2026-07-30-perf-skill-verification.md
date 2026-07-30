# perf skill verification: deduping synthetic records

Findings for the exercise that verified `skills/engineering/perf/SKILL.md`'s procedure end to end.
This repo's own code is almost entirely markdown skill docs, with no CPU-bound hot path at real scale, so the exercise is a small, self-contained workload rather than a fix to existing repo code.
Harness and code: `docs/analysis/2026-07-30-perf-skill-verification/` (`dedupe.py`, `bench_dedupe.py`, `test_dedupe.py`).

## Target

Dedupe 6,000 synthetic paper-like records by key in under 20ms.

## Workload

`bench_dedupe.py:generate_records(6000, seed=42)`: each record's key is drawn with replacement from a pool of 3,600 possible keys (60% of 6,000), so keys collide and the draw order is already random.
This run yields 2,939 unique keys out of 6,000 records - 51% duplicates.

## Baseline

`dedupe()` compared each record's key against a growing `list` with `in` (O(n) per lookup, O(n²) overall): **125ms** on the workload above.

## Profile

`cProfile` against the baseline, same workload:

```
5880 function calls in 0.134 seconds

ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1    0.133    0.133    0.134    0.134 dedupe.py:9(dedupe)
  5878    0.001    0.000    0.001    0.000 {method 'append' of 'list' objects}
     1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

`cProfile` is function-granular, not line-granular - it attributes 0.133s of the 0.134s to `dedupe()` as a whole, not to any one line inside it.
The `not in seen` check was identified as the specific cause by reading the function afterward: it's the only non-trivial expression in the loop, and the two `append` calls it profiles separately account for only 0.001s.
A claim of a specific *line* being the bottleneck would need a line-level profiler (e.g. `line_profiler`); this exercise only supports the function-level claim above.

## Change

One change: swapped the `list` (compared with `in`) for a `dict` (looked up by key), so the membership check is O(1) instead of O(n).
This also narrows the accepted key type from anything comparable with `==` to anything hashable - `test_key_must_be_hashable` in `test_dedupe.py` documents and pins that constraint.
The other three tests (order preserved, full-duplicate input, no-duplicate input) stayed green throughout, unchanged.

## Re-measure

Same harness, same workload (6,000 records, 2,939 unique keys): **0.8ms** - about 155x faster than baseline, comfortably under the 20ms target.

## Location

This is a one-off exercise; the skill's own default for a one-off keeps the numbers in the PR body alone. This file goes beyond that default deliberately: the exercise exists to be read on its own, by anyone checking how the skill was verified, not only by whoever reads the original PR.
