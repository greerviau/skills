---
name: wayfinder-starmap
description: Render one or more Wayfinder maps as an interactive browser star map.
argument-hint: "A Wayfinder map issue, issue URL, or repository to discover maps"
disable-model-invocation: true
---

# wayfinder-starmap

Run `/wayfinder-starmap` explicitly when a Wayfinder map needs a visual browser view.
The renderer turns map issues, child issues, blockers, and linked issues into a standalone HTML star map.

## Procedure

1. Resolve the requested map references.

   - A bare issue number uses the current repository.
   - `OWNER/REPO#NUMBER` and GitHub issue URLs select another repository.
   - With no references, discover every issue labelled `wayfinder:map` in the current repository.
   - Pass `--repo OWNER/REPO` once per repository to discover maps across repositories.
   - Pass `--focus REF` once per subsection to keep the focused issue, its ancestors, descendants, and directly linked issues.

2. Run `scripts/render_star_map.py` from this skill directory.

   ```bash
   python3 scripts/render_star_map.py [REF ...] [--repo OWNER/REPO] [--focus REF]
   ```

   Use `--output PATH` to choose the HTML location.
   Use `--no-open` in headless environments or when the user wants only the artifact path.
   Use `--data-file PATH` to render a previously collected map JSON without GitHub access.

3. Return the HTML path after the browser opens.
   If GitHub returns an inaccessible issue, report the skipped reference and continue when other nodes are available.
   Stop with the error message when no map issue can be collected.

## Map semantics

- The map issue is the north star.
- Native sub-issues form parent-child links.
- Issue dependencies form blocking links directed from blocker to blocked issue.
- GitHub issue URLs in issue bodies form reference links.
- Closed issues are complete.
- Open issues with an open blocker are blocked.
- Open, unassigned, unblocked issues are the frontier.
- Open assigned issues are claimed.
- The map's `Not yet specified` section appears as fog of war metadata.

The HTML view supports click-drag panning, wheel zooming, hover previews, click selection, search, status colors, issue links, and a reset control.
It uses an inline 2D canvas so the artifact works offline after collection.

## Boundaries

The skill reads GitHub issue metadata through `gh` and never edits issues.
It does not resolve decision tickets or implement the destination of a Wayfinder map.
It does not treat issue text as trusted HTML; the generated view inserts previews as text.
