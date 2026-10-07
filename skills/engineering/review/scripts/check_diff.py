#!/usr/bin/env python3
"""Run review's mechanical checks over the lines a change adds.

Usage: check_diff.py <base>

Compares the working tree (committed, uncommitted, and untracked files) with
the merge base of <base> and HEAD, from the repository root whatever the
current directory. Prints one finding per line as `path:line: check: detail`
or `commit <sha>: check: detail`, and names files of unchecked types on
stderr. Exits 0 with no findings, 1 with findings, and 2 when it cannot run.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath

HASH = ("#",)
SLASH = ("//",)
DASH = ("--",)
COMMENT_MARKERS = {
    **dict.fromkeys(
        [
            ".py",
            ".pyi",
            ".sh",
            ".bash",
            ".zsh",
            ".rb",
            ".pl",
            ".r",
            ".yaml",
            ".yml",
            ".toml",
            ".cfg",
        ]
        + [".ini", ".tf"],
        HASH,
    ),
    **dict.fromkeys(
        [
            ".js",
            ".jsx",
            ".mjs",
            ".cjs",
            ".ts",
            ".tsx",
            ".mts",
            ".cts",
            ".go",
            ".rs",
            ".java",
            ".kt",
        ]
        + [
            ".kts",
            ".swift",
            ".c",
            ".h",
            ".cc",
            ".cpp",
            ".hpp",
            ".cs",
            ".scala",
            ".dart",
        ]
        + [".gradle", ".vue", ".svelte"],
        SLASH,
    ),
    **dict.fromkeys([".sql", ".lua", ".hs"], DASH),
    ".php": ("//", "#"),
}
COMMENT_MARKERS_BY_NAME = {"Dockerfile": HASH, "Makefile": HASH}
PYTHON_SUFFIXES = {".py", ".pyi"}
PROSE_SUFFIXES = {".md", ".markdown", ".rst", ".txt", ".adoc"}

TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__|spec)/"
    r"|(^|/)test_[^/]*\.py$|_test\.(py|go)$|\.(test|spec)\.[cm]?[jt]sx?$",
    re.IGNORECASE,
)
FLAKY_PATTERNS = [
    (
        "real clock",
        re.compile(
            r"\btime\.(sleep|time|monotonic)\(|\bsleep\(|\bdatetime\.(now|utcnow|today)\(|"
            r"\bdate\.today\(|\bDate\.now\(|\bnew Date\(\s*\)|\btime\.Now\(|\bsetTimeout\("
        ),
    ),
    (
        "unseeded randomness",
        re.compile(
            r"\brandom\.(random|randint|randrange|choice|choices|shuffle|uniform|sample)\(|"
            r"\bnp\.random\.|\bMath\.random\(|\brand\.(Int|Float|Intn)|\buuid\.uuid4\("
        ),
    ),
    (
        "network call",
        re.compile(
            r"\brequests\.(get|post|put|patch|delete|head|request)\(|\bhttpx\.|\burlopen\(|"
            r"\burllib\.request\b|\bfetch\(|\baxios\.|\bhttp\.(Get|Post)\("
        ),
    ),
]

ABBREVIATIONS = {
    "cfg", "conf", "idx", "cnt", "msg", "msgs", "btn", "usr", "pwd", "tmp", "arr", "obj",
    "num", "nums", "resp", "req", "ctx", "buf", "ptr", "mgr", "svc", "calc", "samps",
}  # fmt: skip
# Names a framework fixes, which the author cannot rename.
FRAMEWORK_NAMES = {"tmp_path", "tmp_path_factory", "tmpdir", "tmpdir_factory"}
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
STRING_LITERAL = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`")
FILE_PATH = re.compile(r"[\w.~-]*(?:/[\w.-]+)+/?")
KEYWORD_ARGUMENT = re.compile(r"(?<=[(,])\s*[A-Za-z_]\w*\s*=(?!=)")
DEFINITION = re.compile(r"^\s*(async\s+)?(def|function|fn|func)\b")
GO_DECLARATION = re.compile(r"^\s*(func|type|var|const|package)\b")

EXAMPLE_IN_COMMENT = re.compile(r"\be\.g\.|\bfor (example|instance)\b", re.IGNORECASE)
ISSUE_REFERENCE = re.compile(r"(?<![\w&])#[0-9]+\b|/issues/[0-9]+|/pull/[0-9]+")
BANNED_PROSE = re.compile(
    r"\b(begin|commenc(e|es|ed|ing)|initiat(e|es|ed|ing)|utili[sz](e|es|ed|ing|ation)|"
    r"leverag(e|es|ed|ing)|facilitat(e|es|ed|ing)|prior to|subsequent to|regarding|concerning|"
    r"obtain(s|ed|ing)?|acquir(e|es|ed|ing)|demonstrat(e|es|ed|ing)|additionally|"
    r"furthermore|moreover|seamless(ly)?|robust|powerful|effortless(ly)?|cutting-edge|"
    r"world-class|next-generation|revolutionary)\b",
    re.IGNORECASE,
)

AGENT_CO_AUTHOR = re.compile(
    r"^co-authored-by:.*\b(claude|anthropic|copilot|openai|chatgpt|gpt|gemini|cursor|codex|devin)\b|"
    r"^co-authored-by:.*\[bot\]",
    re.IGNORECASE,
)
GENERATED_NOTE = re.compile(r"\bgenerated (with|by)\b", re.IGNORECASE)


class GitError(Exception):
    pass


@dataclass
class SourceLine:
    """One line of a file: `kind` is code, comment, docstring, or string."""

    kind: str
    code: str = ""
    comment: str | None = None


def git(*arguments):
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", *arguments],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise GitError(f"git {' '.join(arguments)}: {result.stderr.strip()}")
    return result.stdout


def added_line_numbers(merge_base):
    """Map each changed path to the line numbers the change adds."""
    added = defaultdict(set)
    diff = git(
        "diff", "--no-color", "--no-ext-diff", "--unified=0",
        "--src-prefix=a/", "--dst-prefix=b/", merge_base,
    )  # fmt: skip
    path = None
    number = 0
    previous = ""
    for line in diff.splitlines():
        if line.startswith("+++ ") and previous.startswith("--- "):
            target = line[len("+++ ") :].rstrip("\t")
            path = None if target == "/dev/null" else target[len("b/") :]
        elif line.startswith("@@"):
            number = int(re.match(r"@@ -\S+ \+(\d+)", line).group(1))
        elif line.startswith("+") and path is not None:
            added[path].add(number)
            number += 1
        previous = line
    for path in filter(
        None, git("ls-files", "--others", "--exclude-standard", "-z").split("\0")
    ):
        added[path] = None
    return added


def read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read().splitlines()
    except OSError:
        return []


def mask_strings(text):
    return STRING_LITERAL.sub(lambda literal: "x" * len(literal.group(0)), text)


def classify(path, lines, markers):
    pure_path = PurePosixPath(path)
    python = pure_path.suffix.lower() in PYTHON_SUFFIXES
    block_comments = "//" in markers
    classified = []
    triple_delimiter = None
    triple_kind = None
    block_kind = None
    for text in lines:
        stripped = text.strip()
        if triple_delimiter:
            classified.append(SourceLine(triple_kind, comment=stripped))
            if triple_delimiter in text:
                triple_delimiter = None
            continue
        if block_kind:
            classified.append(
                SourceLine(block_kind, comment=stripped.lstrip("*").strip())
            )
            if "*/" in text:
                block_kind = None
            continue
        if python and stripped[:3] in ('"""', "'''"):
            delimiter = stripped[:3]
            if delimiter not in stripped[3:]:
                triple_delimiter, triple_kind = delimiter, "docstring"
            classified.append(SourceLine("docstring", comment=stripped.strip("\"' ")))
            continue
        if block_comments and stripped.startswith("/*"):
            kind = "docstring" if stripped.startswith("/**") else "comment"
            if "*/" not in stripped[2:]:
                block_kind = kind
            classified.append(SourceLine(kind, comment=stripped.strip("/* ")))
            continue
        if block_comments and stripped.startswith(("///", "//!")):
            classified.append(SourceLine("docstring", comment=stripped[3:].strip()))
            continue
        marker = next((m for m in markers if stripped.startswith(m)), None)
        if marker and not stripped.startswith("#!"):
            classified.append(
                SourceLine("comment", comment=stripped[len(marker) :].strip())
            )
            continue
        masked = mask_strings(text)
        if python:
            for delimiter in ('"""', "'''"):
                if masked.count(delimiter) % 2 == 1:
                    triple_delimiter, triple_kind = delimiter, "string"
        trailing = None
        for marker in markers:
            trailing = re.search(rf"\s{re.escape(marker)}", masked)
            if trailing:
                break
        if trailing:
            classified.append(
                SourceLine(
                    "code", masked[: trailing.start()], text[trailing.end() :].strip()
                )
            )
        else:
            classified.append(SourceLine("code", masked))
    if pure_path.suffix.lower() == ".go":
        mark_go_doc_comments(lines, classified)
    return classified


def mark_go_doc_comments(lines, classified):
    run_start = None
    for index, line in enumerate(classified):
        if line.kind == "comment":
            run_start = index if run_start is None else run_start
            continue
        if run_start is not None and GO_DECLARATION.match(lines[index]):
            for doc_index in range(run_start, index):
                classified[doc_index].kind = "docstring"
        run_start = None


def abbreviation_in(code):
    if not DEFINITION.match(code):
        code = KEYWORD_ARGUMENT.sub("", code)
    for identifier in IDENTIFIER.findall(FILE_PATH.sub("", code)):
        if identifier in FRAMEWORK_NAMES:
            continue
        if re.match(r"n_[a-z]", identifier):
            return identifier
        for part in CAMEL_BOUNDARY.split(identifier):
            for word in part.split("_"):
                if word.lower() in ABBREVIATIONS:
                    return identifier
    return None


def comment_findings(location, comment, check_examples):
    findings = []
    if check_examples and EXAMPLE_IN_COMMENT.search(comment):
        findings.append(f"{location}: comment-form: example in comment")
    if ISSUE_REFERENCE.search(comment):
        findings.append(f"{location}: issue-reference: {comment}")
    banned = BANNED_PROSE.search(comment)
    if banned:
        findings.append(f"{location}: plain-language: `{banned.group(0)}`")
    return findings


def comment_run_findings(path, classified, added):
    findings = []
    index = 0
    while index < len(classified):
        if classified[index].kind != "comment":
            index += 1
            continue
        end = index
        while end < len(classified) and classified[end].kind == "comment":
            end += 1
        run_numbers = set(range(index + 1, end + 1))
        if end - index >= 3 and run_numbers & added:
            findings.append(
                f"{path}:{index + 3}: comment-form: comment of {end - index} lines"
            )
        index = end
    return findings


def source_findings(path, lines, added, markers):
    classified = classify(path, lines, markers)
    findings = comment_run_findings(path, classified, added)
    test_file = TEST_PATH.search(path)
    for number in sorted(added):
        if number > len(classified):
            continue
        line = classified[number - 1]
        location = f"{path}:{number}"
        if line.kind == "code":
            if test_file:
                for name, pattern in FLAKY_PATTERNS:
                    if pattern.search(line.code):
                        findings.append(
                            f"{location}: flakiness: {name}: {lines[number - 1].strip()}"
                        )
            abbreviation = abbreviation_in(line.code)
            if abbreviation:
                findings.append(
                    f"{location}: naming: abbreviated identifier `{abbreviation}`"
                )
        if line.comment and line.kind != "string":
            findings += comment_findings(
                location, line.comment, line.kind != "docstring"
            )
    return findings


def prose_findings(path, lines, added):
    findings = []
    for number in sorted(added):
        if number <= len(lines):
            banned = BANNED_PROSE.search(lines[number - 1])
            if banned:
                findings.append(f"{path}:{number}: plain-language: `{banned.group(0)}`")
    return findings


def file_findings(added_by_path):
    findings = []
    unchecked = []
    for path, added in sorted(added_by_path.items()):
        lines = read_lines(path)
        if added is None:
            added = set(range(1, len(lines) + 1))
        pure_path = PurePosixPath(path)
        markers = COMMENT_MARKERS.get(
            pure_path.suffix.lower()
        ) or COMMENT_MARKERS_BY_NAME.get(pure_path.name)
        if markers:
            findings += source_findings(path, lines, added, markers)
        elif pure_path.suffix.lower() in PROSE_SUFFIXES:
            findings += prose_findings(path, lines, added)
        elif lines:
            unchecked.append(path)
    return findings, unchecked


def commit_findings(merge_base):
    log = git("log", "--format=%H%x00%B%x1e", f"{merge_base}..HEAD")
    findings = []
    for record in filter(str.strip, log.split("\x1e")):
        sha, _, body = record.strip().partition("\0")
        for text in body.splitlines():
            if AGENT_CO_AUTHOR.search(text.strip()) or GENERATED_NOTE.search(text):
                findings.append(f"commit {sha[:12]}: attribution: {text.strip()}")
    return findings


def main(arguments):
    if len(arguments) != 1:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    try:
        os.chdir(git("rev-parse", "--show-toplevel").strip())
        git("rev-parse", "--verify", "--quiet", f"{arguments[0]}^{{commit}}")
        merge_base = git("merge-base", arguments[0], "HEAD").strip()
        findings, unchecked = file_findings(added_line_numbers(merge_base))
        findings += commit_findings(merge_base)
    except GitError as error:
        print(f"check_diff: {error}", file=sys.stderr)
        return 2
    for path in unchecked:
        print(f"check_diff: not checked (unknown file type): {path}", file=sys.stderr)
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
