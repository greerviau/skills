#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown-it-py[linkify]>=3.0", "mdit-py-plugins>=0.4"]
# ///
"""Render a document in the browser for Notion-style commenting, then hand the comments back.

Serves a local review page, blocks until the reviewer clicks "Send to agent" (or
"Finish without comments"), writes the comments to a JSON file, and exits.

Usage:
  uv run doc_review.py <document> [--out PATH] [--port N] [--no-open] [--timeout SECONDS]

A finished review exits 0 whether or not it produced comments; `status` in the JSON says which.
Exit codes: 0 review finished, 3 timed out, 4 aborted.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VIEWER = Path(__file__).resolve().parent / "viewer.html"

EXIT_FINISHED = 0
EXIT_TIMEOUT = 3
EXIT_ABORTED = 4


def make_md():
    """A GitHub-flavored parser, degrading to CommonMark if the extras are unavailable."""
    from markdown_it import MarkdownIt

    try:
        md = MarkdownIt("gfm-like")
    except Exception:
        md = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    for module, plugin in (
        ("mdit_py_plugins.front_matter", "front_matter_plugin"),
        ("mdit_py_plugins.tasklists", "tasklists_plugin"),
    ):
        try:
            mod = __import__(module, fromlist=[plugin])
            md.use(getattr(mod, plugin))
        except Exception:
            pass
    return md


def render(text: str) -> str:
    """Render markdown to HTML, tagging each top-level block with its source line range.

    `data-line="<first>:<last>"` is 1-based and inclusive, so a comment anchored to a
    block reports the exact lines to edit in the source file.
    """
    md = make_md()
    tokens = md.parse(text)
    depth = 0
    for token in tokens:
        if depth == 0 and token.map and token.nesting >= 0:
            token.attrSet("data-line", f"{token.map[0] + 1}:{token.map[1]}")
        depth += token.nesting
    return md.renderer.render(tokens, md.options, {})


class Session:
    """Holds the rendered document and receives the reviewer's verdict."""

    def __init__(self, doc: Path, out: Path):
        self.doc = doc
        self.out = out
        self.done = threading.Event()
        self.result: dict | None = None
        self.lock = threading.Lock()
        self.clients = 0                   # open event streams, one per review page
        self.arrived = False               # a page has connected at least once
        self.left_at: float | None = None  # when the last page disconnected
        text = doc.read_text(encoding="utf-8")
        self.page = (
            VIEWER.read_text(encoding="utf-8")
            .replace("__DOC_HTML__", render(text))
            .replace(
                "__STATE_JSON__",
                json.dumps(
                    {
                        "path": str(doc),
                        "title": doc.name,
                        "mtime": int(doc.stat().st_mtime),
                        "lines": len(text.splitlines()),
                    }
                ),
            )
        )

    def joined(self) -> None:
        with self.lock:
            self.clients += 1
            self.arrived = True
            self.left_at = None

    def parted(self) -> None:
        with self.lock:
            self.clients -= 1
            if self.clients <= 0:
                self.left_at = time.monotonic()

    def watch(self, grace: float) -> None:
        """End the review once every page is gone, so a closed tab does not strand the agent.

        Liveness is a held connection rather than a timer the browser may throttle in a
        background tab. The grace covers a reload, where the stream drops and comes back.
        """
        while not self.done.wait(1):
            with self.lock:
                left = self.left_at if (self.arrived and self.clients <= 0) else None
            if left and time.monotonic() - left > grace:
                self.finish("abandoned", [])

    def finish(self, status: str, comments: list) -> None:
        self.result = {
            "status": status,
            "document": str(self.doc),
            "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "comments": comments,
        }
        self.out.write_text(json.dumps(self.result, indent=2) + "\n", encoding="utf-8")
        self.done.set()


class Handler(BaseHTTPRequestHandler):
    session: Session

    def log_message(self, *args):  # keep the agent's stdout clean
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = self.path.split("?")[0]
        if route in ("/", "/index.html"):
            self._send(200, self.session.page.encode("utf-8"), "text/html; charset=utf-8")
        elif route == "/api/events":
            self._events()
        else:
            self._send(404, b"not found", "text/plain")

    def _events(self):
        """Hold the connection open for as long as the page is there; dropping it ends the review."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        session = self.session
        session.joined()
        try:
            while not session.done.is_set():
                self.wfile.write(b": open\n\n")   # the write is what discovers a departed page
                self.wfile.flush()
                if session.done.wait(3):
                    break
        except OSError:
            pass
        finally:
            session.parted()

    def do_POST(self):
        route = self.path.split("?")[0]
        if route not in ("/api/submit", "/api/cancel"):
            self._send(404, b"not found", "text/plain")
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, b'{"ok":false}', "application/json")
            return
        # A cancel discards the review, so its body never reaches the agent.
        comments = (payload.get("comments") or []) if route == "/api/submit" else []
        status = "submitted" if comments else "no-comments"
        self._send(200, json.dumps({"ok": True}).encode(), "application/json")
        self.session.finish(status, comments)


def free_port(preferred: int) -> int:
    """Hold the default port when it is free: a stable origin keeps a reviewer's saved drafts."""
    for candidate in (preferred, 0):
        try:
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", candidate))
                return sock.getsockname()[1]
        except OSError:
            continue
    raise OSError("no port available")


def summarize(result: dict) -> None:
    comments = result["comments"]
    if result["status"] == "abandoned":
        print("The review tab closed before anything was sent. Any comments drafted are saved in the "
              "browser and come back if the review is served again; ask the reviewer before assuming "
              "they had nothing to say.")
        return
    if not comments:
        print("No comments; the reviewer finished the review without changes.")
        return
    print(f"{len(comments)} comment(s) on {result['document']}:\n")
    for index, comment in enumerate(comments, 1):
        where = f"lines {comment['lines'][0]}-{comment['lines'][1]}" if comment.get("lines") else "whole document"
        print(f"[{index}] {where}" + (f" — under {comment['section']!r}" if comment.get("section") else ""))
        if comment.get("quote"):
            print(f'    quoting: "{comment["quote"]}"')
        print(f"    comment: {comment['body']}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("document", type=Path, help="markdown (or plain text) file to review")
    parser.add_argument("--out", type=Path, help="where to write the comments JSON (default: <document>.review.json)")
    parser.add_argument("--port", type=int, default=8787, help="port to serve on (default: 8787, falling back to any free port)")
    parser.add_argument("--no-open", action="store_true", help="print the URL instead of opening a browser")
    parser.add_argument("--timeout", type=float, default=0, help="give up after N seconds (default: wait forever)")
    parser.add_argument("--grace", type=float, default=20,
                        help="end the review N seconds after the last page disconnects (default: 20)")
    args = parser.parse_args()

    doc = args.document.expanduser().resolve()
    if not doc.is_file():
        print(f"error: no such file: {doc}", file=sys.stderr)
        return EXIT_ABORTED
    out = (args.out or doc.with_suffix(doc.suffix + ".review.json")).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    session = Session(doc, out)
    handler = type("BoundHandler", (Handler,), {"session": session})
    server = ThreadingHTTPServer(("127.0.0.1", free_port(args.port)), handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"

    threading.Thread(target=server.serve_forever, daemon=True).start()
    threading.Thread(target=session.watch, args=(args.grace,), daemon=True).start()
    print(f"Reviewing {doc}\nOpen {url} to comment; the comments land in {out}", flush=True)
    if not args.no_open:
        webbrowser.open(url)

    try:
        finished = session.done.wait(timeout=args.timeout or None)
    except KeyboardInterrupt:
        finished = False
    server.shutdown()

    if not finished:
        print("Review window closed without a verdict.", file=sys.stderr)
        return EXIT_TIMEOUT if args.timeout else EXIT_ABORTED

    time.sleep(0.2)  # let the browser's response flush before the process exits
    summarize(session.result)
    print(f"Written to {out}")
    return EXIT_FINISHED


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    sys.exit(main())
