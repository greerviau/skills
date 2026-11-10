---
name: mockup
description: Use when the user asks for UI mockups, visual explorations of a feature, or screen redesigns before implementation, from a quick sketch to a multi-page set. Excludes experiments whose purpose is to test technical feasibility.
---

# mockup

Build a reviewable UI mockup at the scale the request needs.
Keep application source, dependencies, and configuration unchanged until implementation is requested.
The request determines whether the output is temporary or kept and whether version control or publication is wanted.
Do not create issues as part of this workflow.
Use the requested location and format.
Otherwise, save the mockup in the repo, or in the OS temporary directory when repository instructions prohibit it.

## Ground the design

Read the affected screens, relevant product rules, and existing visual assets.
Preserve the existing logo, fonts, terminology, and product facts unless the request changes them.
For an existing product, inspect representative populated screens and relevant empty or error states when access is available.
Use synthetic fixtures for mockup data and distinguish proposed behavior from observed behavior.
Do not change a live account or database to prepare a mockup without authorization.
Resolve an ambiguity that changes a product rule before depending on it, and continue independent layout work.

Translate the user's visual constraints into observable checks.
Record layout relationships separately for desktop and mobile when they differ.

## Build the review artifact

Prefer standalone HTML, CSS, and JavaScript for browser mockups.
A single file is sufficient for one feature.
For several screens, share assets and add a gallery or navigation when it helps review.
Add a device switcher only when comparing viewport sizes helps the task.
Keep required assets with the deliverable and avoid dependencies on temporary servers or application source paths.
Use the requested framework when the user chooses one, and package an openable result when requested.

Make the interactions under review usable with local state.
Include the states needed to assess the design, for example a populated list, pagination, an open dialog, or a processing animation.
Keep unrelated behavior as labeled placeholders.
For app screenshots or demonstrations, use the current UI and representative fixtures.
When generated media will be maintained, retain the source and capture steps needed to reproduce it.

For a kept multi-page set, record screen coverage, intentional behavior changes, placeholder data, and known implementation dependencies.
Mark unverified API support as unknown.
Scale these notes to the artifact instead of requiring a separate document for a quick sketch.

## Check the result

Render and inspect the artifact before presenting it.
Use the user's reported viewport and representative sizes for the target devices.
Add intermediate widths and breakpoint boundaries when controls wrap or layout changes there.
Check for unintended horizontal overflow, clipped controls, missing assets, and console errors.
Check vertical overflow against the requested scrolling behavior.
Inspect ordering, spacing, legibility, and the states under review in rendered output.
Play animations through their transitions and inspect their final state.
Automated geometry checks supplement visual inspection.
Report any rendering or interaction checks that could not run.

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
Continue to application implementation when the user requests it.
