---
name: dep-upgrade
description: Use when upgrading Python dependencies in a uv-managed project. Keeps manifests and uv.lock consistent, updates git-sourced internal packages in lockstep, and verifies the downstream project rather than the upgraded package's own suite. Trigger on "upgrade a dependency", "bump a package", "refresh uv.lock", "update the internal package tag", "update dependencies", "renovate this dependency", "upgrade this library".
---

# dep-upgrade

Upgrade dependencies in a uv-managed Python project with a targeted resolver run, an auditable lockfile diff, and downstream verification.
Use `uv` for dependency, environment, and test commands; do not use `pip`, `pip-tools`, Poetry, or hand-edited lockfile entries.

## Procedure

1. **Capture the target and current state.**
   Run `git status --short --branch` and record the issue, branch, commit, and requested package, version, tag, or revision.
   Locate every `pyproject.toml`, `uv.lock`, workspace member, and CI or README command that defines or verifies the project.
   Confirm that the project uses uv and that a lockfile exists.
   Run `uv lock --check`; stop if the existing lockfile is stale or missing unless repairing that state is part of the request.

2. **Inventory dependency declarations.**
   Search all workspace manifests and source tables for the target package, its extras and markers, and every `git+` source.
   Classify the target as a registry dependency, a URL dependency, a local or workspace dependency, or a git-sourced dependency.
   Preserve the existing dependency group, markers, extras, source URL, and Python constraints unless the request changes them.
   Do not add a direct requirement merely to upgrade a transitive dependency.

   For a git-sourced internal package, find every declaration that points to the same repository across the workspace.
   Remove the `git+` prefix from the source URL, then verify that the requested tag exists with `git ls-remote --exit-code --refs --tags <git-url> "refs/tags/<tag>"` when the repository is reachable.
   Update every intended package from that repository to the same tag before resolving; do not leave one internal package on the previous tag.
   Keep unrelated repositories and intentionally pinned revisions unchanged.

3. **Establish a baseline.**
   Install exactly the current lockfile with `uv sync --locked`.
   Run the downstream project's documented test suite and required checks through `uv run`, using the same commands that CI or the README uses when available.
   Record each command and result before editing dependency files.
   If the baseline fails, stop and report the pre-existing failure; an upgrade cannot be credited with or cleared of that failure.

4. **Change the declaration and resolve.**
   Change the direct requirement or git tag in the manifest, using `uv add` when its options express the intended group, source, marker, and version change; otherwise edit `pyproject.toml` directly.
   Never edit `uv.lock` by hand.
   Resolve a registry or transitive target with `uv lock --upgrade-package <package>`.
   Use `uv lock --upgrade` only when the request explicitly asks for a broad refresh, and record that scope.
   Resolve after all lockstep internal tag changes are present.

5. **Audit the lockfile diff.**
   Run `uv lock --check`, `uv sync --locked`, and `git diff --check`.
   Inspect `git diff -- pyproject.toml uv.lock` in full.
   Confirm that the target version, source, tag, or revision matches the request and that every lockstep internal package resolves from the requested tag.
   Review every transitive change, marker, artifact, and source change; revert unrelated resolver churn or explain why the target requires it.
   A lockfile that resolves only after an undeclared manifest change is not valid.

6. **Verify the downstream project.**
   Run the exact baseline commands again in the updated environment, then run the project's full downstream suite and its runtime or end-to-end entry point when one exists.
   Do not use the upgraded package's own test suite as compatibility evidence; the consumer project is the test subject.
   Compare the updated results with the baseline.
   Treat an installation or lock failure, a new test failure, a changed runtime result, or a missing internal tag as a blocked upgrade until the cause is fixed or the target is rejected.
   If the dependency's external behavior needs source-backed investigation, use the `tech-research` skill if available and record its findings before selecting a compatibility workaround.

7. **Report the upgrade.**
   Return this record:

   ```text
   Target: <package and requested version, tag, or revision>
   Source: <registry, URL, local/workspace, or git repository>
   Manifest changes: <paths and declarations changed>
   Resolver command: <exact uv command>
   Lockfile: <checked, with the relevant versions/sources and any required transitive changes>
   Internal tag set: <all packages and the resolved tag, or not applicable>
   Baseline: <commands and results>
   Downstream verification: <commands and results>
   Dependency's own suite: not used as compatibility evidence
   Result: <verified|blocked|baseline-failed|regression>
   Remaining risk: <known issue or none known>
   ```

   If the change is being landed, hand it to the repository's normal development workflow after this verification.

## Boundaries

- This skill owns dependency declaration changes, uv resolution, lockfile review, and downstream verification; it does not own application fixes caused by an incompatible upgrade.
- Keep upgrades targeted unless a broad refresh is explicitly requested.
- Flag unrelated dependency or application defects for their own issue and branch.

**Interaction mode** (see `standards`): when running autonomously and the target version, tag, or scope is missing, choose the narrowest compatible interpretation, record the assumption in the report, and proceed when the repository can verify it. Stop when no defensible target exists or when the baseline is not green.
