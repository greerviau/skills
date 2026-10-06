---
name: dep-upgrade
description: Use when upgrading Python dependencies in a uv-managed project. Keeps manifests and uv.lock consistent, updates git-sourced internal packages in lockstep, and verifies the downstream project instead of the upgraded package's own suite. Trigger on "upgrade a dependency", "bump a package", "refresh uv.lock", "update the internal package tag", "update dependencies", "renovate this dependency", "upgrade this library".
---

# dep-upgrade

Upgrade dependencies in a uv-managed Python project with a targeted resolver run, a reviewable lockfile diff, and downstream verification.
Use `uv` for dependency, environment, and test commands. Do not use `pip`, `pip-tools`, Poetry, or hand-edited lockfile entries.

## Procedure

1. Capture the target and current state.
   Run `git status --short --branch` and record the issue, branch, commit, and requested package, version, tag, or revision.
   When the target version, tag, or scope is missing and no user can answer (`standards`), take the narrowest compatible interpretation the repository can verify, record the assumption in the report, and proceed. Stop when no defensible target exists.
   Locate every `pyproject.toml`, `uv.lock`, workspace member, and CI or README command that defines or verifies the project.
   Confirm the project uses uv and has a lockfile.
   Run `uv lock --check`. If the lockfile is stale or missing, stop unless repairing it is part of the request.

2. Inventory dependency declarations.
   Search all workspace manifests and source tables for the target package, its extras and markers, and every `git+` source.
   Classify the target as a registry, URL, local or workspace, or git-sourced dependency.
   Keep the existing dependency group, markers, extras, source URL, and Python constraints unless the request changes them.
   Do not add a direct requirement to upgrade a transitive dependency.

   For a git-sourced internal package, find every declaration in the workspace that points to the same repository.
   When the repository is reachable, strip the `git+` prefix from the source URL and verify the requested tag exists with `git ls-remote --exit-code --refs --tags <git-url> "refs/tags/<tag>"`.
   Move every intended package from that repository to the same tag before resolving, so none stays on the previous tag.
   Leave unrelated repositories and intentionally pinned revisions unchanged.

3. Establish a baseline.
   Install the current lockfile exactly with `uv sync --locked`.
   Run the downstream project's documented test suite and required checks through `uv run`, using the commands CI or the README uses when available.
   Record each command and result before editing dependency files.
   If the baseline fails, stop and report the pre-existing failure. The upgrade can be neither blamed for it nor cleared of it.

4. Change the declaration and resolve.
   Change the direct requirement or git tag in the manifest. Use `uv add` when its options express the intended group, source, marker, and version change, and otherwise edit `pyproject.toml` directly.
   Never edit `uv.lock` by hand.
   Resolve a registry or transitive target with `uv lock --upgrade-package <package>`.
   Use `uv lock --upgrade` only when the request asks for a broad refresh, and record that scope.
   Resolve after all lockstep internal tag changes are in place.

5. Audit the lockfile diff.
   Run `uv lock --check`, `uv sync --locked`, and `git diff --check`.
   Read `git diff -- pyproject.toml uv.lock` in full.
   Confirm the target version, source, tag, or revision matches the request and every lockstep internal package resolves from the requested tag.
   Review every transitive change, marker, artifact, and source change. Revert unrelated resolver churn or explain why the target requires it.
   A lockfile that resolves only after an undeclared manifest change is invalid.

6. Verify the downstream project.
   Rerun the baseline commands in the updated environment, then the project's full downstream suite and its runtime or end-to-end entry point if one exists.
   Do not use the upgraded package's own test suite as compatibility evidence. The consumer project is under test.
   Compare the results with the baseline.
   An installation or lock failure, a new test failure, a changed runtime result, or a missing internal tag blocks the upgrade until the cause is fixed or the target is rejected.
   If the dependency's external behavior needs source-backed investigation, use the `tech-research` skill if available and record its findings before choosing a compatibility workaround.

7. Report the upgrade:

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

   If the change is being landed, pass it to the repository's normal development workflow after verification.

## Scope

- This skill owns dependency declaration changes, uv resolution, lockfile review, and downstream verification. It does not fix application code broken by an incompatible upgrade.
- Keep upgrades targeted unless a broad refresh is requested.
- Flag unrelated dependency or application defects for their own issue and branch.
