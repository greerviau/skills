"""Harness for the perf skill's own verification exercise (see the PR that added
skills/engineering/perf/SKILL.md for the full before/after write-up).

Workload: dedupe N synthetic paper-like records by key, ~40% of them exact
duplicates, in randomized order. Target: hold dedupe() under 20ms at N=6000.
Kept here, and re-runnable, so a future regression in this pattern is
detectable against the same baseline.
"""
from __future__ import annotations

import random
import time

from dedupe import dedupe


def generate_records(n: int, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    unique_n = max(1, int(n * 0.6))
    keys = [f"rec-{i:08d}" for i in range(unique_n)]
    records = [{"key": rng.choice(keys), "title": "paper"} for _ in range(n)]
    rng.shuffle(records)
    return records


def time_dedupe(records: list[dict], repeats: int = 5) -> tuple[float, list[dict]]:
    best = float("inf")
    result: list[dict] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = dedupe(records)
        best = min(best, time.perf_counter() - t0)
    return best, result


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
    records = generate_records(n)
    elapsed, result = time_dedupe(records)
    print(f"workload: dedupe {n} records ({len(set(r['key'] for r in records))} unique keys)")
    print(f"dedupe(): {elapsed * 1000:.1f} ms -> {len(result)} unique records")
