---
name: doc-review
description: Render Markdown, text, HTML, PDF, or DOCX documents for browser-based inline comments and return the comments with source locations.
disable-model-invocation: true
---

# doc-review

Run `/doc-review` to collect a human's comments on a document in the browser, then revise the document against them.
The review page renders the original document without converting it or writing it back to disk.
Comments are anchored to source locations, which chat feedback is not.

Run it only when the user asks. Handing a document back in chat is the default.

The mechanism is `scripts/doc_review.py`. Do not rebuild any part of it (renderer, comment UI, transport) inline.

## Procedure

### 1. Serve the document

Run the script in the background. It opens the reviewer's browser and blocks until they send their comments back.

```bash
uv run doc_review.py <document>
```

Supported formats are Markdown, plain text, HTML (`.html`, `.htm`), PDF (`.pdf`), and DOCX (`.docx`).
HTML renders directly in the review page.
PDF uses PDF.js and DOCX uses docx-preview, both in the browser, and neither is converted or written to disk.
Both load pinned renderers from jsDelivr, so they need network access when the review page opens.

Run it from the `scripts/` directory next to this file so `viewer.html` resolves.
The only prerequisite is [uv](https://docs.astral.sh/uv/). If it is missing, install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`.

Background the process instead of blocking a foreground call, because the review takes as long as the human takes.
The process exits when they click send, which returns control to you.

Flags:

- `--out PATH`: the comments file (default `<name>-<hash>.review.json` in a private `doc-review-<uid>` directory under the OS temp directory, so the review leaves nothing in the document's repo). The script prints the path.
- `--port N`: default 8787, falling back to any free port. Keep the default unless it is taken, because the reviewer's saved drafts are scoped to the origin and a new port loses them.
- `--no-open`: print the URL instead of opening a browser.
- `--timeout SECONDS`: give up waiting after this long.
- `--grace SECONDS`: default 20. How long after the review page disconnects the review ends as `abandoned`. It covers a reload, where the connection drops and returns.

### 2. Tell the reviewer it is open

In one line: select text to comment, edit or delete comments in the side panel, then "Send to agent" when done.
Then wait. Do not poll the file, start other work on the document, or guess what they will say.

### 3. Read the comments

The script writes JSON (also summarized on stdout):

```json
{"status": "submitted",
 "comments": [{"id": 1, "body": "Tighten this.", "quote": "Intro paragraph with…",
               "lines": [3, 3], "section": "Sample spec"}]}
```

Comments come in the order the reviewer saw them: document order, with whole-document comments first.
`lines` is an inclusive 1-based range into the source file for Markdown, text, and HTML passage comments, and null for whole-document, PDF, and DOCX comments.
PDF anchors carry page numbers and text offsets. DOCX anchors carry rendered paragraph numbers and text offsets.
`quote` is the exact highlighted text, and `section` is the enclosing heading when one exists.

`status` is `submitted`, `no-comments`, or `abandoned`, and all three exit 0.
`no-comments` means the reviewer sent nothing: they had nothing to change, or discarded their drafted comments.
`abandoned` means the page went away without sending. The drafted comments stay in the reviewer's browser and return if the same document is served again, so ask whether they want it reopened and do not treat it as approval.
Exit codes: 0 review finished, 3 timed out, 4 aborted.

### 4. Revise the document

Address every comment, editing at the line range it anchors to.
If a comment asks for something you believe is wrong, do the rest and say which one you pushed back on and why. Do not drop it silently.

### 5. Report back

Give the revised document and one line per comment saying what you changed.
If the user wants another round, re-run the script on the revised document as a fresh review.

## Notes

- The reviewer's in-progress comments survive a page reload, so a closed tab or browser restart mid-review loses nothing.
- ` ```mermaid ` blocks render as diagrams. A comment on one anchors to the fence's line range with the diagram type as its quote. Offline, or when a diagram fails to parse, the source stays visible and commentable as text.
- Line ranges come from the source and stay valid only while the file is unedited since serving. Do not edit a document under review.
- Delete the `.review.json` file after applying the comments, unless the user wants it kept.
