# Render check

When a browser automation tool is available, use it to load the page, resize the viewport, take screenshots, walk Tab, and read console errors.
Run the audit by passing the contents of `scripts/audit.js` (in this skill's folder) to its evaluate call, which returns the JSON result.
Use this route for pages served by a dev server.

## Headless browser

Without browser automation, use `chrome-headless-shell`, which renders at any window width.
Full Chrome in `--headless=new` mode will not shrink the viewport below 500px.

```bash
BROWSER=$(npx -y @puppeteer/browsers install chrome-headless-shell@stable --path "${TMPDIR:-/tmp}/ui-design-browsers" 2>/dev/null | tail -1 | cut -d' ' -f2-)
```

The first run downloads the browser and later runs print the cached path.

Screenshot each width, then open the PNG:

```bash
"$BROWSER" --hide-scrollbars --window-size=1280,900 --screenshot="$PWD/shot-1280.png" "file://$PWD/page.html"
"$BROWSER" --hide-scrollbars --window-size=390,844 --screenshot="$PWD/shot-390.png" "file://$PWD/page.html"
```

A screenshot shows the first screen only.
For a long page, take one at a larger window height, for example `--window-size=1280,3000`.

## Audit

Run the audit on a scratch copy of the page, never on the deliverable.
The copy must sit next to the original so its relative asset paths resolve.

```bash
cp page.html .audit-page.html
echo "<script src=\"file://$SKILL_DIR/scripts/audit.js\"></script>" >> .audit-page.html
for w in 1280 390; do
  "$BROWSER" --window-size=$w,900 --virtual-time-budget=15000 --dump-dom "file://$PWD/.audit-page.html" 2>/dev/null \
    | sed -n 's/.*<pre id="audit">\(.*\)<\/pre>.*/\1/p'
done
rm .audit-page.html
```

Set `SKILL_DIR` to this skill's folder.
Each line of output is one width's JSON result:

- `pageScrollsSideways`: the page scrolls horizontally at this width.
- `overflow`: elements that extend past the right edge of the viewport, excluding those inside a container that scrolls or clips horizontally.
- `violations`: axe-core results for WCAG 2.2 A and AA and axe best practices, including `color-contrast`, `target-size`, `heading-order`, `button-name`, `label`, and `image-alt`.

An empty line means the audit did not finish within the time budget, or axe-core did not load from jsdelivr.
`{"error": ...}` names the failure.

## What the audit leaves to you

- Contrast over images and gradients, which axe reports as needing review instead of as a violation.
- Focus visibility: walk Tab with browser automation, or screenshot after focusing each control in a scratch copy.
- Overlapping text and controls, and content hidden under fixed headers or bars. Read them in the screenshots.
- Motion: check final states and `prefers-reduced-motion`.
