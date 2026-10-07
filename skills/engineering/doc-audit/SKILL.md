---
name: doc-audit
description: Use after code changes or when writing documentation or comments. Audits the touched documentation surface, updates stale prose, and checks it against the plain-language rules.
---

# doc-audit

Documentation and comments describe the current code in present tense, never a change narrative (how it used to work, what changed, which ticket motivated it).
The style rules are in `standards`.
Its `SKILL.md` holds present tense, the decision-history exception, no repo layouts, semantic line breaks, plain language, and mermaid over ASCII.
Its `CODING-STANDARDS.md` holds comments that carry a fact, two-line inline comments without examples, and the docstring rules.

## Procedure

Run this before treating a non-trivial code change as done.

1. List what the change touched: functions, modules, behaviors, and the comment lines it adds. Take the comments from the diff, not from memory.
2. Find the documentation covering that surface: docstrings on changed functions, surrounding comments, the nearest directory README, `docs/` files describing the feature, and examples that demonstrate it.
3. Check each against the code. Rewrite anything stale to current behavior instead of appending a change note (see the decision-history exception in `standards`).
4. Note what you checked and updated, so the audit is visible.
5. Check language. Dispatch a subagent with the passages you wrote or rewrote and the "Plain language" rules in `standards`. It reports each violation as `path:line`, the rule, and a rewrite, and does not edit. Apply the result. Run the check inline when no subagent is available.

Do steps 1-4 yourself. Judging whether a passage is now misleading depends on change intent that a diff does not carry.

Limit step 5 to prose this change wrote or rewrote. Flag pre-existing violations elsewhere and fix them on their own branch (branch hygiene in `standards`).

Skip changes with no documentation surface, such as test-only and formatting-only diffs.
