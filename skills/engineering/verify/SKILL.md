---
name: verify
description: Use when proving that a change works in the running app (web, desktop, mobile, CLI, TUI, or service) by driving it the way a user does, or when asked to set up a reusable way for agents to launch and drive a project's app. Not for running the test suite alone.
---

# verify

Prove a change works by driving the real app through the path a user takes, and capture evidence that survives teardown.
The project's **recipe** is a project-local skill named `verify-<app>` that records how to launch the app, run its doctor check, drive it, capture evidence, and clean up, plus a feature map.
Use the recipe when the repo has one, and build it on first use when it does not.

## 1. Find or build the recipe

Look for `verify-*/SKILL.md` under `.agents/skills/` and `.claude/skills/` in the repo, and under `skills/` in the Git common directory (`git rev-parse --path-format=absolute --git-common-dir`).
When none exists, read [references/build-recipe.md](references/build-recipe.md), build the recipe, and commit it in a commit of its own, on a new branch when the current branch is the default branch.
When the user or the repo's agent instructions (`AGENTS.md` or equivalent) say not to write documents to the repo, build it at `skills/verify-<app>/` in the Git common directory, and tell the user it stays local.
When the user asked only for the recipe, stop after building and proving it, and report the recipe's path and the proof run's evidence.

## 2. Check the instance

Launch an instance of your own with the recipe's launch command, and wait for its ready signal.
Never drive an instance the user is using.
When the recipe says two instances cannot run side by side and one is already running, stop and report it.
Run the recipe's doctor check.
When a recipe step fails because the app changed, fix the recipe, prove the fixed step, and include the fix in the same change.

## 3. Drive

For each behavior the change claims, drive the real user path with the recipe's harness:

- Use the user's entry points, never internal setters, test-only endpoints, or seeded state the user could not reach.
- Cover every entry point the feature map lists for the feature, not only the convenient one.
- Capture the action and the resulting state, not only the final screen.
- Check side effects alongside what is visible: files written, rows inserted, requests and messages sent.
- Mock only where a production boundary already isolates an external system.
  When the safe path is a dry run or test mode, observe what it actually skips (files, network, git refs) instead of trusting its name.

When a journey needs a precondition the seed data lacks, report the journey as not verified and record the missing precondition in the feature's gotchas.
Never weaken a journey to make it pass.
When the change adds a user-facing feature or entry point, add it to the feature map.

## 4. Clean up

Stop only the processes you started, by the PIDs you recorded, and remove the instance's scratch state.
Keep the evidence in the location the recipe names, and confirm it still exists after cleanup.

## 5. Report

For each claimed behavior, give the steps you ran, the evidence path, and the result: verified, failed (the app did the wrong thing), or not verified (the journey could not run or the evidence does not decide).
Only verified is a pass.
