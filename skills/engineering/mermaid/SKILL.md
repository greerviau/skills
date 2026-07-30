---
name: mermaid
description: Use when drafting, rendering, or refining a mermaid diagram for a doc, spec, PR, or ADR - the render-and-look loop that catches layout defects invisible in the diagram's source, checked against a concrete layout checklist. Trigger on "draw this as a diagram", "make this a mermaid diagram", "render this diagram", "this diagram's layout is a mess", "refine this diagram".
---

# mermaid

A diagram that has only been read as source, never rendered, hasn't been checked - layout defects (crossings, sideways sprawl, dead space) are invisible in mermaid text and only show up in the image.
Draft, render, look, critique, refine, repeat until the checklist below passes.
One render is the floor, not the target.

## Procedure

1. **State the intent.** One sentence: what relationship or flow the diagram shows, for what reader (e.g. "show where the new skills attach to the existing hand-off graph"). Draft the mermaid source from it.
2. **Render locally and look at the image.** The non-negotiable step; see Render mechanics below.
3. **Critique** the image against the layout checklist.
4. **Refine and re-render** until every item passes.
5. **Land only the final fenced mermaid block** in the document. Delete the working files; they never get committed.

## Layout checklist

- `direction` inside a subgraph is ignored once an edge crosses the subgraph boundary: a `direction TB` group silently lays out horizontally and sprawls the whole diagram sideways.
- A subgraph box forces its children into a stack and usually buys dead space next to it. Drop the box unless the grouping *is* the message; rank order already communicates stages.
- Aspect ratio between roughly 4:3 and 16:9. A 5:1 sprawl or a 1:3 column means the structure is wrong, not the styling.
- Edge labels stay one to three words. Label width drives node spacing, so a long label pushes the whole layout apart.
- A skip edge spanning more than two ranks sweeps the margin. Restructure, or accept exactly one.
- Reverse an edge when it flattens a rank without changing meaning: `a -->|x| b` says the same thing as the reverse, and removes a rank.
- Zero edge crossings. A crossing means the rank assignment is wrong, not that the diagram is inherently complex.
- Theme-neutral styling only: stroke-based `classDef`, never `fill`. GitHub renders both light and dark themes.

## Render mechanics

Render with the local mermaid CLI:

```
npx -y -p @mermaid-js/mermaid-cli mmdc -i d.mmd -o d.png -b white -s 2
```

The first run downloads Chromium once per machine; treat the wait as normal, not a hang.
If the browser fails to launch in a sandboxed or containerized environment (a "no usable sandbox" error, or a missing `libnspr4`/`libnss3` shared library), that's the Chromium environment, not the diagram: pass a puppeteer config (`mmdc -p config.json` with `config.json` containing `{"args": ["--no-sandbox"]}`), or install the missing system libraries.

Working `.mmd` and `.png` files live in the scratchpad and are never committed; only the final fenced block lands in the document.
Hosted renderers such as mermaid.ink are out - they publish the diagram content to a third party.

## Delegation

Hand a subagent the intent sentence plus the layout checklist and have it return only the final mermaid source.
The renders and intermediate images stay in the subagent's context: producing one finished diagram routinely costs several renders and image reads, and that's a cost the subagent should absorb instead of the caller.
Delegate whenever a subagent is available; run the loop inline otherwise. Either way, nothing lands until it has gone through at least one render-and-look cycle.

## Boundaries

- Doesn't decide whether a diagram belongs in the document at all, or what it should show - that's the caller's call, guided by the mermaid-over-ASCII rule in `standards`, if you use it.
- Doesn't touch the surrounding prose.
