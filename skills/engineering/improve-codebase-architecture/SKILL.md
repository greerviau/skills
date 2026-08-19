---
name: improve-codebase-architecture
description: Use when a codebase needs structural opportunities identified and ranked before implementation, with a visual HTML report. Trigger on "/improve-codebase-architecture", "scan the architecture", "find structural opportunities", "review the codebase architecture", "where should we deepen this codebase".
disable-model-invocation: true
---

# improve-codebase-architecture

Run `/improve-codebase-architecture` explicitly to scan a codebase for evidence-backed opportunities to make shallow modules deeper, reduce accidental information leaks, improve seam placement, eliminate error conditions, or restore locality.
The output is a ranked HTML report in the operating system's temporary directory.
This skill does not edit production code or design the selected change's interface.

## Procedure

1. **Set the scope.** If the user names a module, subsystem, or pain point, scan it and its direct callers first.
Otherwise, inspect recent history with `git log --oneline` and `git log --name-only` to find areas that change repeatedly, then use those areas as the initial scope.
Widen the scan when history has no clear hot spot or when a candidate's callers cross the initial scope.

2. **Read the local vocabulary.** Read `docs/UBIQUITOUS-LANGUAGE.md` and any glossary that covers the scoped code.
Read nearby ADRs or decision records when they exist.
Use the repository's terms for domain concepts.
When the `design` skill is available, read it for the structural vocabulary; otherwise use these lenses:

   - **Module depth:** compare the complexity of a module's interface with the functionality it hides.
   - **Information hiding:** identify facts callers must know, separating load-bearing leaks from accidental leaks.
   - **Seam placement:** find the public boundary where behavior can be substituted and where a test should attach.
   - **Error-condition elimination:** look for invalid states that a type, default, or ownership change can make impossible.
   - **Navigability:** find concepts split across files or names that make the owning code hard to locate.

3. **Explore the code.** Delegate independent directory or subsystem scans when subagents are available.
Trace real entry points, callers, tests, configuration, and recent changes.
Do not rely on counts or generic smells alone.
For every suspected shallow module, apply the deletion test: deleting the module should either concentrate complexity in a better owner or reveal that the proposed split only moves complexity.
Record file paths, symbols, call relationships, and the code evidence for each candidate.

4. **Form candidates.** Keep only opportunities with a concrete structural cause and a plausible change in locality, impact across callers, testability, or error-condition elimination.
Each candidate records:

   - a short title naming the proposed deepening;
   - the files and symbols involved;
   - the structural lens and evidence;
   - the current friction in one sentence;
   - the direction of the change in one sentence, without proposing an interface;
   - expected gains in locality, impact across callers, seam placement, or error-condition elimination;
   - constraints, ADR conflicts, and unknowns;
   - a recommendation strength: `Strong`, `Worth exploring`, or `Speculative`.

Do not list style preferences, broad rewrites, duplicate candidates, or refactors whose only evidence is file size.
Do not re-litigate an ADR unless the current friction is concrete enough to justify reopening it.

5. **Rank candidates.** Rank by evidence strength first, then by structural impact and expected locality.
Use risk and uncertainty to lower a recommendation strength, not to hide it.
Put a candidate with high theoretical impact below a smaller candidate when its evidence is weak.
Choose one top recommendation and cite the files and evidence that place it first.

6. **Write the report.** Read `HTML-REPORT.md` in this skill directory for the report shape and diagram patterns.
Resolve the temporary directory from `$TMPDIR`, falling back to `/tmp` on Unix-like systems and `%TEMP%` on Windows.
Write a fresh file named `architecture-review-<timestamp>.html` there.
The report is a single readable HTML file with inline styles; use Mermaid or inline SVG for relationship diagrams when they clarify the candidate.
Each candidate has a before/after visualisation, files, problem, direction, gains, recommendation strength, and relevant ADR warning.
Keep prose sparse and make the diagrams carry the structural comparison.

7. **Open and return the report.** Open the absolute path with `open` on macOS, `xdg-open` on Linux, or `start` on Windows.
Return the path and the ranked candidate titles.
Interactive runs end by asking: `Which of these would you like to explore?`
Do not start implementation in this invocation.

**Interaction mode:** In an autonomous run, do not wait for a candidate selection.
Return the report path, the ranked list, and the top recommendation with its evidence; record that no candidate was selected and leave implementation untouched.

## Boundaries

- This skill scans and ranks structural opportunities; it does not implement them.
- It does not invent domain terms when the glossary or code provides one.
- It does not propose a final interface before the user selects a candidate.
- After selection, use the `spec` skill, if installed, to investigate and plan the change; otherwise continue with an explicit design discussion before editing code.
