# Render and look

A visual that has not been rendered is unchecked.
Render it, look at the image, and fix what the checklist finds.

## Checklist

- The file renders with no error, and script-set text appears in the rendered DOM.
- Every label is readable. No text overlaps or runs off the edge.
- The layout holds at 1280px and 390px wide.
- The claim is visible in the initial state.
- Changing the control changes the output.

## HTML

Set `CHROME` to the browser binary: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` on macOS, `google-chrome` or `chromium` on Linux.
When a browser automation tool is available, use it instead to load the page, move the control, and read console errors.

Screenshot at desktop width, then open the PNG:

```bash
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=1280,900 --screenshot=out.png "file://$PWD/page.html"
```

Confirm the script ran by printing the DOM and finding text the script sets:

```bash
"$CHROME" --headless=new --disable-gpu --dump-dom "file://$PWD/page.html" | grep -o 'id="caption">[^<]*'
```

Headless Chrome enforces a minimum window width, so `--window-size=390,...` clips the page instead of showing a phone layout.
Check phone width by loading the page in a 390px iframe and screenshotting the wrapper:

```bash
echo '<body style="margin:0"><iframe src="file://'"$PWD"'/page.html" style="width:390px;height:700px;border:0"></iframe></body>' > frame.html
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=800,720 --screenshot=phone.png "file://$PWD/frame.html"
```

A screenshot cannot move a control.
To test it, set a different `value` on the control in a scratch copy, dump the DOM, and confirm the output text changed.

## Plots

Use matplotlib through `uv`, with the `Agg` backend so no window opens:

```bash
uv run --with matplotlib python plot.py
```

In the script, call `fig.savefig("plot.png", dpi=200, bbox_inches="tight")` and set `figsize=(8, 4.5)`.
Label both axes with units, then open the PNG.

## Mermaid

Render with the local CLI and open the PNG:

```bash
npx -y -p @mermaid-js/mermaid-cli mmdc -i d.mmd -o d.png -b white -s 2
```

The first run downloads Chromium.
Do not use hosted renderers, which publish the diagram content to a third party.
