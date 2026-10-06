# Architecture review report

Write the report as one HTML file in the OS temporary directory.
Do not add the report or its working diagrams to the repository.

## Scaffold

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Architecture review - REPOSITORY</title>
  <style>
    :root { color-scheme: light dark; }
    body { max-width: 1100px; margin: 0 auto; padding: 3rem 1.5rem; font: 16px/1.5 system-ui, sans-serif; }
    article, .top { border: 1px solid #8885; border-radius: 12px; padding: 1.25rem; margin: 2rem 0; }
    .candidates { display: grid; gap: 1.5rem; }
    .diagrams { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
    .diagram { border: 1px solid #8885; border-radius: 8px; padding: 1rem; min-height: 180px; }
    .badge { border-radius: 999px; padding: .2rem .6rem; font-size: .8rem; }
    .strong { background: #166534; color: white; }
    .worth { background: #a16207; color: white; }
    .speculative { background: #475569; color: white; }
    code, .files { font-family: ui-monospace, monospace; }
    @media (max-width: 700px) { .diagrams { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <h1>Architecture review - REPOSITORY</h1>
    <p>DATE - solid box: module · dashed line: seam · red arrow: accidental leak · dark box: deep module</p>
  </header>
  <main class="candidates">
    <!-- Candidate articles go here. -->
  </main>
  <section class="top">
    <h2>Top recommendation</h2>
    <!-- One candidate and its evidence. -->
  </section>
</body>
</html>
```

The report must stay readable if scripts or external assets fail.
Use a CDN Mermaid script only when a graph improves the comparison. Inline SVG or styled HTML boxes avoid the dependency for simple diagrams.

## Candidate card

Each candidate is one `article` containing:

- a short title naming the deepening;
- a recommendation badge: `Strong`, `Worth exploring`, or `Speculative`;
- the exact files and symbols involved;
- a side-by-side before/after visualization;
- one-sentence problem and direction statements;
- short gains stated in terms of module depth, information hiding, seam placement, error-condition elimination, or navigability;
- an ADR warning when the candidate conflicts with a recorded decision.

Use one visual pattern per candidate:

- Call graph: the current chain, and the proposed deep module hiding its internal calls.
- Cross-section: several shallow modules before, one deeper owner after.
- Mass diagram: a wide interface over a small implementation before, a narrow interface over a larger hidden implementation after.
- Seam diagram: accidental leaks crossing the seam before, the hidden implementation after.

Base the visualization on the cited files and symbols.
Do not draw a speculative interface as if it were settled.

## Style

Use plain English and the repository's glossary.
Use `module`, `interface`, `implementation`, `depth`, `seam`, `information hiding`, `error-condition elimination`, and `navigability` instead of vague claims like "cleaner" or "more maintainable".
Keep each gains list to six short bullets or fewer.
Use red only for accidental leaks and amber only for ADR warnings.
