---
name: triage
description: Classify one inbound GitHub issue or pull request and produce an agent-ready brief.
argument-hint: "GitHub issue or pull request URL or number"
disable-model-invocation: true
---

# triage

Run `/triage` on one inbound GitHub issue or pull request.
It classifies the item and produces one agent-ready brief.
It does not change code, labels, issue state, or pull request state, and it does not implement, review, label, close, merge, or comment on the item.

## Procedure

1. Resolve the source item. Ask for it when the argument is absent. Accept a GitHub issue or PR URL, or a number in the current repository. Use the URL's repository when one is present.
   Load the body, state, author, labels, comments, linked items, and timestamps with `gh`.
   For a PR, also load the base and head, changed files, diff, review comments, and check results.
   If GitHub data is unavailable, ask for the item's text and mark repository context as unverified.
2. Read the repository context: the glossary and the contribution or issue guidance that applies.
   For an issue, locate the likely entry point, owning code, tests, and configuration from the request's terms.
   For a PR, inspect the changed files, nearby tests, and the linked issue if one exists.
   Search for duplicate issues using the item's distinctive terms and report candidates with links, for example `gh issue list --search "<terms> in:title,body" --state all --limit 20`.
   Do not modify the repository.
3. Separate evidence from interpretation. Record what the source item states, what the repository confirms, and what is inferred.
   Treat a fix proposed in an issue as a suggestion. Treat a PR's diff as the implementation under review, not a request to reimplement.
   Use the repository's ubiquitous-language terms verbatim.
4. Assign one category, the first whose definition fits the item's primary purpose:

   | Category | Use when |
   | --- | --- |
   | `bug` | Existing behavior violates a stated or observable contract. |
   | `feature` | The item requests new user-visible behavior. |
   | `maintenance` | The item requests an internal, dependency, tooling, or behavior-preserving change. |
   | `documentation` | The item changes documentation, examples, comments, or other explanatory text only. |
   | `question` | The item asks for an explanation or decision without requesting implementation. |
   | `unknown` | The available evidence cannot distinguish the category. |

   If the item contains separate requests, classify the primary one and list the others as scope or open questions.
5. Assign one disposition and one work type.
   Dispositions:
   - `ready`: an agent can act without guessing.
   - `needs-information`: a named question blocks action.
   - `duplicate`: a linked or confirmed item covers the same work.
   - `out-of-scope`: the request conflicts with the repository boundary.
   - `deferred`: the request is valid but intentionally postponed.
   - `closed`: the item is already resolved and needs no further action.

   Work types:
   - `implement`: a ready issue.
   - `review`: a ready PR.
   - `investigate`: an unresolved technical problem.
   - `answer`: a question.
   - `close`: a duplicate, out-of-scope, or deferred item.

   A `needs-information` result may use `investigate` when the missing evidence can be gathered without a user decision.
   Ask the user only the questions needed to resolve a blocking ambiguity. When no user can answer (`standards`), emit `needs-information`, list the exact questions, and record every assumption in the brief.
   Never claim `ready` when an agent would have to invent a requirement, path, command, or acceptance criterion.
6. Write the brief with these fields in this order:

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
   Derive checkable acceptance criteria from the source item or confirmed repository behavior.
   Mark an unverified command, path, or assumption as unverified instead of filling it in.
   For a disposition other than `ready`, state the blocking reason in `Objective` and `Constraints and open questions`.
7. Return the complete brief to the caller or fleet runner without starting implementation. Any later code change follows the repository's normal development workflow outside this skill.

## Notes

- Category describes the item's primary purpose. Disposition describes whether and how work proceeds.
- A PR is an inbound item even when an external contributor owns its head repository.
- When the brief exposes a decision that needs a design or implementation plan, triage does not replace that plan.
