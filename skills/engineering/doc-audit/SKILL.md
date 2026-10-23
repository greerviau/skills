---
name: doc-audit
description: Use after code changes or when writing documentation or comments. Audits the touched documentation surface, updates stale prose, and checks it against the plain-language rules.
---

# doc-audit

Documentation and comments describe the current code in present tense, never a change narrative (how it used to work, what changed, which ticket motivated it).
Records that exist to capture a decision or history (ADRs, decision logs, CHANGELOGs, release notes, migration guides, commit messages, PR descriptions) may describe before and after.

## Rules

- Write in present tense, describing what is. Rewrite affected passages instead of appending "changed from ..." notes.
- Do not add repo layouts to documentation.
- In prose markdown, use semantic line breaks: one sentence per line, no hard-wrapping.
- Prefer mermaid to ASCII diagrams.
- A diagram is documentation. When the change alters a structure or flow that a diagram shows, update the diagram and render it.
- A code comment carries a fact the code cannot state, in at most two lines and with no example. Delete a comment that narrates the code. Do not reference this repo's issue or PR numbers in a comment.
- A docstring states what the thing does, then parameters, return, and raises, in the language's standard format. Its summary is one line. Omit parameters the signature and types already state.
- Use the repo's `CODING-STANDARDS.md` where it adds rules.

### Plain language

- Use the short common word: start, use, help, before, after, about, get, show, also.
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless.
- Use active voice with the actor named.
- Use one word per thing and repeat a term verbatim instead of varying it.
- Give every "this", "it", and "that" one antecedent.
- Name the mechanism instead of a figurative label ("load-bearing", "the lever").
- End a sentence on its claim, with no trailing "-ing" clause that grades it.
- Bold a term once, where it is defined.

## Procedure

Run this before treating a non-trivial code change as done.

1. List what the change touched: functions, modules, behaviors, and the comment lines it adds. Take the comments from the diff, not from memory.
2. Find the documentation covering that surface: docstrings on changed functions, surrounding comments, the nearest directory README, `docs/` files describing the feature, and examples that demonstrate it.
3. Check each against the code. Rewrite anything stale to current behavior instead of appending a change note (see the decision-history exception above).
4. Note what you checked and updated, so the audit is visible.
5. Check language. Dispatch a subagent with the passages you wrote or rewrote and the plain-language rules above. It reports each violation as `path:line`, the rule, and a rewrite, and does not edit. Apply the result. Run the check inline when no subagent is available.

Do steps 1-4 yourself. Judging whether a passage is now misleading depends on change intent that a diff does not carry.

Limit step 5 to prose this change wrote or rewrote. Leave pre-existing violations elsewhere unfixed, list them for the user, and ask which to open as GitHub issues. When no user can answer, list them in the final report.

Skip changes with no documentation surface, such as test-only and formatting-only diffs.
