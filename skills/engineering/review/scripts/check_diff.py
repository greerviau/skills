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

import io
import os
import re
import subprocess
import sys
import tokenize
from collections import defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath

HASH = ("#",)
SLASH = ("//",)
DASH = ("--",)
COMMENT_MARKERS = {
    **dict.fromkeys(
        [".py", ".pyi", ".sh", ".bash", ".zsh", ".rb", ".pl", ".r", ".yaml", ".yml", ".toml",
         ".cfg", ".ini", ".tf"],
        HASH,
    ),
    **dict.fromkeys(
        [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".go", ".rs", ".java",
         ".kt", ".kts", ".swift", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".scala", ".dart",
         ".gradle", ".vue", ".svelte"],
        SLASH,
    ),
    **dict.fromkeys([".sql", ".lua", ".hs"], DASH),
    ".php": ("//", "#"),
}  # fmt: skip
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
FILE_PATH = re.compile(r"(?<![\w)\]])(?:~|\.{1,2})?/[\w.-]+(?:/[\w.-]+)*/?")
GO_DECLARATION = re.compile(r"^(func|type|var|const|package)\b")

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
    """One line of a file: `kind` is code, comment, docstring, or string. String contents in `code` are masked."""

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


def unquote_path(quoted):
    """Undo git's C-style quoting of a path: `"b/q\\"t.py"` becomes `b/q"t.py`."""
    escapes = {"n": b"\n", "t": b"\t", '"': b'"', "\\": b"\\"}
    raw = bytearray()
    body = quoted[1:-1]
    index = 0
    while index < len(body):
        if body[index] == "\\" and re.match(r"[0-7]{3}", body[index + 1 : index + 4]):
            raw.append(int(body[index + 1 : index + 4], 8))
            index += 4
        elif body[index] == "\\" and index + 1 < len(body):
            raw += escapes.get(body[index + 1], body[index + 1].encode())
            index += 2
        else:
            raw += body[index].encode()
            index += 1
    return raw.decode("utf-8", errors="replace")


def diff_path(target):
    target = target.rstrip("\t")
    if target.startswith('"'):
        target = unquote_path(target)
    return None if target == "/dev/null" else target[len("b/") :]


def added_line_numbers(merge_base):
    """Map each changed path to the line numbers the change adds.

    A new untracked file maps to None. Files git diffs as binary are returned separately.
    """
    added = defaultdict(set)
    binary = []
    diff = git(
        "diff", "--no-color", "--no-ext-diff", "--no-textconv", "--unified=0",
        "--src-prefix=a/", "--dst-prefix=b/", merge_base,
    )  # fmt: skip
    path = None
    number = 0
    in_header = False
    for line in diff.split("\n"):
        if line.startswith("diff --git "):
            in_header = True
        elif in_header and line.startswith("+++ "):
            path = diff_path(line[len("+++ ") :])
        elif in_header and line.startswith("Binary files "):
            target = diff_path(
                re.match(r"Binary files .* and (.*) differ$", line).group(1)
            )
            if target:
                binary.append(target)
        elif line.startswith("@@"):
            in_header = False
            number = int(re.match(r"@@ -\S+ \+(\d+)", line).group(1))
        elif not in_header and line.startswith("+") and path is not None:
            added[path].add(number)
            number += 1
    untracked = git("ls-files", "--others", "--exclude-standard", "-z")
    for path in filter(None, untracked.split("\0")):
        added[path] = None
    return added, binary


def read_lines(path):
    """Split on newlines only, as git counts lines. Returns None for an unreadable file."""
    try:
        with open(path, encoding="utf-8", errors="replace", newline="") as handle:
            text = handle.read()
    except OSError:
        return None
    lines = [line.rstrip("\r") for line in text.split("\n")]
    return lines[:-1] if lines and lines[-1] == "" else lines


def classify(path, lines, markers):
    pure_path = PurePosixPath(path)
    if pure_path.suffix.lower() in PYTHON_SUFFIXES:
        try:
            return lex_python(lines)
        except Exception:  # noqa: BLE001, S110 - tokenize raises many types on malformed input
            pass
    classified = lex_generic(lines, markers, pure_path.suffix.lower())
    if pure_path.suffix.lower() == ".go":
        mark_go_doc_comments(lines, classified)
    return classified


def lex_python(lines):
    """Classify Python lines with tokenize, masking strings and keyword-argument names."""
    code = [list(line) for line in lines]
    comments = [None] * len(lines)
    kinds = ["code"] * len(lines)
    tokens = list(
        tokenize.generate_tokens(io.StringIO("\n".join(lines) + "\n").readline)
    )
    fstring_start = getattr(tokenize, "FSTRING_START", None)
    fstring_end = getattr(tokenize, "FSTRING_END", None)
    trivia = {tokenize.NL, tokenize.COMMENT}
    statement_starts = {
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENCODING,
    }

    def significant_index(index, step):
        index += step
        while 0 <= index < len(tokens) and tokens[index].type in trivia:
            index += step
        return index if 0 <= index < len(tokens) else None

    def significant(index, step):
        found = significant_index(index, step)
        return None if found is None else tokens[found]

    def logical_line_head(index):
        while index > 0 and tokens[index - 1].type not in statement_starts:
            index -= 1
        while tokens[index].type in trivia:
            index += 1
        return tokens[index]

    def opens_body(token_index):
        """A `:` ending a def or class header, which a one-line docstring may follow."""
        token = tokens[token_index]
        head = logical_line_head(token_index)
        return token.string == ":" and head.string in ("def", "class", "async")

    def apply_string(first, last, start_index, end_index):
        before_index = significant_index(start_index, -1)
        after = significant(end_index, 1)
        statement = (
            before_index is None
            or tokens[before_index].type in statement_starts
            or opens_body(before_index)
        )
        docstring = statement and (
            after is None or after.type in (tokenize.NEWLINE, tokenize.ENDMARKER)
        )
        (start_row, start_column), (end_row, end_column) = first.start, last.end
        for row in range(start_row, end_row + 1):
            if row > len(lines):
                break
            line_index = row - 1
            if docstring:
                low = start_column if row == start_row else 0
                high = end_column if row == end_row else len(lines[line_index])
                prose = lines[line_index][low:high].strip()
                if row == start_row:
                    prose = re.sub(r"^[rRbBuUfF]{0,2}(\"\"\"|\'\'\'|\"|\')", "", prose)
                if row == end_row:
                    prose = re.sub(r"(\"\"\"|\'\'\'|\"|\')$", "", prose)
                comments[line_index] = prose.strip()
                del code[line_index][low:high]
                if not "".join(code[line_index]).strip():
                    kinds[line_index] = "docstring"
                    code[line_index] = []
                continue
            if start_row < row < end_row:
                kinds[line_index] = "string"
                code[line_index] = []
                continue
            low = start_column if row == start_row else 0
            high = end_column if row == end_row else len(code[line_index])
            for column in range(low, min(high, len(code[line_index]))):
                code[line_index][column] = "x"

    brackets = []
    fstring_stack = []
    definition_depth = None
    lambda_depth = None
    for index, token in enumerate(tokens):
        if fstring_start is not None and token.type == fstring_start:
            fstring_stack.append(index)
            continue
        if fstring_stack:
            if token.type == fstring_end:
                start_index = fstring_stack.pop()
                if not fstring_stack:
                    apply_string(tokens[start_index], token, start_index, index)
            continue
        if token.type == tokenize.STRING:
            apply_string(token, token, index, index)
        elif token.type == tokenize.COMMENT:
            row, column = token.start
            if row == 1 and token.string.startswith("#!"):
                code[0] = []
                continue
            comments[row - 1] = token.string.lstrip("#").strip()
            del code[row - 1][column:]
            if not "".join(code[row - 1]).strip():
                kinds[row - 1] = "comment"
        elif token.type == tokenize.NAME and token.string == "def":
            definition_depth = len(brackets)
        elif token.type == tokenize.NAME and token.string == "lambda":
            lambda_depth = len(brackets)
        elif (
            token.type == tokenize.OP
            and token.string == ":"
            and lambda_depth == len(brackets)
        ):
            lambda_depth = None
        elif token.type == tokenize.OP and token.string in "([{":
            definition = token.string == "(" and definition_depth == len(brackets)
            if definition:
                definition_depth = None
            brackets.append((token.string, definition))
        elif token.type == tokenize.OP and token.string in ")]}" and brackets:
            brackets.pop()
        elif (
            token.type == tokenize.NAME
            and brackets
            and brackets[-1] == ("(", False)
            and lambda_depth is None
        ):
            after = significant(index, 1)
            if after is not None and after.string == "=":
                row, column = token.start
                for offset in range(column, token.end[1]):
                    code[row - 1][offset] = " "
    return [
        SourceLine(kind, "".join(characters), comment)
        for kind, characters, comment in zip(kinds, code, comments)
    ]


def string_end(text, start, quote, escapes):
    """Index just past the quote closing the string opened at `start`, or None if the line ends first."""
    index = start + 1
    while index < len(text):
        if escapes and text[index] == "\\":
            index += 2
            continue
        if text[index] == quote:
            return index + 1
        index += 1
    return None


def regex_end(text, start):
    """Index just past a JavaScript regex literal opened at `start`, or None if `/` is division."""
    before = text[:start].rstrip()
    if before and before[-1] not in "(,=:[!&|?{};":
        return None
    index = start + 1
    in_class = False
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if character == "[":
            in_class = True
        elif character == "]":
            in_class = False
        elif character == "/" and not in_class:
            return index + 1
        index += 1
    return None


def lex_generic(lines, markers, suffix):
    """Classify lines of a C-like, hash-comment, or dash-comment language."""
    block_comments = "//" in markers
    quotes = "\"'`" if block_comments else "\"'"
    # Go raw strings and single quotes in shell, SQL, YAML, and TOML take no escapes.
    backtick_escapes = suffix != ".go"
    single_quote_escapes = block_comments
    javascript = suffix in {
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".ts",
        ".tsx",
        ".mts",
        ".cts",
    }
    classified = []
    block_kind = None
    open_backtick = False
    for row, text in enumerate(lines):
        code = []
        parts = []
        kind = None
        all_string = open_backtick
        index = 0
        if row == 0 and text.startswith("#!"):
            classified.append(SourceLine("code"))
            continue
        while index < len(text):
            if block_kind:
                kind = kind or block_kind
                close = text.find("*/", index)
                stop = len(text) if close == -1 else close
                parts.append(text[index:stop].strip().lstrip("*").strip())
                index = stop if close == -1 else close + 2
                if close != -1:
                    block_kind = None
                continue
            if open_backtick:
                close = string_end(text, index - 1, "`", backtick_escapes)
                stop = len(text) if close is None else close
                code.append("x" * (stop - index))
                index = stop
                if close is not None:
                    open_backtick = False
                continue
            character = text[index]
            all_string = False
            if block_comments and text.startswith("/*", index):
                block_kind = (
                    "docstring"
                    if text.startswith("/**", index)
                    and not text.startswith("/**/", index)
                    else "comment"
                )
                index += 3 if block_kind == "docstring" else 2
                continue
            marker = next((m for m in markers if text.startswith(m, index)), None)
            if marker == "#" and index > 0 and not text[index - 1].isspace():
                marker = None
            if marker:
                rest = text[index + len(marker) :]
                doc = marker == "//" and rest[:1] in ("/", "!")
                parts.append(rest[1:].strip() if doc else rest.strip())
                kind = kind or ("docstring" if doc else "comment")
                break
            if javascript and character == "/":
                close = regex_end(text, index)
                if close is not None:
                    code.append("x" * (close - index))
                    index = close
                    continue
            if character in quotes:
                if character == "`":
                    open_backtick = True
                    code.append("x")
                    index += 1
                    continue
                escapes = character == '"' or single_quote_escapes
                close = string_end(text, index, character, escapes)
                stop = len(text) if close is None else close
                code.append("x" * (stop - index))
                index = stop
                continue
            code.append(character)
            index += 1
        if block_kind and not text:
            kind = block_kind
        code_text = "".join(code)
        comment = " ".join(part for part in parts if part).strip()
        if all_string and text:
            classified.append(SourceLine("string"))
        elif code_text.strip() or kind is None:
            classified.append(SourceLine("code", code_text, comment or None))
        else:
            classified.append(SourceLine(kind, "", comment))
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
    """Report a run of comment lines holding three or more lines of prose."""
    findings = []
    index = 0
    while index < len(classified):
        if classified[index].kind != "comment":
            index += 1
            continue
        end = index
        while end < len(classified) and classified[end].kind == "comment":
            end += 1
        prose_rows = [row for row in range(index, end) if classified[row].comment]
        if len(prose_rows) >= 3 and set(range(index + 1, end + 1)) & added:
            findings.append(
                f"{path}:{prose_rows[2] + 1}: comment-form: comment of {len(prose_rows)} lines"
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


def file_findings(added_by_path, binary):
    findings = []
    unchecked = list(binary)
    for path, added in sorted(added_by_path.items()):
        lines = read_lines(path)
        if lines is None:
            unchecked.append(path)
            continue
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
        git("rev-parse", "--verify", f"{arguments[0]}^{{commit}}")
        merge_base = git("merge-base", arguments[0], "HEAD").strip()
        findings, unchecked = file_findings(*added_line_numbers(merge_base))
        findings += commit_findings(merge_base)
    except GitError as error:
        print(f"check_diff: {error}", file=sys.stderr)
        return 2
    for path in unchecked:
        print(
            f"check_diff: not checked (unknown type or unreadable): {path}",
            file=sys.stderr,
        )
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
