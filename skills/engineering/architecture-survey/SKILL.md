---
name: architecture-survey
description: Use when the user asks to survey or audit a codebase's architecture, find refactoring or deepening opportunities, or asks how to make an upcoming change or spec easy to build. Not for reviewing a diff or for carrying out a refactor already chosen.
---

# architecture-survey

Survey a codebase for **deepening candidates**: places where restructuring would put more behavior behind a smaller interface, so callers learn less and changes concentrate in one module.
Rank the candidates in a report and stop for the user to pick one.
This skill reads code and changes none of it.

## Terms

- A **module** is anything with an interface and an implementation: a function, class, package, or service.
- An **interface** is everything a caller must know to use a module correctly: the signature, invariants, call order, error modes, required configuration, and performance limits.
- A **deep module** hides much behavior behind a small interface. A **shallow module** has an interface nearly as complex as its implementation.
- A **seam** is where a module's interface lives, the place where behavior can be substituted without editing the code behind it. An **adapter** is one implementation that fills a seam, such as the production client or an in-memory fake.

## Procedure

1. Scope. When the user names an area, a pain point, or an upcoming change or spec, survey that area and skip the ranking below. For an upcoming change, look for the deepening that makes that change smallest.
   Otherwise rank hot spots from history, ignoring generated, vendored, and lock files:

   ```bash
   git log --since=6.months --name-only --format= -- . ':(exclude)*.lock' | grep . | sort | uniq -c | sort -rn | head -30
   ```

   Widen the window when the history is short or the changes are spread evenly.
   Read `UBIQUITOUS-LANGUAGE.md`, `CODING-STANDARDS.md`, and decision records (`docs/adr/`, `docs/decisions/`) that cover the scoped area.
   The scope is done when you can name the paths you will survey and why.
2. Explore the scoped paths. Fan discovery out to read-only subagents in parallel when subagents are available, and ask for paths, signatures, call sites, and short excerpts, not whole files. Look for:
   - one concept spread across many small modules that a reader must open together
   - shallow modules and pass-through wrappers
   - a fact every caller repeats to call something safely
   - helpers extracted for testing while the bugs sit in how callers combine them
   - files that change together in `git log` but live apart
   - code that is untested, or hard to test through its current interface
3. Filter each suspect with the **deletion test**: inline the module into its callers in your head.
   If its complexity disappears, the module is a pass-through, and removing or merging it is a candidate.
   If the complexity reappears in each caller, the module earns its place, and the candidate, if any, moves more caller logic behind it.
   Keep a candidate only when callers end up knowing less. Drop moves, renames, and style cleanups.
   A seam with one adapter and no test substitute is indirection, and removing it can be a candidate. A proposed seam names its two adapters, usually production and a test substitute.
   Keep a candidate that contradicts a decision record only when its friction outweighs the recorded reason, and cite the record.
4. Classify each candidate's dependencies, which decide how the deepened module is tested:
   - In-process (pure computation, in-memory state): test through the new interface directly.
   - Local stand-in (a database or filesystem with a local substitute, such as PGLite or an in-memory filesystem): run the stand-in in the tests, and keep the seam internal to the module.
   - Owned remote (your own service across a network): define an interface at the seam, with a network adapter for production and an in-memory adapter for tests.
   - Third-party (an external API): inject it at the seam and substitute it in tests.
5. Rate each candidate:
   - Strong: the deletion test clearly passes and history shows the friction, such as hot-spot churn, repeated fixes, or files that change together.
   - Worth exploring: the deletion test passes, and the payoff depends on where the code goes next.
   - Speculative: everything else.

   When no candidate rates Strong, the report opens with "No strong candidates found."
6. Write the report to `<date>-architecture-survey-<area>.md` in the OS temporary directory, never to the repo. For each Strong and Worth exploring candidate, give:
   - a title naming the deepening, and its rating
   - the files involved
   - the problem in one sentence, with its evidence (commit counts, the callers that repeat a fact)
   - the change in one sentence: what moves behind which interface. Do not design the interface.
   - the gain: what callers stop knowing, where changes and bugs concentrate, which tests get simpler, and which tests of removed modules the change retires
   - the dependency category and how the deepened module is tested
   - the decision record it contradicts, if any
   - a before and after mermaid diagram when the structure is a graph or sequence. Render each diagram and fix its layout before saving.

   List Speculative candidates one line each.
   Name modules with the glossary's domain terms, not class names.
   End with the top recommendation: one candidate and one sentence on why.
7. Report the path, list the candidates one line each with their ratings, and ask which to pursue. Stop for the answer.
   When no user can answer, report the path and stop.
   A chosen candidate that changes an interface its callers use needs a spec before implementation. One that keeps every caller-facing interface is a behavior-preserving refactor under the existing tests.
   Offer to file the other Strong candidates as GitHub issues.
