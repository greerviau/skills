---
name: design
description: Shared vocabulary for judging code structure through module depth, information hiding, seam placement, error-condition elimination, and navigability. Use when asking whether code is well-structured, how to organize it, whether a module is deep, or where a seam belongs.
---

# design

Shared vocabulary for structural judgment: what makes a module well designed, where a boundary belongs, and when an error case can be designed away instead of handled.
`spec`, `refactor`, and `review` cite this document instead of asserting "simplicity" or "maintainability", so a structural claim can be checked.
Each section is a lens to apply to a structural decision.

## Module depth

A module's interface is a cost every caller pays. The functionality behind it is what callers do not have to think about. Depth is that functionality weighed against the interface's complexity.

- A **deep module** hides substantial functionality behind a narrow interface. A filesystem's `open`/`read`/`write`/`close` hides disk layout, caching, and buffering.
- A **shallow module** has an interface about as complex as what it does. A pass-through wrapper, whose body is one call to another function with renamed arguments, adds a name and no depth.
- To judge a proposed split or merge, ask whether the new boundary simplifies each side's interface relative to what it hides, or moves the same complexity behind a new name.

## Information hiding

Ask what a caller must know to use this correctly beyond the signature. Each fact a caller must hold in mind to call something safely is a hiding failure somewhere.

- A **necessary leak** is a fact the caller needs, such as an API's rate limit. An **accidental leak** is an implementation detail that escaped because nothing hid it, such as an internal retry count. Fix accidental leaks and document necessary ones.
- A leak that appears in more than one caller means the boundary is in the wrong place.

## Seam placement

A **seam** is where a public boundary is crossed: where behavior can be substituted without editing the code on the other side. It is also where a test attaches. Assert at the seam, not on internals.

- A seam too low, inside a helper, makes tests exercise mechanics unrelated to the behavior under test.
- A seam too high, only at the process boundary, forces any specific test to drive the whole system.
- The right seam is the real entry point (CLI, endpoint, flow, per the E2E bias in `standards`) that still lets the one thing under test be substituted.

## Error-condition elimination

A handled error still costs a branch, a message, and a caller who must decide what to do. An error that cannot occur costs nothing.

- Before writing the handling, ask whether the precondition producing the error can be made impossible: a type that cannot represent the invalid state, a default that removes the empty case, a merge that removes the conflict.
- Propagate only the errors that remain. Propagating everything by default produces shallow modules.

## Navigability

A concept lives in one place, findable by its name in the repo's ubiquitous-language glossary (`standards`), instead of being split across files that each hold a fragment.

- Name things for what they are, not how they are currently implemented. A name tied to an implementation detail becomes false when the detail changes, and a stale name keeps readers, human or agent, from finding the code that owns a concept.
- Code that changes together lives together. A change touching many files for one concept is a navigability defect.

## Related skills

- A request framed as "is this well-structured" or "how should this be organized" reads `design`. A request framed as "clean this up" or "reduce duplication" invokes `refactor`, which reads `design` for its vocabulary.
- A request to explain or judge a seam reads `design`. A request to run the test-first loop invokes `tdd` (if you use it), which reads `design` for harder calls.
