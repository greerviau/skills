---
name: mermaid
description: Use when drafting, rendering, or refining a software diagram for a doc, spec, PR, or ADR, including any UML type (class, sequence, state, activity, component, deployment, use case, timing) or an ER diagram - picks the diagram type, then runs the render-and-look loop that catches layout defects invisible in the diagram's source. Trigger on "draw this as a diagram", "make this a mermaid diagram", "draw a sequence diagram", "UML diagram", "render this diagram", "this diagram's layout is a mess", "refine this diagram".
---

# mermaid

Layout defects (crossings, sideways sprawl, dead space) are invisible in mermaid source and show up only in the rendered image, so a diagram never rendered is unchecked.
Draft, render, look, critique, refine, and repeat until the checklist passes. Render at least once.

## Procedure

1. State the intent in one sentence: what relationship or flow the diagram shows, for which reader (for example, "show where the new skills attach to the existing hand-off graph").
2. Pick the diagram type and its syntax from [references/diagram-types.md](references/diagram-types.md). Draft the source from the intent.
3. Render locally and look at the image (see Render mechanics).
4. Critique the image against the layout checklist.
5. Refine and re-render until every item passes.
6. Put only the final fenced mermaid block in the document. For a PlantUML fallback, commit the `.puml` source and rendered `.svg` beside the document instead. Delete the working files and do not commit them.

## Layout checklist

- `direction` inside a subgraph is ignored once an edge crosses the subgraph boundary. A `direction TB` group then lays out horizontally and sprawls the diagram sideways.
- A subgraph box forces its children into a stack and usually leaves dead space beside it. Drop the box unless the grouping is the message, since rank order already shows stages.
- Aspect ratio is between roughly 4:3 and 16:9. A 5:1 sprawl or a 1:3 column means the structure is wrong.
- Edge labels are one to three words. Label width drives node spacing, so a long label pushes the layout apart.
- A skip edge spanning more than two ranks sweeps the margin. Restructure, or allow exactly one.
- Reverse an edge when that flattens a rank without changing meaning. `a -->|x| b` reads the same as its reverse and removes a rank.
- Zero edge crossings. A crossing means the rank assignment is wrong.
- Every label renders as written. A `<>` or a literal `\n` in the image is a syntax error from the label rules in the reference.
- Theme-neutral styling only: stroke-based `classDef`, never `fill`. GitHub renders light and dark themes.

## Render mechanics

Render with the local mermaid CLI:

```
npx -y -p @mermaid-js/mermaid-cli mmdc -i d.mmd -o d.png -b white -s 2
```

The first run downloads Chromium once per machine, so a long wait is normal.
A sandboxed or containerized environment produces two separate failures:

- "No usable sandbox": pass a puppeteer config with `mmdc -p config.json`, where `config.json` contains `{"args": ["--no-sandbox"]}`.
- A missing shared library (`chrome-headless-shell: error while loading shared libraries: libnspr4.so`, or the same for `libnss3.so`): installing the system package needs root, which an agent sandbox usually lacks. Without root, download the `.deb` (`apt-get download libnspr4 libnss3`), extract it without installing (`dpkg-deb -x <package>.deb <dir>`), and set `LD_LIBRARY_PATH` to `<dir>/usr/lib/x86_64-linux-gnu` when running `mmdc`.

Keep working `.mmd` and `.png` files in the scratchpad.
Do not use hosted renderers such as mermaid.ink or the PlantUML server, which publish the diagram content to a third party.

## Delegation

When a subagent is available, give it the intent sentence, the diagram type, and the layout checklist and have it return only the final source, so the renders and intermediate images stay in its context.
Otherwise run the loop inline.

## Scope

This skill does not decide whether a diagram belongs in the document or what it shows. The caller decides.
It does not edit the surrounding prose.
