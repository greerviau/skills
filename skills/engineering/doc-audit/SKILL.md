---
name: doc-audit
description: Use after finishing any code change, and whenever writing or editing documentation or code comments. Reviews and updates docstrings, nearby comments, directory READMEs, docs files, and examples so they match the current code, written in present tense describing current state rather than a change narrative. Trigger on "before you're done, check the docs", "update the docs", "write a comment/docstring", or as a final step before treating any code change as complete.
---

# doc-audit

Documentation and comments describe the current state of the code, in present tense — never a change narrative (how it used to work, what changed, what ticket motivated it). The full style rules — present tense, the decision-history exception, no repo layouts, semantic line breaks, mermaid over ASCII — live in the `standards` skill under "Documentation and comments." Apply them when auditing.

## Procedure: auditing after a code change

Before treating any non-trivial code change as done:

1. Identify what you touched: which functions, modules, or behaviors changed.
2. Check the documentation covering that surface: docstrings on the changed functions, surrounding comments, the nearest directory README, any `docs/` files describing the feature, and any examples demonstrating it.
3. For each, check whether it still matches the code — update anything stale by rewriting to current reality, not appending a change note (see the decision-history exception in `standards`).
4. Briefly note what you checked or updated, so the audit is visible.

Skip changes with no documentation surface (test-only, formatting-only diffs).
