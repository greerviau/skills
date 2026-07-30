"""dedupe(): drop duplicate records by key, keeping first occurrence and order.

Part of the perf skill's own verification exercise - see the PR that added
skills/engineering/perf/SKILL.md for the full before/after write-up.
"""
from __future__ import annotations


def dedupe(records: list[dict]) -> list[dict]:
    seen: list[str] = []
    out: list[dict] = []
    for r in records:
        if r["key"] not in seen:
            seen.append(r["key"])
            out.append(r)
    return out
