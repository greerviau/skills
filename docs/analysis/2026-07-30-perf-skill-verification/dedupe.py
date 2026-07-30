"""dedupe(): drop duplicate records by key, keeping first occurrence and order.

Part of the perf skill's own verification exercise - see
../2026-07-30-perf-skill-verification.md for the before/after write-up.
"""
from __future__ import annotations

from typing import Hashable


def dedupe(records: list[dict]) -> list[dict]:
    """Each record's "key" must be hashable - a dict lookup backs the check."""
    seen: dict[Hashable, dict] = {}
    for r in records:
        if r["key"] not in seen:
            seen[r["key"]] = r
    return list(seen.values())
