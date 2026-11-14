---
name: ui-design
description: Use when building, restyling, or polishing user interface, when the user asks for UI mockups, visual explorations of a feature, or screen redesigns before implementation, or when a screen looks generic, templated, or AI-made. Excludes disposable experiments that test technical feasibility, data plots, and software diagrams.
---

# ui-design

Build user interface to the **design standard** (the rules under "Apply the design standard"), render it, and check the render before showing it.
When the user asks for a **mockup** (a reviewable UI artifact built before implementation), keep application source, dependencies, and configuration unchanged until implementation is requested, and build a standalone artifact.
Otherwise build in the project's own stack and components.
Do not create issues as part of this workflow.

## Ground the design

Read the affected screens, relevant product rules, and existing visual assets.
Find the project's design tokens, component library, icon set, and fonts, and build with them.
The project's existing system overrides the defaults in the design standard. Apply a default only where the project sets nothing.
Preserve the existing logo, fonts, terminology, and product facts unless the request changes them.
For an existing product, inspect representative populated screens and relevant empty or error states when access is available.
Resolve an ambiguity that changes a product rule before depending on it, and continue independent layout work.

Translate the user's visual constraints into observable checks.
Record layout relationships separately for desktop and mobile when they differ.

## Apply the design standard

Layout:
- Take every margin, gap, and padding from one spacing scale. Default: 4, 8, 12, 16, 24, 32, 48, 64, 96.
- Align every block to the container edges or the grid columns, with equal left and right content edges.
- Give each row of cards one height.
- Nest boxes at most two deep.

Type:
- Use one family, or a display face and a text face with fixed jobs, from at most four font files.
- Make each heading level at least 1.2 times the size of the next. Give each kind of element one size across the product (every card title, every figure).
- Set running text at 16px or more with line height 1.5 to 1.7 and lines of at most 75 characters. Dense UI (tables, sidebars, field hints) may use 14px. Set nothing under 12px.
- Use sentence case for headings, labels, and buttons, and never tracked capitals for labels.
- Set numbers that line up in columns with `font-variant-numeric: tabular-nums`.
- Keep every word as live text, never baked into an image.

Colour:
- Keep the interface mostly neutral. Colour comes from content, data, and state.
- Use one near-black ink for text (not `#000`), with hairlines at 10 to 15% of it.
- Use one accent for the primary action, links, focus, and selection.
- Meet WCAG 2.2 AA contrast: 4.5:1 for text, 3:1 for text of 24px or 18.66px bold, and 3:1 for control boundaries and focus indicators against their neighbours.
- Use muted text only for labels, metadata, and timestamps, still at 4.5:1.
- Pair every status colour with an icon or text.
- When the project has a dark theme, apply every colour rule in both themes.

Components:
- Mark the main action of each view with the only filled button. Give secondary actions one other style and use text links for the rest.
- Keep one radius scale, one card style, one link style, and one icon set at one stroke weight.
- Make touch targets at least 44px tall. On pointer-only dense UI, make targets at least 24px with 8px between neighbours.
- Give every control an accessible name. An icon-only button gets an `aria-label`.
- Put a visible label above each form field. A placeholder is never the label.
  Give each field the matching `type` and `autocomplete`, and use 16px input text on phones.
  Validate on submit, show each error under its field naming the field and what to enter, and move focus to the first invalid field.
- Step headings down one level at a time, and keep Tab order equal to reading order (no `tabindex` above 0).
- Show the focus ring at once, never hidden under a sticky header.

Motion:
- Animate only `transform` and `opacity`, with one ease-out curve and no bounce. Use 100 to 200ms for hover and press.
- Leave content complete at rest, without script, and under `prefers-reduced-motion`. Do not reveal blocks as the page scrolls.

States:
- For each surface under review, design the populated, empty, loading, and error states, and the longest realistic content (long names, many items, large numbers).
- Write the empty state as what belongs there and how to add the first one, and the confirmation in the button's own words.

Avoid these generated-UI patterns unless the project already uses them:
- A small label (eyebrow) over every section heading.
- A row of three or four large figures over one-word labels (a stat strip). Show a number in the sentence or table it belongs to, and only from real data.
- The same block (heading, lede, three icon cards) in every section, every card the same length.
- Decorative gradients, gradient text, glows, and frosted-glass panels.
- A coloured left border as the only accent on cards and callouts.
- Emoji as icons or bullets.
- Centred text for everything.
- Invented testimonials, customer logos, metrics, and people.

Write button labels as a verb and an object ("Export report") and headings as the thing the section holds.
Before writing headings, empty states, onboarding, or marketing text, read [references/ui-copy-tells.md](references/ui-copy-tells.md).

## Build

In the project, build with its components and tokens. Add a token before hard-coding a new value.

For a mockup:
- Use the requested location and format. Otherwise save it in the repo, or in the OS temporary directory when repository instructions prohibit it.
- Prefer standalone HTML, CSS, and JavaScript. A single file is sufficient for one feature.
  For several screens, share assets and add a gallery or navigation when it helps review.
  Add a device switcher only when comparing viewport sizes helps the task.
- Keep required assets with the deliverable and avoid dependencies on temporary servers or application source paths.
  Use the requested framework when the user chooses one, and package an openable result when requested.
- Make the interactions under review usable with local state, and keep unrelated behavior as labeled placeholders.
- Use synthetic fixtures and distinguish proposed behavior from observed behavior.
  Do not change a live account or database to prepare a mockup without authorization.
- For app screenshots or demonstrations, use the current UI and representative fixtures.
  When generated media will be maintained, retain the source and capture steps needed to reproduce it.
- For a kept multi-page set, record screen coverage, intentional behavior changes, placeholder data, and known implementation dependencies. Mark unverified API support as unknown.
  Scale these notes to the artifact instead of requiring a separate document for a quick sketch.

## Check the result

Render and inspect the result before presenting it, with the commands in [references/render-check.md](references/render-check.md).
- Render at the user's reported viewport, 1280 and 390 wide, and 320 for overflow. Add widths at breakpoint boundaries where controls wrap or the layout changes.
- Run the accessibility and overflow audit at 1280 and 390, and fix every violation it reports in the change.
- Check vertical overflow against the requested scrolling behavior, and look for clipped controls, missing assets, and console errors.
- Walk the page with Tab and confirm the focus ring shows on each control.
- Inspect ordering, spacing, legibility, and the states under review in the screenshots, and read them against the design standard and the generated-UI patterns.
- Play animations through their transitions and inspect their final state.

Fix what the check finds and render again.
After three fix rounds, stop and report what remains open, with the reason for each deviation you keep.
Report any check that could not run.

## Review and revise

Deliver a clickable path to the artifact and show it through the host's supported HTML renderer when available.
In T3 Code, use `html_preview` followed by `html_render` to show HTML.
Keep an annotatable local file when requested, even if a hosted preview also exists.
Use browser automation when the user asks for browser inspection or annotation.
Do not start an HTTP server solely to present static HTML when the host can render it directly.

Apply all feedback from the current message and recheck affected screens, states, and viewport sizes.
Preserve approved choices across revisions.
When subjective copy remains unresolved, offer a small set of distinct alternatives together.
Refresh the displayed artifact after edits and identify which copy contains the revision.
Continue from a mockup to application implementation when the user requests it.
