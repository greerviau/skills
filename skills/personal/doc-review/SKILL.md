---
name: doc-review
description: Use only when the user explicitly asks to mark up a document in the browser (a spec, plan, draft, report, README, or any markdown or text file). Renders the document, where the user highlights passages and leaves Notion-style comments, then hands every comment back with its source line range and quoted text so the document can be revised against them. Never invoke it on your own after producing a document. Trigger on "/doc-review", "let me mark this up in the browser", "open the doc for inline comments", "send me the draft to comment on".
disable-model-invocation: true
---

# doc-review

Run `/doc-review` explicitly to collect a human's comments on a document in the browser, then revise the document against them.
A reviewer marking up passages in place gives comments anchored to exact lines, which chat feedback does not.

Run it when the user asks for it; handing a document back in chat stays the default.

The mechanism is `scripts/doc_review.py`. Never rebuild any part of it (renderer, comment UI, transport) inline.

## Procedure

**1. Serve the document.**
Run the script in the background; it opens the reviewer's browser and blocks until they send their comments back.

```bash
uv run doc_review.py <document>
```

Run it from the `scripts/` directory next to this file so `viewer.html` resolves.
The only prerequisite is [uv](https://docs.astral.sh/uv/); if it is missing, install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Background it rather than blocking a foreground call, since a review takes as long as the human takes.
The process exits on its own once they click send, which is what returns control to you.

Flags: `--out PATH` for the comments file (default `<document>.review.json`), `--port N` (default 8787, falling back to any free port), `--no-open` to print the URL instead of opening a browser, `--timeout SECONDS` to give up waiting.
Keep the default port unless it is taken; the reviewer's saved drafts are scoped to the origin, so a new port loses them.
`--grace SECONDS` (default 20) is how long after the review page disconnects the review ends as `abandoned`; it covers a reload, where the page's connection drops and comes back.

**2. Tell the reviewer it is open**, in one line: select text to comment, edit or delete comments in the side panel, then "Send to agent" when done.
Then wait. Do not poll the file, do not start other work on the document, and do not guess what they will say.

**3. Read the comments** from the JSON the script writes (also summarized on stdout):

```json
{"status": "submitted",
 "comments": [{"id": 1, "body": "Tighten this.", "quote": "Intro paragraph with…",
               "lines": [3, 3], "section": "Sample spec"}]}
```

Comments arrive in the order the reviewer saw them: document order, with whole-document comments first.
`lines` is an inclusive 1-based range into the source file, `quote` is the exact text they highlighted, and `section` is the enclosing heading.
`lines` is null for a comment on the document as a whole.
`status` is one of `submitted`, `no-comments`, or `abandoned`; all three exit 0.
`no-comments` means the reviewer sent nothing back: they had nothing to change, or they discarded the comments they had drafted.
`abandoned` means the review page went away without sending: the reviewer's drafted comments are still saved in their browser and come back if the same document is served again, so ask whether they want it reopened rather than treating it as approval.
Exit codes: 0 review finished, 3 timed out, 4 aborted.

**4. Revise the document.** Address every comment, editing at the line range each one anchors to.
Where a comment asks for something you believe is wrong, do the rest, and say which one you pushed back on and why — do not silently drop it.

**5. Report back**: the revised document, and one line per comment saying what you changed for it.
If the user wants another round, re-running the script on the revised document is a fresh review.

## Notes

- The reviewer's in-progress comments survive a page reload, so a closed tab or a browser restart mid-review loses nothing.
- ` ```mermaid ` blocks render as diagrams, and a comment on one anchors to the fence's line range with the diagram type as its quote. Offline, or on a diagram that fails to parse, the source stays visible and commentable as ordinary text.
- Line ranges come from the source, so they stay valid as long as you have not edited the file since serving it. Do not edit a document while it is under review.
- Delete the `.review.json` file once you have applied the comments, unless the user wants it kept.
