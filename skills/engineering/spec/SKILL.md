---
name: spec
description: Use when the user asks to write a software spec, design an idea up front, or settle requirements, scope, and design before implementation, including requests to be interviewed or grilled about a planned change.
---

# spec

Turn a request for a feature, bug fix, pipeline, or infrastructure change into a reviewed spec when scope or design needs to be settled before implementation.
This skill plans and does not build. Implementation starts after the user reviews the spec.

The spec is written only after an **alignment interview**: rounds of questions in which the user makes every decision and the agent finds every fact.
Write nothing until the user says to write.

The spec is human-facing: it states what, why, what "done" means, what is out of scope, and the work items that deliver it. It carries no step-level detail (files to edit, commands). The implementer works that out against the code as it is then.

## Procedure

1. Explore before asking. Identify the outcome and the kind of work, find which repos and subsystems are involved, and read the repo's `GLOSSARY.md` files for the affected contexts.
   Fan discovery out to read-only subagents in parallel when subagents are available and ask for paths, signatures, and short excerpts, not whole files. Check whether the request spans more than one repo. For a bug, find how to reproduce it end to end. Find how the change can be proven end to end with the repo's existing tests or entry points.
   The first round is ready when you can name the decisions the request leaves open and the code facts each one depends on.
2. Run the alignment interview in rounds. Track the open decisions as a tree: each decision branches into the decisions that depend on its answer. A round asks every open decision whose prerequisites are settled. A question whose answer depends on another question in the same round waits for a later round.
   Cover success criteria, scope boundaries, constraints, design forks, names, and ambiguous domain terms. Each round also asks what adjacent work the change should take on or leave out, so scope grows during the interview and not after the spec exists.
   Write each round as plain numbered text, not a structured question tool:

   ```
   1. <Question title>. <Question, listing the options when there are several.>
      Recommendation: <answer>. <One line on why.>
   ```

   Word each question so "yes" accepts the recommendation. Stop after each round and wait for the answers. Recompute the open decisions from the answers before the next round.
   When no user can answer, take the recommendation for each open decision and record each one as an assumption under "Risks and open questions".
3. Find facts yourself and leave decisions to the user. Never ask the user for something the code, docs, or an experiment can answer. When a question needs a fact you do not have, dispatch a subagent to find it and ask the rest of the round meanwhile. Only the questions that depend on that fact wait.
   For a claim about third-party or external behavior, check the installed source and tests first, then the vendor docs for the pinned version, then standards and release notes. Record each claim with its citation and a confidence level (high, moderate, low, unknown). When a decision depends on something you have not seen work, run a throwaway experiment.
4. Base each recommendation on quality, correctness, simplicity, scalability, and maintainability, giving development cost little weight. Prefer the smallest change that fully solves the problem. A smaller change that only patches the symptom is not a candidate, and the question says so. Reuse an existing mechanism before adding a parallel one. When a new concept enters the design, re-derive the interfaces around it instead of keeping the old shape for compatibility.
   When deepening a module the change touches would make the change smaller, recommend the deepening as the first work item.
   When a fork is the interface of a new or deepened module, draft two materially different interfaces, such as the smallest one and one shaped for the most common caller, and show what each caller must know.
   Before recommending an option, read the signatures, call sites, and input shapes it depends on and confirm the code supports it. When a later finding contradicts a settled decision, reopen that decision in the next round.
5. Close the interview. When no open decisions remain, say so, list each settled decision in one line, and stop. Write the spec only when the user says to write.
   When the user says to write while decisions are still open, list the open ones under "Risks and open questions".
   When no user can answer, write once no open decisions remain.
6. Write the spec. It contains only decisions the user settled or assumptions recorded as such. When a new decision comes up while writing, stop and ask it as a round instead of deciding it in the spec.
   - Summary: the request and the chosen approach.
   - Requirements: outcome, success criteria, scope boundaries, constraints.
   - Scope: repos and subsystems affected, with cross-repo coordination.
   - Approach: the key decisions, and why this option over the alternative for each real fork. Record each rejected option with the reason it lost, and list real alternatives as follow-ups.
   - Work items: an ordered list, one line each, naming what it changes and the outcome that shows it is done. Size each so one PR lands it, and state dependencies. A one-file bug fix is one work item.
   - Testing strategy: how the change is proven end to end.
   - Risks and open questions, including external claims with their citations.

   Keep it to one or two screens, longer only when the scope spans repos. State each fact once and cut what a reviewer cannot act on.

   Add a mermaid diagram in place of prose for each of these the spec contains:
   - The change spans services, repos, or deployed components: a component or deployment diagram in Scope.
   - A new or changed interaction between components: a sequence diagram in Approach.
   - An entity gains states or its transitions change: a state diagram in Approach.
   - A new or changed data model: a class or ER diagram in Approach.
   - Work items whose dependencies are not a straight line: a flowchart of the work items in Work items.

   Draw the system after the change, and mark the parts the change adds or alters with a stroke-based `classDef`. Render each diagram and fix its layout before saving. A spec with none of these gets no diagram.
7. Save the spec to the OS temporary directory, in kebab-case with a date prefix such as `2026-07-07-fix-xic-shard-lookup.md`. Never write or commit it to a repo.
8. Update the glossary. Write new or corrected terms to the existing `GLOSSARY.md`, and create `GLOSSARY.md` at the repo root when none exists. Under a no-documents-in-the-repo instruction, extend an existing glossary and put new terms in the spec's text instead.
   One entry per term: the term, its precise meaning, and where useful the code artifacts that embody it. Scope entries to the repo, in present tense, with no planning status. Add a term only when it names a domain concept people could misunderstand. A repo with distinct bounded contexts gives each its own `GLOSSARY.md` in the context's root directory, and the repo-root glossary maps them.
9. Report the file paths with a one-line description each, and ask how to proceed: file the work items as issues, implement them in order, or iterate on the spec.
   Stop for the answer. When no user can answer, report the spec path and the recorded assumptions and stop without executing.
   When the spec supersedes an open PR, say so in the spec and close the PR.
