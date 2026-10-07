#!/usr/bin/env python3
"""Run review's mechanical checks over the lines a change adds.

Usage: check_diff.py <base>

Compares the working tree (committed, uncommitted, and untracked files) with
the merge base of <base> and HEAD. Prints one finding per line as
`path:line: check: detail` or `commit <sha>: check: detail`. Exits 0 with no
findings, 1 with findings, and 2 when <base> does not resolve.
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath

HASH_COMMENT = ("#",)
SLASH_COMMENT = ("//",)
DASH_COMMENT = ("--",)
COMMENT_MARKERS = {
    **dict.fromkeys(
        [
            ".py",
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
            ".ini",
        ],
        HASH_COMMENT,
    ),
    **dict.fromkeys(
        [
            ".js",
            ".jsx",
            ".mjs",
            ".cjs",
            ".ts",
            ".tsx",
            ".go",
            ".rs",
            ".java",
            ".kt",
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
        ],
        SLASH_COMMENT,
    ),
    **dict.fromkeys([".sql", ".lua", ".hs"], DASH_COMMENT),
    ".php": ("//", "#"),
}
COMMENT_MARKERS_BY_NAME = {"Dockerfile": HASH_COMMENT, "Makefile": HASH_COMMENT}
PROSE_SUFFIXES = {".md", ".markdown", ".rst", ".txt", ".adoc"}

TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__|spec)/"
    r"|(^|/)test_[^/]*\.py$|_test\.(py|go)$|\.(test|spec)\.[cm]?[jt]sx?$"
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
    "cfg",
    "conf",
    "idx",
    "cnt",
    "msg",
    "msgs",
    "btn",
    "usr",
    "pwd",
    "tmp",
    "arr",
    "obj",
    "num",
    "nums",
    "resp",
    "req",
    "ctx",
    "buf",
    "ptr",
    "mgr",
    "svc",
    "calc",
    "samps",
}
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CAMEL_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
STRING_LITERAL = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`")
FILE_PATH = re.compile(r"[\w.~-]*(?:/[\w.-]+)+/?")
# Names a framework fixes, which the author cannot rename.
FRAMEWORK_NAMES = {"tmp_path", "tmp_path_factory", "tmpdir", "tmpdir_factory"}

EXAMPLE_IN_COMMENT = re.compile(r"\be\.g\.|\bfor (example|instance)\b", re.IGNORECASE)
ISSUE_REFERENCE = re.compile(r"(?<![\w&])#[0-9]+\b|/issues/[0-9]+|/pull/[0-9]+")
BANNED_PROSE = re.compile(
    r"\b(utili[sz](e|es|ed|ing|ation)|leverag(e|es|ed|ing)|facilitat(e|es|ed|ing)|"
    r"prior to|subsequent to|commenc(e|es|ed|ing)|initiat(e|es|ed|ing)|regarding|"
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


@dataclass
class AddedLine:
    path: str
    number: int
    text: str


def git(*arguments):
    return subprocess.run(
        ["git", *arguments], capture_output=True, text=True, check=False
    )


def added_lines(merge_base):
    diff = git("diff", "--no-color", "--no-ext-diff", "--unified=0", merge_base).stdout
    path = None
    number = 0
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = None if line == "+++ /dev/null" else line[len("+++ b/") :]
        elif line.startswith("@@"):
            number = int(re.match(r"@@ -\S+ \+(\d+)", line).group(1))
        elif line.startswith("+") and path is not None:
            yield AddedLine(path, number, line[1:])
            number += 1
    untracked = git("ls-files", "--others", "--exclude-standard", "-z").stdout
    for path in filter(None, untracked.split("\0")):
        try:
            with open(path, encoding="utf-8") as handle:
                for number, text in enumerate(handle.read().splitlines(), start=1):
                    yield AddedLine(path, number, text)
        except (UnicodeDecodeError, OSError):
            continue


def comment_markers(path):
    pure_path = PurePosixPath(path)
    return COMMENT_MARKERS.get(pure_path.suffix.lower()) or COMMENT_MARKERS_BY_NAME.get(
        pure_path.name
    )


def split_comment(text, markers):
    """Return (code with string contents masked, comment, whole_line) for one line."""
    stripped = text.strip()
    if markers == SLASH_COMMENT and stripped.startswith(("/*", "*")):
        return "", stripped.lstrip("/*").strip(), True
    for marker in markers:
        if stripped.startswith(marker) and not stripped.startswith("#!"):
            return "", stripped[len(marker) :].strip(), True
    masked = STRING_LITERAL.sub(lambda literal: "x" * len(literal.group(0)), text)
    for marker in markers:
        trailing = re.search(rf"\s{re.escape(marker)}\s", masked)
        if trailing:
            return masked[: trailing.start()], text[trailing.end() :].strip(), False
    return masked, None, False


def abbreviation_in(code):
    code = FILE_PATH.sub("", STRING_LITERAL.sub("", code))
    for identifier in IDENTIFIER.findall(code):
        if identifier in FRAMEWORK_NAMES:
            continue
        if re.match(r"n_[a-z]", identifier):
            return identifier
        for part in CAMEL_BOUNDARY.split(identifier):
            for word in part.split("_"):
                if word.lower() in ABBREVIATIONS:
                    return identifier
    return None


def line_findings(lines):
    findings = []
    comment_run = []
    for line in lines:
        location = f"{line.path}:{line.number}"
        markers = comment_markers(line.path)
        suffix = PurePosixPath(line.path).suffix.lower()

        if markers:
            code, comment, whole_line = split_comment(line.text, markers)
            if (
                whole_line
                and comment_run
                and comment_run[-1].path == line.path
                and comment_run[-1].number == line.number - 1
            ):
                comment_run.append(line)
            else:
                comment_run = [line] if whole_line else []
            if len(comment_run) == 3:
                findings.append(
                    f"{location}: comment-form: third consecutive comment line"
                )
            if TEST_PATH.search(line.path):
                for name, pattern in FLAKY_PATTERNS:
                    if pattern.search(code):
                        findings.append(
                            f"{location}: flakiness: {name}: {line.text.strip()}"
                        )
            abbreviation = abbreviation_in(code)
            if abbreviation:
                findings.append(
                    f"{location}: naming: abbreviated identifier `{abbreviation}`"
                )
            if comment:
                if EXAMPLE_IN_COMMENT.search(comment):
                    findings.append(f"{location}: comment-form: example in comment")
                if ISSUE_REFERENCE.search(comment):
                    findings.append(f"{location}: issue-reference: {comment}")
                banned = BANNED_PROSE.search(comment)
                if banned:
                    findings.append(f"{location}: plain-language: `{banned.group(0)}`")
        elif suffix in PROSE_SUFFIXES:
            banned = BANNED_PROSE.search(line.text)
            if banned:
                findings.append(f"{location}: plain-language: `{banned.group(0)}`")
    return findings


def commit_findings(merge_base):
    log = git("log", "--format=%H%x00%B%x1e", f"{merge_base}..HEAD").stdout
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
    base = arguments[0]
    if git("rev-parse", "--verify", "--quiet", f"{base}^{{commit}}").returncode != 0:
        print(f"check_diff: cannot resolve base `{base}`", file=sys.stderr)
        return 2
    merge_base = git("merge-base", base, "HEAD").stdout.strip()
    findings = line_findings(added_lines(merge_base)) + commit_findings(merge_base)
    for finding in findings:
        print(finding)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
