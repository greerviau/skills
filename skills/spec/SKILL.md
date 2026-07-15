---
name: spec
description: Use when the user hands you a request to scope and plan before building — a feature they want, a bug to fix, a new pipeline, or a piece of infrastructure — and wants a reviewed plan of action rather than immediate code. Interviews the user to sharpen the requirements, explores the relevant code across one or many repos to discover scope, designs an approach, maintains the repo's ubiquitous-language glossary, writes the plan to a markdown file, and asks whether to execute or iterate. Trigger on "/spec", "spec this out", "plan this", "scope this out", "write a spec/plan for ...".
---

# spec

Turn a raw request into a concrete, reviewed plan of action. The request may be a feature, a bug fix, a new pipeline, or a piece of infrastructure. It may be confined to a single file in a single repo, or span many files across many repos. **This skill plans; it does not build** — the only files it writes are the plan document and the ubiquitous-language glossary, and implementation starts only after the user reviews the plan and chooses to execute.

## Principles

- **Discover before designing.** Never plan against assumed structure. Find the real code, the real call sites, the real conventions first.
- **Be context-efficient.** Exploration across a multi-repo workspace produces a lot of bytes. Fan discovery out to `Explore` subagents (or the sandbox) and keep only the distilled findings — file paths, symbols, and the shape of the code — in your own context. Don't read whole files into context when a subagent can return the relevant excerpts.
- **Match the request's weight.** A one-file bug fix gets a short plan; a new cross-repo pipeline gets a thorough one. Don't pad a small request into a big document, and don't under-specify a large one.
- **The plan is a contract.** Someone (you, later, or a teammate) should be able to execute it without re-deriving the scope. Name specific files, functions, and steps — not vague intentions.
- **Speak the domain's ubiquitous language.** The spec, the conversation, and the eventual code must use the same words for the same concepts. Terms agreed with the user during specing are recorded in the repo's glossary (see below) so nothing gets lost in translation between planning and development.

## The ubiquitous-language glossary

Each repo carries a glossary of its domain terms — the shared vocabulary between user, spec, and code. It lives in version control so it travels with the code:

- **Default layout:** a single `docs/UBIQUITOUS-LANGUAGE.md` at the repo root, one entry per term: the term, its precise meaning in this domain, and (where useful) the code artifacts that embody it. Honor an existing glossary location or standing convention over the default.
- **Large repos with distinct bounded contexts** (e.g. a monorepo of several services plus a frontend): each context keeps its own `UBIQUITOUS-LANGUAGE.md` in its subdirectory, scoped to that context's meanings. The root glossary then acts as the global map — it lists each context, links to its glossary, and records cross-context mappings where the same concept goes by different names (or the same name means different things) on either side of a boundary.
- A term belongs in the glossary when it names a domain concept people could misunderstand — not every variable or utility. Keep entries short and precise; a glossary nobody reads is worse than none.

During specing: **read** the relevant glossaries before the interview and use their terms exactly — never introduce a synonym for a concept that already has a name. **Extend** them as the interview and exploration settle new terms or reveal that an existing entry is stale, confirming definitions with the user as part of the interview rather than inventing them. Glossary updates are written with the plan and are part of the spec's deliverable.

## Procedure

### 1. Skim the territory

Restate the request in one or two sentences to yourself: what outcome does the user want, and what kind of work is it (feature / bug / pipeline / infra)? Then do a quick first-pass exploration — enough to know which repos and subsystems are in play — so the interview that follows asks informed questions instead of naive ones. Locate and read the glossaries covering the affected contexts as part of this pass.

### 2. Interview the user

Before designing anything, grill the user for the details that most often invalidate a spec. Use `AskUserQuestion` and cover whichever of these the request leaves unclear:

- **Outcome and success criteria** — what does "done" look like, and for whom (end users, other services, the team)?
- **Scope boundaries** — what is explicitly *out* of scope?
- **Constraints** — backward compatibility, performance, security, deadlines, required tooling.
- **Design-fork preferences** — where exploration revealed a real fork (two viable architectures, two integration points), ask which way to go rather than guessing.
- **Terminology** — when the request uses a domain term ambiguously, uses two words for what seems to be one concept, or names a concept the glossary doesn't cover, pin down the definition with the user. These agreed definitions become glossary entries.

Keep asking until the answers stop changing the plan. Skip only questions the user plainly cannot answer better than exploration can — those go in the plan's open-questions section instead. Record the answers; they belong in the spec so the reasoning survives review.

### 3. Explore to discover scope

Map the real code the request touches. The goal is to know, concretely: which repos are involved, which files and symbols are the touch points, what the existing conventions are, and where the seams and risks are.

- Prefer `Explore` subagents for breadth — dispatch them to locate relevant files, entry points, call sites, tests, config, and existing patterns across the workspace. Launch independent searches in parallel. Ask each to return paths + short excerpts, not whole files.
- The scope may cross repo boundaries. Explicitly check whether the request implies changes in more than one repo (e.g. a shared library plus its consumers, infra plus the service it runs) and discover each side.
- **For bug fixes specifically:** identify how to reproduce the bug end-to-end, as close to how a user hits it as possible. The plan's first step should be reproduction, so the eventual fix targets the real cause rather than a guess.
- Note the existing conventions (test framework, lint setup, directory layout, naming) so the plan proposes work that fits the codebase rather than fighting it.

Keep a running list of: **primary repo**, other affected repos, key files/symbols, new or corrected glossary terms, and open questions. If exploration surfaces a new fork the interview didn't cover, go back to the user before designing past it.

### 4. Design and build the plan

Decide on an approach and turn it into a step-by-step plan of action. If there's a real fork in the design the user hasn't already settled, pick the one that best fits quality, correctness, simplicity, robustness, and long-term maintainability, and note the alternative briefly as a rejected option with the reason — don't present a menu.

The plan should cover:

- **Summary** — what the request is and the chosen approach, in a few sentences.
- **Requirements** — the outcome, success criteria, scope boundaries, and constraints gathered in the interview.
- **Scope** — repos and files affected; call out cross-repo coordination if any.
- **Approach / design** — the key decisions and why. For anything non-trivial, why this over the obvious alternative.
- **Steps** — an ordered, concrete list of the work. Each step names the file(s)/symbol(s) it touches and what changes. For bugs, step 1 is reproduction.
- **Testing & verification** — how the change will be proven to work end-to-end, using the repo's existing test/verify setup.
- **Risks & open questions** — anything that could invalidate the plan or needs a decision from the user. State uncertainty plainly — an open question is more useful than a confident guess that sends the implementation the wrong way.

Write the plan in the glossary's terms throughout — don't define terms inline in the plan; link or refer to the glossary instead.

### 5. Save the plan and update the glossary

Write the plan to a `.md` file with the native Write tool. Honor an explicit location from the request or a standing convention (a `CLAUDE.md` directive, a memory, a location the user has set before); otherwise default to `docs/plans/` inside the primary repo, creating the folder if needed. Name the file descriptively in kebab-case, prefixed with the actual current date, e.g. `2026-07-07-fix-xic-shard-lookup.md`.

Alongside the plan, write any new or corrected glossary entries to the appropriate `UBIQUITOUS-LANGUAGE.md` file(s), creating them (and the root map, for multi-context repos) if they don't exist yet.

After writing, report only the file paths and a one-line description each — don't dump the plan's full contents back into the conversation.

### 6. Ask the user to review

Tell the user the plan is written and where. Then ask how they want to proceed:

- **Execute** — start implementing the plan as written.
- **Iterate** — refine the plan together first (they'll give feedback; update the file and re-present).

Ask this as a genuine choice and stop for their answer. If execution is chosen, follow the plan step by step, and keep the plan file updated if reality diverges from it during the build.
