---
name: tech-research
description: Use when a technical question needs a sourced, version-pinned answer about third-party behavior, standards, or pinned dependencies - what a library API does, what a standard requires, or how a pinned dependency behaves. Captures findings with citations and confidence levels.
---

# tech-research

Investigate a question about third-party or external behavior against primary sources and record the answer in a version-pinned findings file.
Every claim carries a citation and a confidence level. A claim missing either is model recall and does not belong in the file.

## Source hierarchy

Start at the top and drop a rank only when nothing above answers the question.

1. The installed dependency's own source and tests, at the version pinned in this repo (lockfile, `requirements.txt`, `package.json`, `go.mod`, whichever applies). Read the code, not a description of it.
2. Official vendor documentation for the pinned version, not "latest". A doc site that shows only current-version content may have drifted from what is installed; say so when it might have.
3. Specifications and RFCs, for protocol or standard questions that vendor docs only implement.
4. Release notes and issue trackers, for "does this version have X" or "was this deliberate" questions the above do not settle.
5. Forums, Q&A sites, and third-party writeups, used only to locate a lead and never cited as the answer.

Blog posts and model recall are not sources. A blog post can point at where to look but does not replace reading the thing it describes. Verify any API fact recalled from training against the hierarchy, or mark it `unknown`.

## Per-claim confidence

Each claim gets a citation (file and line, doc URL and section, RFC section, issue or PR number) and one level:

- high: read directly from the pinned source or tests, or from vendor docs explicitly scoped to the pinned version.
- moderate: vendor docs without version confirmation, or a spec the implementation was not checked against.
- low: release notes, issue discussion, or inference from adjacent behavior.
- unknown: nothing in the hierarchy answered it. State the open question instead of guessing.

A synthesized answer built from several claims is itself a claim. It cites the claims it draws on and takes the lowest confidence among them.

## Version pinning

An API fact belongs to a version, not to the library. Record the checked version, read from the lockfile or manifest and not assumed, at the top of the findings file. A version bump invalidates the answer, so re-verify it.

## Procedure

1. Find the pinned version of whatever is in question before reading anything else. When the question is ambiguous (which library, which version, which reading) and no user can answer (`standards`), research the most likely reading, record the assumption in the findings file, and proceed.
2. When the question splits into independent sub-questions (several APIs, several libraries, a question plus its edge cases), fan them out to subagents, one per sub-question, each returning sourced findings for its slice. Otherwise work directly.
3. For each sub-question, start at the top of the hierarchy and stop at the first rank that answers it with confidence.
4. Write the findings file in the location *Artifact location* (`standards`) gives for research findings, named in kebab-case with a date prefix, such as `2026-07-30-websocket-reconnect-backoff.md`. Put the checked version at the top, with one claim per line or bullet, each with its citation and confidence.
   The file is a reference: claims, citations, confidence. Leave out any narrative of the search and any conclusions section that restates a claim.
5. Report the file path instead of restating the findings in conversation.

## Related skills

- This skill answers questions about third-party or external behavior, such as what a library does or what an RFC requires. `spec` discovers scope in this repo's own code. "How does this dependency behave" is `tech-research`, and "where in our code does this belong" is `spec`.
- The output is a findings file, not a code change. A caller quotes the claims it depends on, with their citations, instead of re-deriving the answer.
