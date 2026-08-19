---
name: doc-audit
description: Use after code changes or when writing documentation or comments. Audits the touched documentation surface, updates stale prose, and checks it against the plain-language rules.
---

# doc-audit

Documentation and comments describe the current state of the code, in present tense — never a change narrative (how it used to work, what changed, what ticket motivated it). The full style rules — present tense, the decision-history exception, no repo layouts, semantic line breaks, comments that earn their place, inline comments of two lines or less with no examples, plain language, mermaid over ASCII — live in the `standards` skill under "Documentation and comments." Apply them when auditing.

## Procedure: auditing after a code change

Before treating any non-trivial code change as done:

1. Identify what you touched: which functions, modules, or behaviors changed, and which comment lines the change adds. Enumerate the comments from the diff rather than from memory.
2. Check the documentation covering that surface: docstrings on the changed functions, surrounding comments, the nearest directory README, any `docs/` files describing the feature, and any examples demonstrating it.
3. For each, check whether it still matches the code — update anything stale by rewriting to current reality, not appending a change note (see the decision-history exception in `standards`).
4. Briefly note what you checked or updated, so the audit is visible.
5. **Check language.** Dispatch a subagent with the passages you wrote or rewrote and the "Plain language" rules in `standards`. It reports each violation as `path:line`, the rule, and a concrete rewrite; it does not edit. Apply what it returns. Run the check inline when no subagent is available.

Steps 1–4 stay with you rather than a subagent; judging whether a passage is now misleading depends on change intent a diff doesn't carry.

Scope step 5 to prose this change wrote or rewrote, not the surrounding document. Pre-existing violations elsewhere follow branch hygiene in `standards`: flag them, fix them on their own branch.

Skip changes with no documentation surface (test-only, formatting-only diffs).
