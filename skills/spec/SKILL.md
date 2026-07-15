---
name: spec
description: Use when the user hands you a request to scope and plan before building — a feature they want, a bug to fix, a new pipeline, or a piece of infrastructure — and wants a reviewed plan of action rather than immediate code. Interviews the user to sharpen the requirements, explores the relevant code across one or many repos to discover scope, designs an approach, writes the plan to a markdown file, and asks whether to execute or iterate. Trigger on "/spec", "spec this out", "plan this", "scope this out", "write a spec/plan for ...".
---

# spec

Turn a raw request into a concrete, reviewed plan of action. The request may be a feature, a bug fix, a new pipeline, or a piece of infrastructure. It may be confined to a single file in a single repo, or span many files across many repos. **This skill plans; it does not build** — the only files it writes are the plan document itself, and implementation starts only after the user reviews the plan and chooses to execute.

## Principles

- **Discover before designing.** Never plan against assumed structure. Find the real code, the real call sites, the real conventions first.
- **Be context-efficient.** Exploration across a multi-repo workspace produces a lot of bytes. Fan discovery out to `Explore` subagents (or the sandbox) and keep only the distilled findings — file paths, symbols, and the shape of the code — in your own context. Don't read whole files into context when a subagent can return the relevant excerpts.
- **Match the request's weight.** A one-file bug fix gets a short plan; a new cross-repo pipeline gets a thorough one. Don't pad a small request into a big document, and don't under-specify a large one.
- **The plan is a contract.** Someone (you, later, or a teammate) should be able to execute it without re-deriving the scope. Name specific files, functions, and steps — not vague intentions.

## Procedure

### 1. Skim the territory

Restate the request in one or two sentences to yourself: what outcome does the user want, and what kind of work is it (feature / bug / pipeline / infra)? Then do a quick first-pass exploration — enough to know which repos and subsystems are in play — so the interview that follows asks informed questions instead of naive ones.

### 2. Interview the user

Before designing anything, grill the user for the details that most often invalidate a spec. Use `AskUserQuestion` and cover whichever of these the request leaves unclear:

- **Outcome and success criteria** — what does "done" look like, and for whom (end users, other services, the team)?
- **Scope boundaries** — what is explicitly *out* of scope?
- **Constraints** — backward compatibility, performance, security, deadlines, required tooling.
- **Design-fork preferences** — where exploration revealed a real fork (two viable architectures, two integration points), ask which way to go rather than guessing.

Keep asking until the answers stop changing the plan. Skip only questions the user plainly cannot answer better than exploration can — those go in the plan's open-questions section instead. Record the answers; they belong in the spec so the reasoning survives review.

### 3. Explore to discover scope

Map the real code the request touches. The goal is to know, concretely: which repos are involved, which files and symbols are the touch points, what the existing conventions are, and where the seams and risks are.

- Prefer `Explore` subagents for breadth — dispatch them to locate relevant files, entry points, call sites, tests, config, and existing patterns across the workspace. Launch independent searches in parallel. Ask each to return paths + short excerpts, not whole files.
- The scope may cross repo boundaries. Explicitly check whether the request implies changes in more than one repo (e.g. a shared library plus its consumers, infra plus the service it runs) and discover each side.
- **For bug fixes specifically:** identify how to reproduce the bug end-to-end, as close to how a user hits it as possible. The plan's first step should be reproduction, so the eventual fix targets the real cause rather than a guess.
- Note the existing conventions (test framework, lint setup, directory layout, naming) so the plan proposes work that fits the codebase rather than fighting it.

Keep a running list of: **primary repo**, other affected repos, key files/symbols, and open questions. If exploration surfaces a new fork the interview didn't cover, go back to the user before designing past it.

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

### 5. Save the plan to a markdown file

Write the plan to a `.md` file with the native Write tool. Honor an explicit location from the request or a standing convention (a `CLAUDE.md` directive, a memory, a location the user has set before); otherwise default to `docs/plans/` inside the primary repo, creating the folder if needed. Name the file descriptively in kebab-case, prefixed with the actual current date, e.g. `2026-07-07-fix-xic-shard-lookup.md`.

After writing, report only the file path and a one-line description — don't dump the plan's full contents back into the conversation.

### 6. Ask the user to review

Tell the user the plan is written and where. Then ask how they want to proceed:

- **Execute** — start implementing the plan as written.
- **Iterate** — refine the plan together first (they'll give feedback; update the file and re-present).

Ask this as a genuine choice and stop for their answer. If execution is chosen, follow the plan step by step, and keep the plan file updated if reality diverges from it during the build.
