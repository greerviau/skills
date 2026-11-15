# Build the recipe

Write the recipe for an agent that has never seen the app.

## 1. Read the repo

Answer these from the code, docs, and scripts, and ask the user only what you cannot observe:

- Surface: what a user touches, such as a web UI, desktop app, mobile app, CLI or TUI, API, or library. Pick the primary one and note the others.
- Run: how the app starts locally. Prefer the repo's documented dev command (package scripts, Makefile, README). Note ports, environment variables, seed data, and auth.
- Drive: how an agent can operate it. Prefer harnesses the repo already has, such as Playwright or Cypress specs, expect scripts, PTY helpers, HTTP endpoints, or a debug port. Otherwise use browser automation over CDP for web and Electron, tmux or a PTY for a CLI or TUI, and HTTP for a service.
- Observe: what evidence can be captured, such as screenshots, terminal transcripts, response bodies, logs, exit codes, and database state.
- Isolate: whether two instances can run side by side with separate ports, data directories, and profiles.

When the checkout does not build or start, report the failing command and its output, and stop without changing app code.
When an irrelevant missing asset blocks startup, such as a sample config or a static directory the app never serves, the recipe may create it, labeled as verification setup, and remove it in cleanup.

## 2. Write the recipe

Write it where the repo keeps project skills, `.agents/skills/` or `.claude/skills/`.
When the repo has neither, write `.agents/skills/verify-<app>/` and add a relative symlink at `.claude/skills/verify-<app>` that points to it.

`SKILL.md` has frontmatter with `name: verify-<app>` and a `description` that names the app, its surface, and when to use it.
Fill each section from what step 1 found, with real commands and selectors from this repo:

- Launch: the exact command that starts an instance from an empty data directory, including migrations and seed data, and the signal that it is ready to use. A process that answers a health check while its init scripts still run is not ready. Record the PID. For a short-lived CLI or TUI, launch builds the binary or installs dependencies once, and each drive starts in its own PTY or tmux session.
- Doctor: one read-only check that the instance is worth driving: the process is up, the build matches the checkout, the port belongs to this instance, and auth is valid.
- Drive: the harness commands, using stable handles such as ARIA labels, data attributes, prompt strings, and route paths, never coordinates or tab order.
- Evidence: what to capture for each proof and the directory it goes to, outside the checkout and outside anything cleanup removes.
- Cleanup: how to stop the instances a run started, by recorded PID, never by process name, and remove scratch state while keeping evidence.
- Helpers: each script the recipe ships is executable, and the recipe shows how to call it.

## 3. Seed the feature map

Create `verify-<app>/features/README.md` as an index, with one file per user-facing feature beside it, starting with the 3 to 5 most used, found from routes, commands, menus, or docs.
Each feature file has these sections:

- `Sub-features`
- `How to reach it`: the user's path to the feature.
- `Driving it`: the harness commands for each entry point.
- `Gotchas`: preconditions, flaky steps, and seed data the journey needs.

## 4. Prove the recipe

Run the recipe end to end once: launch, doctor, drive one mapped feature, capture evidence, and clean up.
After cleanup, confirm the evidence still exists.
Fix each failing step, and run cleanup after every failed attempt so no processes or ports are left behind.
When you proved it in a stand-in for the real target, such as a container in place of a fresh machine, list each setup step the stand-in did that the target will not, as unverified.
