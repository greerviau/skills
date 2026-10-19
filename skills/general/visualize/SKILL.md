---
name: visualize
description: Use when a concept, system, algorithm, or dataset is easier to see than to read and the user wants it drawn, plotted, demonstrated, or made interactive. Builds the smallest visual that carries the explanation, renders it, and checks the render. Trigger on "show me", "visualize this", "draw this", "plot this", "diagram", "demonstrate", "make this interactive".
---

# visualize

Demonstrate with a visual the reader can take in within seconds.
The visual carries the explanation and prose only labels it.
Build the smallest form that shows the point, render it, and look at the render before showing the user.

## Procedure

1. State the claim in one sentence: the one thing the visual must make clear.
   When the visual has two claims, build two visuals.
   When the user is learning the concept and a user can answer, ask them to predict the outcome before showing it.
2. Pick the form from the table.
3. Build it with the rules below.
4. Render it and look at the result with [references/render-and-look.md](references/render-and-look.md).
5. Fix every defect on the checklist and render again until none remain.
6. Show it. Put text visuals in chat, give the path of a file, and open an HTML file in the browser.
   Add one caption sentence that states the claim.

## Forms

| Content | Form |
| --- | --- |
| Logic or an algorithm | Pseudocode with the state annotated at each step |
| Control flow, call structure, file layout | Indented tree in a text block |
| Component interaction, sequence, state machine, data flow | Mermaid block, or hand-drawn SVG when layout matters |
| A trend, distribution, or comparison of numbers | Plot saved as PNG, or inline SVG in a page |
| Behavior that depends on a parameter (a threshold, rate, or size) | Single-file HTML page with one control on that parameter and the output updating beside it |
| A process over time | HTML page with a stepper that advances one step per click |
| A change | Before and after side by side in the same layout, or a diff block |

## Rules

- Draw the mechanism and not its name.
  Label each arrow with a verb, and use real names and values.
- Encode state with shape, position, or pattern as well as color.
- Show the claim in the initial state, without interaction.
- Expose only the parameters the claim depends on.
- Build HTML from [references/page-skeleton.html](references/page-skeleton.html).
  The page is one file with no build step, inline SVG for figures, and libraries only from cdnjs.cloudflare.com or cdn.jsdelivr.net at an exact version.
- An HTML page sends nothing back to the agent, so ask the user any question in chat.

## Output location

Write files to the path the user gives.
Otherwise create a directory with `mktemp -d` and write there, so the visual does not enter the user's project.
