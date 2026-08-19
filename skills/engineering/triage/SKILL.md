---
name: triage
description: Use when an inbound GitHub issue or external pull request needs a category, disposition, and agent-ready brief. Reads the source item, repository context, and pull request diff when present, then separates evidence from assumptions before routing the work. Trigger on "triage this issue", "triage this PR", "classify this ticket", "prepare a brief from this issue".
argument-hint: "GitHub issue or pull request URL or number"
---

# triage

Classify one inbound GitHub issue or pull request and produce one agent-ready brief.
This skill does not change code, labels, issue state, or pull request state.

## Procedure

1. **Resolve the source item.** Accept a GitHub issue or pull request URL, or a number in the current repository.
   Use the URL's repository when one is present.
   Load the body, state, author, labels, comments, linked items, and timestamps with `gh`.
   For a pull request, also load the base and head, changed files, diff, review comments, and check results.
   If GitHub data is unavailable, ask for the item's text and mark repository context as unverified.
2. **Read the repository context.** Read the repository glossary and the contribution or issue guidance that applies to the item.
   For an issue, locate the likely entry point, owning code, tests, and configuration from the request's terms.
   For a pull request, inspect the changed files, nearby tests, and the linked issue when one exists.
   Search for likely duplicate issues using the item's distinctive terms and report candidates with links, for example `gh issue list --search "<terms> in:title,body" --state all --limit 20`.
   Do not modify the repository while triaging it.
3. **Separate evidence from interpretation.** Record what the source item states, what the repository confirms, and what remains inferred.
   Treat a proposed fix in an issue as a suggestion rather than a requirement.
   Treat a pull request's diff as the implementation under review, not as a request to reimplement.
   Preserve the repository's ubiquitous-language terms verbatim.
4. **Assign one category.** Use the first category whose definition fits the item's primary purpose:

   | Category | Use when |
   | --- | --- |
   | `bug` | Existing behavior violates a stated or observable contract. |
   | `feature` | The item requests new user-visible behavior. |
   | `maintenance` | The item requests an internal, dependency, tooling, or behavior-preserving change. |
   | `documentation` | The item changes documentation, examples, comments, or other explanatory text only. |
   | `question` | The item asks for an explanation or decision without requesting implementation. |
   | `unknown` | The available evidence cannot distinguish the category. |

   If one item contains separate requests, classify the primary request and list the others as scope or open questions.
5. **Assign one disposition and work type.** Use `ready` when an agent can act without guessing, `needs-information` when a named question blocks action, `duplicate` when a linked or confirmed item covers the same work, `out-of-scope` when the request conflicts with the repository boundary, `deferred` when the request is valid but intentionally postponed, and `closed` when the item is already resolved and needs no further action.
   Use `implement` for a ready issue, `review` for a ready pull request, `investigate` for an unresolved technical problem, `answer` for a question, and `close` for a duplicate, out-of-scope, or deferred item.
   A `needs-information` result may use `investigate` when the missing evidence can be gathered without a user decision.
6. **Write the brief.** Produce the following fields in this order:

   ```markdown
   ## Triage result
   - Source: <URL>
   - Category: <bug|feature|maintenance|documentation|question|unknown>
   - Disposition: <ready|needs-information|duplicate|out-of-scope|deferred|closed>
   - Work type: <implement|review|investigate|answer|close>
   - Confidence: <high|moderate|low|unknown>

   ## Agent-ready brief
   ### Objective
   <one actionable outcome, or why no action starts>

   ### Evidence
   - Source item: <stated facts with links or quoted terms>
   - Repository: <confirmed paths, symbols, tests, or constraints>
   - Inference: <assumptions, each marked as an inference>

   ### Scope
   - In scope: <files, behavior, or review surface>
   - Out of scope: <explicit exclusions or None known>

   ### Acceptance criteria
   1. <checkable criterion>

   ### Verification
   - <real command, end-to-end flow, or review check>

   ### Constraints and open questions
   - <constraint or question, or None known>

   ### Duplicate candidates
   - <linked candidate and reason, or None found>

   ### References
   - <source and repository links>
   ```

   Keep source-backed facts separate from inference.
   Make acceptance criteria checkable and derive them from the source item or confirmed repository behavior.
   Mark an unverified command, path, or assumption as unverified rather than filling it in.
   For a non-ready disposition, state the blocking reason in `Objective` and `Constraints and open questions`.
7. **Return the result without starting implementation.** Give the complete brief to the caller or fleet runner.
   Any later code change follows the repository's normal development workflow outside this skill.

## Interaction mode

In interactive use, ask for the source item when the argument is absent and ask only the focused questions needed to resolve a blocking ambiguity.
In autonomous use, do not block on missing information; emit `needs-information`, list the exact questions, and record every assumption in the brief.
Never claim `ready` when the agent would have to invent a requirement, path, command, or acceptance criterion.

## Boundaries

- `triage` classifies an inbound item and writes a brief; it does not implement, review, label, close, merge, or comment on the item.
- The category describes the item's primary purpose; the disposition describes whether and how work proceeds.
- A pull request is an inbound item even when its head repository is owned by an external contributor.
- Triage does not replace a design or implementation plan when the brief exposes a decision that needs one.
