"""Behavior pin for dedupe(): first-occurrence order, exact unique set.
Fixed expectations, independent of how dedupe() is implemented.
Run directly: python3 test_dedupe.py
"""
from __future__ import annotations

from dedupe import dedupe


def test_keeps_first_occurrence_order() -> None:
    records = [{"key": "a"}, {"key": "b"}, {"key": "a"}, {"key": "c"}, {"key": "b"}]
    assert dedupe(records) == [{"key": "a"}, {"key": "b"}, {"key": "c"}]


def test_all_duplicates_collapse_to_one() -> None:
    records = [{"key": "same", "n": i} for i in range(50)]
    assert dedupe(records) == [{"key": "same", "n": 0}]


def test_no_duplicates_passes_through_unchanged() -> None:
    records = [{"key": f"rec-{i}"} for i in range(50)]
    assert dedupe(records) == records


def test_key_must_be_hashable() -> None:
    """Documents the one behavior change from the list-based version: that
    implementation compared keys with `==` and accepted any type; this one
    looks keys up in a dict, so an unhashable key (e.g. a list) now raises."""
    try:
        dedupe([{"key": ["not", "hashable"]}])
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError for an unhashable key")


if __name__ == "__main__":
    tests = [
        test_keeps_first_occurrence_order,
        test_all_duplicates_collapse_to_one,
        test_no_duplicates_passes_through_unchanged,
        test_key_must_be_hashable,
    ]
    for t in tests:
        t()
        print(f"ok: {t.__name__}")
    print(f"{len(tests)} passed")
