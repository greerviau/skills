# Coding standards

The rules for code: comments, docstrings, identifiers, and tests.
They apply in every repo.
`SKILL.md` holds the rules for prose, artifacts, and workflow.

General rules go under their topic heading.
A rule that holds only for one language goes under a `## <Language>` heading.

## Comments and docstrings

The present-tense and no-change-narrative rules in `SKILL.md` (*Documentation and comments*) apply to every comment.

- A comment carries a fact the code cannot state: a non-obvious constraint, a reason, a subtlety, or an external contract the code must match. Delete comments that narrate what the code does.
- For each comment, name the fact it carries and check whether the code on the lines it describes already states it. Delete the comment when the fact is unnamed, the code states it, or you cannot decide.
- Limit inline comments to two lines and never add an example. A comment that needs an example or a third line means the code needs fixing.
- A docstring states what the thing does, then parameters, return, and raises, in the language's standard format (PEP 257 or Google style for Python). Nothing else belongs in it.
- Keep a docstring summary to one line. Add a body only when a caller cannot use the thing correctly without it. A docstring that walks through the implementation, enumerates edge cases, or argues for the design is over budget at any length.
- Omit parameters the signature and types already state. "path: str, the path as a string" carries no fact.
- Module-level documentation is exempt from the two-line inline cap.

## Identifiers

- Name identifiers with full words, never abbreviations or truncations: `configuration` not `cfg`, `index` not `idx`, `sample_count` not `n_samps`. Domain acronyms the glossary records (`mz`, `xic`, `ms2`) are names and stay verbatim.
## Testing

- Build every behavior change **test-first**: write a test at the change's public seam, run it, and confirm it fails because the behavior is missing (not an import error or a missing fixture). Then write the minimum code to pass, and refactor while the tests stay green.
- Record each red run as the test name and its failure message. The PR's testing section cites it.
- A missing harness is not an exemption. Build the fixture, runner, or driver first, in its own commit.
- Changes with no behavior to test are exempt: documentation, comments, formatting, and renames the existing suite covers. So are changes another guard proves: dependency upgrades (the existing suite), refactors (characterization tests), performance work (a benchmark), and prototypes (discarded).
- Weight tests toward E2E over narrow unit tests. Exercise the functionality as a user does, through the real entry point (CLI, endpoint, UI flow).
- A bug fix carries a regression test built from the reproduction. It fails before the fix and passes after.
- Flakiness is a defect. Do not use unseeded randomness, real clocks, order-dependent tests, or un-stubbed network calls.
