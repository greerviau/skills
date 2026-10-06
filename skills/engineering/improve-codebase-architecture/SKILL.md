---
name: improve-codebase-architecture
description: Scan a codebase for evidence-backed structural opportunities and rank them before implementation.
disable-model-invocation: true
---

# improve-codebase-architecture

Run `/improve-codebase-architecture` to scan a codebase for evidence-backed opportunities to deepen shallow modules, remove accidental information leaks, improve seam placement, eliminate error conditions, or restore locality.
The output is a ranked HTML report in the OS temporary directory.
This skill does not edit production code or design the selected change's interface.

## Procedure

1. Set the scope. If the user names a module, subsystem, or pain point, scan it and its direct callers first.
   Otherwise find areas that change repeatedly with `git log --oneline` and `git log --name-only`, and use them as the initial scope.
   Widen the scan when history shows no clear hot spot or a candidate's callers cross the initial scope.

2. Read the local vocabulary: `docs/UBIQUITOUS-LANGUAGE.md`, any glossary covering the scoped code, and nearby ADRs or decision records.
   Use the repository's terms for domain concepts.
   Read the `design` skill for structural vocabulary when available. Otherwise use these lenses:

   - Module depth: compare a module's interface complexity with the functionality it hides.
   - Information hiding: identify facts callers must know, separating necessary leaks from accidental ones.
   - Seam placement: find the public boundary where behavior can be substituted and a test should attach.
   - Error-condition elimination: find invalid states that a type, default, or ownership change can make impossible.
   - Navigability: find concepts split across files, or names that make the owning code hard to locate.

3. Explore the code. Delegate independent directory or subsystem scans to subagents when available.
   Trace real entry points, callers, tests, configuration, and recent changes. Do not rely on counts or generic smells alone.
   For each suspected shallow module, apply the deletion test: deleting it should either concentrate complexity in a better owner or show that the split only moved complexity.
   Record file paths, symbols, call relationships, and the code evidence for each candidate.

4. Form candidates. Keep only opportunities with a concrete structural cause and a plausible gain in locality, impact across callers, testability, or error-condition elimination.
   Each candidate records:

   - a short title naming the proposed deepening;
   - the files and symbols involved;
   - the structural lens and evidence;
   - the current friction, in one sentence;
   - the direction of the change, in one sentence, without proposing an interface;
   - expected gains in locality, impact across callers, seam placement, or error-condition elimination;
   - constraints, ADR conflicts, and unknowns;
   - a recommendation strength: `Strong`, `Worth exploring`, or `Speculative`.

   Exclude style preferences, broad rewrites, duplicate candidates, and refactors whose only evidence is file size.
   Reopen an ADR only when the current friction is concrete enough to justify it.

5. Rank by evidence strength first, then structural impact and expected locality.
   Risk and uncertainty lower a recommendation strength but do not hide a candidate.
   A candidate with high theoretical impact and weak evidence ranks below a smaller candidate with strong evidence.
   Choose one top recommendation and cite the files and evidence that place it first.

6. Write the report. Read `HTML-REPORT.md` in this skill's directory for the report shape and diagram patterns.
   Resolve the temporary directory from `$TMPDIR`, falling back to `/tmp` on Unix-like systems and `%TEMP%` on Windows.
   Write a new file named `architecture-review-<timestamp>.html` there.
   The report is one HTML file with inline styles. Use Mermaid or inline SVG for relationship diagrams where they clarify a candidate.
   Each candidate has a before/after visualization, files, problem, direction, gains, recommendation strength, and any relevant ADR warning.
   Keep prose sparse and let the diagrams carry the structural comparison.

7. Open the absolute path with `open` on macOS, `xdg-open` on Linux, or `start` on Windows.
   Return the path and the ranked candidate titles.
   Interactive runs end by asking: `Which of these would you like to explore?`
   Do not start implementation in this invocation.

Autonomous runs do not wait for a selection. Return the report path, the ranked list, and the top recommendation with its evidence, and record that no candidate was selected.

## Scope

- This skill scans and ranks structural opportunities and does not implement them.
- It uses a glossary or code term when one exists and does not invent domain terms.
- It proposes no final interface before the user selects a candidate.
- After selection, use the `spec` skill, if installed, to investigate and plan the change. Otherwise hold an explicit design discussion before editing code.
