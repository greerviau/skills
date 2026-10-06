---
name: spec
description: Turn a raw request into a reviewed implementation plan and human-facing spec.
disable-model-invocation: true
---

# spec

Run `/spec` to turn a raw request (a feature, bug fix, pipeline, or infrastructure change, in one file or many repos) into a reviewed plan.
This skill plans and does not build. It writes the spec, the implementation plan, and the ubiquitous-language glossary updates. Implementation starts after the user reviews the spec and chooses to execute.

## Two artifacts, two readers

The spec and the implementation plan have different readers, so they are separate files (*Artifact audience* in `standards`).

- The implementation plan is agent-facing. It states what to change and in what order, naming files, symbols, and commands, at whatever length precision needs. Write it first: writing per-symbol steps against the real code exposes cases the code cannot support, and those change what the spec says.
- The spec is human-facing. It states what, why, what "done" means, and what is out of scope, in one to two screens, linking to the plan for detail. It is derived from the plan and carries the review gate. The reviewer does not read the plan.

## Principles

- Find the real code, call sites, and conventions before designing. Never plan against assumed structure.
- Fan discovery out to `Explore` subagents and keep only distilled findings (paths, symbols, code shape) in your context. Do not read whole files when a subagent can return the relevant excerpts.
- Size the spec to the request's scope. A one-file bug fix gets a short spec and a cross-repo pipeline gets a thorough one. A spec grows because it covers more decisions, not because it explains each at more length.
- The plan is a contract. Someone should be able to execute it without re-deriving scope, so name specific files, functions, and steps.
- Revise the spec and plan together. Feedback that changes the approach changes the plan, and a spec revised alone leaves the executor working from steps the review never covered.
- Use the domain's ubiquitous language in the spec, conversation, and code, as recorded in the repo's glossary.

## The ubiquitous-language glossary

The core rule (read the glossary, use its terms verbatim, extend it when a term settles or goes stale) is in `standards`. While specing:

- Read the glossaries for the affected contexts before the interview and use their terms exactly.
- Extend them as the interview and exploration settle new terms or reveal stale entries, confirming definitions with the user. Glossary updates ship with the plan.

Layout (an existing location or convention overrides these defaults): one `docs/UBIQUITOUS-LANGUAGE.md` at the repo root with one entry per term (term, precise meaning, and where useful the code artifacts that embody it).
A large repo with distinct bounded contexts gives each context its own `UBIQUITOUS-LANGUAGE.md`; the root glossary maps them and records cross-context name mismatches.
Scope entries to the repo, not the spec: no per-spec section and no planning status like *(planned)*. Group only by where in the repo the term belongs, and define in present tense.
Add a term when it names a domain concept people could misunderstand, not for every variable or utility.

## Procedure

### 1. Skim the territory

Identify the outcome and the kind of work (feature, bug, pipeline, infra).
Explore enough to know which repos and subsystems are involved, so the interview asks informed questions.
Read the glossaries for the affected contexts.

### 2. Interview the user

Before designing, ask the user (via `AskUserQuestion`) about whichever of these the request leaves unclear:

- Outcome and success criteria: what "done" looks like, and for whom.
- Scope boundaries: what is out of scope.
- Constraints: backward compatibility, performance, security, deadlines, required tooling.
- Design forks: where exploration found a real fork, which way to go.
- Terminology: domain terms the request uses ambiguously or the glossary does not cover. These become glossary entries.

Keep asking until the answers stop changing the plan, and record them in the spec.
Questions the user cannot answer better than exploration can go in the open-questions section.

### 3. Explore to discover scope

Map the real code the request touches: repos, files and symbols, existing conventions, and risks.

- Use `Explore` subagents for breadth: locate files, entry points, call sites, tests, config, and existing patterns. Launch independent searches in parallel and ask for paths and short excerpts, not whole files.
- Check whether the request implies changes in more than one repo (a shared library and its consumers, infra and its service) and explore each.
- For bug fixes, identify how to reproduce end to end as a user hits it. The plan's first step is reproduction.
- Note the test framework, lint setup, layout, and naming so the plan fits the codebase.

Keep a running list: primary repo, other affected repos, key files and symbols, new or corrected glossary terms, open questions.
If exploration surfaces a new fork, return to the user before designing past it.

### 4. Choose the approach

Pick the approach. Where the user has not settled a design fork, pick the option that best fits quality, correctness, and the structural standard in `design`, and record each rejected option with the reason it lost. Do not present a menu.

Settle this before detailed writing. Once a long plan exists against one architecture, the spec derived from it rationalizes that architecture, and reopening an alternative means rewriting the plan.

### 5. Write the implementation plan

Turn the approach into the agent-facing plan, grounded in the real code, per *Artifact audience* in `standards`:

- An ordered list of steps, each naming the exact files and symbols it touches and what changes there. For bugs, step 1 is reproduction.
- For each step, the command that verifies it (the repo's real test, lint, or run command).
- The conventions the executor would otherwise rediscover: test framework and layout, fixture patterns, config locations, call sites to update.
- Anything exploration left unverified, marked as such.

Writing the steps is a second discovery pass. It surfaces cases discovery missed, such as a function that cannot take the argument the approach assumed or a component that raises on an input the new flow produces.
Treat each as a finding. Fold it into the plan as a prerequisite phase or a changed step, and carry it into the spec's requirements and risks. If it contradicts something the user settled in the interview, return to them before deriving the spec.

Run the concision pass (`standards`) over the plan. Its never-cut-a-fact floor protects the executor's detail, so expect few cuts.

Write the plan to a scratch or git-ignored path, named for the request in kebab-case, date-prefixed, with an `-implementation` suffix, such as `<scratch>/2026-07-07-fix-xic-shard-lookup-implementation.md`. It is an input to one execution; the spec is what survives.

### 6. Derive the spec from the plan

Cover these at the density a reviewer needs:

- Summary: the request and chosen approach, in a few sentences.
- Requirements: outcome, success criteria, scope boundaries, and constraints from the interview.
- Scope: repos and subsystems affected, with cross-repo coordination called out.
- Approach: the key decisions, and for each real fork, why this option over the alternative. Skip forks that were never close.
- Testing strategy: how the change is proven end to end, in a sentence or two. Commands belong in the plan.
- Risks and open questions: anything that could invalidate the approach or needs a user decision, including what writing the plan surfaced. State uncertainty plainly.

Hold it to one to two screens by linking to the plan: link the plan as a whole, and anchor each spec section to the plan headings it summarizes (scope to the step list, a risk to the step it threatens).

Write in the glossary's terms and refer to the glossary instead of defining terms inline.

### 7. Save the spec and update the glossary

Run the concision pass (`standards`) over the draft and apply what it returns.

Write the spec to a `.md` file with the Write tool. Use an explicit location or standing convention if there is one; otherwise `docs/plans/` in the primary repo. Name it in kebab-case with a date prefix, such as `2026-07-07-fix-xic-shard-lookup.md`.

Write new or corrected glossary entries to the appropriate `UBIQUITOUS-LANGUAGE.md` files, creating them (and the root map for multi-context repos) if needed, following the scoping rules above.

Report the file paths (spec, plan, any glossary file) with a one-line description each. Do not paste their contents into the conversation.

### 8. Ask the user to review the spec

Say where the spec is and ask how to proceed:

- Execute: start implementing from the plan written in step 5.
- Iterate: refine the spec with the user, revise the plan wherever the change reaches it, and present again.

Stop for the answer.

Autonomous runs (`standards`) do not block on the interview or review gate. Resolve what exploration can, take the most defensible call on the rest, record each assumption under "Risks and open questions", write both artifacts, and execute (via the `dev-workflow` skill, if you use it).
