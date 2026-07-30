---
name: tech-research
description: Use when a technical question needs a sourced, version-pinned answer about third-party or external behavior - what a library's API actually does, what a spec or RFC requires, how a pinned dependency behaves - captured as a durable findings file instead of asserted from memory. Trigger on "how does this library actually handle", "what does the X API do", "check the vendor docs for", "does this version support", "what does the RFC/spec say about", "research how this dependency behaves", "verify this against the docs, not from memory".
---

# tech-research

Investigate a technical question about third-party or external behavior against high-trust primary sources, and capture the answer as a durable, version-pinned findings file.
**The hard rule: every claim carries a citation and a confidence level.**
A claim with neither is model recall, not research, and doesn't belong in the findings file.

## Source hierarchy

Work down this list; drop to a lower rank only when nothing above answers the question:

1. **The installed dependency's own source and tests** - the version actually pinned in this repo (lockfile, `requirements.txt`, `package.json`, `go.mod`, whichever applies). Read the code itself, not a description of it.
2. **Official vendor documentation for the pinned version**, not "latest" - a doc site that only shows current-version content may already have drifted from what's installed; say so when it might have.
3. **Specifications and RFCs**, for protocol- or standard-level questions the vendor docs merely implement.
4. **Release notes and issue trackers**, for "does this version have X" or "was this deliberate" questions the above don't settle.
5. **Everything else** - forums, Q&A sites, third-party writeups - used only to locate a lead, never cited as the answer itself.

**Blog posts and model recall are not sources.** A blog post can point at where to look; it never substitutes for reading the thing it describes. Recalling an API fact from training is exactly the failure this skill exists to prevent - verify it against the hierarchy above, or mark it `unknown`.

## Per-claim confidence

Every claim in the findings file gets a citation (file and line, doc URL and section, RFC section, issue or PR number) and one of:

- **high** - read directly from the pinned source/tests, or from vendor docs explicitly scoped to the pinned version.
- **moderate** - vendor docs without version confirmation, or a spec the implementation hasn't been checked against directly.
- **low** - release notes, issue discussion, or inference from adjacent behavior.
- **unknown** - nothing in the hierarchy answered it. State the open question plainly rather than filling the gap with a guess.

## Version pinning

An API fact is a fact about a version, not the library in general. Record the checked version - read from the lockfile or manifest, not assumed - at the top of the findings file. A version bump invalidates the old answer; re-verify rather than reuse it.

## Procedure

1. **Pin the version.** Find the installed/pinned version of whatever's in question before reading anything else.
2. **Decompose and delegate.** When the question splits into independent sub-questions (several APIs, several libraries, a question plus its edge cases), fan them out to subagents, one per sub-question, each returning sourced findings for its own slice. Run it directly when the question doesn't decompose.
3. **Work the hierarchy.** For each sub-question, start at the top of the source hierarchy and stop at the first rank that answers it with confidence.
4. **Write the findings file.** Default location `docs/analysis/`, filename kebab-case and date-prefixed (e.g. `2026-07-30-websocket-reconnect-backoff.md`), the same convention `spec` uses for `docs/plans/`. State the checked version up top; one claim per line or bullet, each with its citation and confidence.
5. **Report the path**, not the content - point at the file instead of restating findings in conversation.

**Interaction mode** (see `standards`): running autonomously, don't block on an ambiguous question (which library, which version, which of several plausible readings) - research the most likely reading, record the assumption in the findings file, and proceed.

## Boundaries

- Against `spec`: this skill answers questions about third-party or external behavior - what a library actually does, what a spec or RFC actually requires. `spec` discovers scope in this repo's own code - where a concept lives, what calls what. "How does this dependency behave" is `tech-research`; "where in our code does this belong" is `spec`.
- Produces a findings file, not a code change - there's nothing to land. A caller (`spec`, or anyone else) cites the file instead of re-deriving the answer.
- Never smooths uncertainty into a confident-sounding claim. `unknown` plus a stated open question beats a guess.
