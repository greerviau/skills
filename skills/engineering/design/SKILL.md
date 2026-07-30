---
name: design
description: The shared vocabulary for judging and explaining structure - module depth, information hiding, seam placement, error-condition elimination, navigability - that `spec`, `refactor`, and `review` reason in instead of asserting "simplicity" or "maintainability" with no operational meaning. Read it when a skill references "the design skill", or directly when judging whether code is well-structured. Trigger on "is this well-structured", "how should this be organized", "is this a deep module", "what's a good seam here", "define information hiding".
---

# design

The shared vocabulary for structural judgment: what makes a module well-designed, where a boundary belongs, when an error case can be designed away instead of handled.
Other skills (`spec`, `refactor`, `review`) reference this document instead of asserting "simplicity" or "maintainability" as if the terms were self-evident, so a structural claim is citable and reviewable rather than a matter of taste.
Each section is a lens applied to a structural decision, read rather than run as a procedure.

## Module depth

A module's interface is a cost every caller pays; the functionality behind it is what a caller doesn't have to think about. Depth is that functionality weighed against the interface's complexity.

- A **deep module** hides substantial functionality behind a narrow interface, e.g. a filesystem's `open`/`read`/`write`/`close` hiding disk layout, caching, and buffering.
- A **shallow module**'s interface is about as complex as what it does. A pass-through wrapper, a function whose body is one call to another function with the arguments renamed, is the primary smell: it adds a name without adding depth.
- Judging a proposed split or merge: does the new boundary make each side's interface simpler relative to what it hides, or does it just relocate the same complexity behind a new name?

## Information hiding

What must a caller know to use this correctly, beyond the signature? Every fact a caller has to hold in their head to call something safely is a hiding failure somewhere.

- A **load-bearing leak** is a fact the caller genuinely needs, e.g. an API's rate limit; an **accidental leak** is an implementation detail that escaped only because nothing hid it, e.g. an internal retry count. Fix the second kind; document the first.
- A leak that shows up in more than one caller means the boundary is in the wrong place, not that the callers need reminding.

## Seam placement

A **seam** is the point where a public boundary is crossed: where behavior can be substituted without editing the code on the other side of it. It is also, mechanically, where a test attaches; assert at the seam, not on internals.

- Too low, inside a helper: a test exercises mechanics unrelated to the behavior it's checking.
- Too high, only at the process boundary: testing anything specific means driving the whole system.
- The right seam sits at the real entry point (CLI, endpoint, flow, per the E2E bias in `standards`) that still lets the one thing under test be substituted.

## Error-condition elimination

An error handled well is still a cost: a branch, a message, a caller who has to decide what to do with it. An error that cannot occur is free.

- Before writing the handling, ask whether the precondition that produces the error can be made impossible instead: a type that can't represent the invalid state, a default that removes the empty case, a merge that removes the conflict.
- Only propagate what's left after that question. Propagating everything by default is the shallow move.

## Navigability

A concept should have one place it lives, findable by the name recorded in the repo's ubiquitous-language glossary (`standards`), not scattered across files that each hold a fragment of it.

- Name things after what they are, not how they're currently implemented. A name tied to an implementation detail stops being true the moment the detail changes, and a stale name is the direct cause of a reader, human or agent, failing to find the code that owns a concept.
- Locality: code that changes together lives together. A change that touches many files for one concept is a navigability defect worth naming, not a refactor inconvenience.

## Boundaries

Read while judging or explaining a structural question, never a numbered step in another skill's procedure, and produces no artifact of its own.

- Against `refactor`: a request framed as "is this well-structured" or "how should this be organized" reads `design`; a request framed as "clean this up" or "reduce duplication" invokes `refactor`, which then reads `design` for the vocabulary it judges by.
- Against `tdd` (the `tdd` skill, if you use it): a request to explain or judge a seam reads `design`; a request to drive the test-first loop invokes `tdd`, which reads `design` for the harder calls.
