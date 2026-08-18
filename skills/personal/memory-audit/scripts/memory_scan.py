# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scan agent memory directories: print the roster, then the mechanical defects.

Read-only except for --backup, which snapshots every scanned directory first.
Findings are candidates for a human to judge, not verdicts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

PROJECTS_ROOT = Path.home() / ".claude" / "projects"
BACKUP_ROOT = Path.home() / ".claude" / "memory-audit-backups"
VALID_TYPES = {"user", "feedback", "project", "reference"}
# Tuned against a 66-memory corpus: 0.42 keeps every pair a human would want to look at
# and drops the tail of coincidental word overlap. Lowering it floods the report.
SIMILAR_THRESHOLD = 0.42

RELATIVE_DATES = re.compile(
    r"\b(yesterday|today|tomorrow|last (?:week|month|night|year)|next (?:week|month|year)"
    r"|this (?:week|morning|afternoon)|recently|just now|a (?:few )?(?:days?|weeks?) ago)\b",
    re.IGNORECASE,
)
WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
INDEX_LINK = re.compile(r"\]\(([^)]+\.md)\)")
BACKTICKED = re.compile(r"`([^`\n]+)`")
PATHISH = re.compile(r"^[\w@./-]+/[\w@./-]+$")
WORD = re.compile(r"[a-z][a-z0-9_.-]{1,}")
NAME_WORD = re.compile(r"[a-z]{3,}")

STOPWORDS = {
    "the", "and", "for", "not", "but", "are", "was", "its", "use", "via", "one", "two", "all",
    "any", "own", "per", "yet", "get", "got", "may", "can", "you", "how", "why", "who", "out",
    "off", "new", "old", "way", "let", "run", "see", "set", "add", "keep", "make",
    "this", "that", "with", "from", "when", "then", "than", "them", "they", "have", "having",
    "into", "onto", "over", "under", "before", "after", "which", "while", "would", "should",
    "could", "there", "their", "these", "those", "what", "your", "yours", "does", "done",
    "each", "also", "must", "never", "always", "only", "even", "same", "such", "very", "more",
    "most", "less", "some", "instead", "rather", "apply", "user", "greer", "stated", "means",
}


def stem(word: str) -> str:
    for suffix in ("ing", "ped", "ned", "ed", "es", "s"):
        if len(word) - len(suffix) >= 4 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def tokens(text: str) -> set[str]:
    return {stem(w) for w in WORD.findall(text.lower()) if w not in STOPWORDS and len(w) > 1}


def name_tokens(text: str) -> set[str]:
    return {stem(w) for w in NAME_WORD.findall(text.lower()) if w not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def containment(a: set[str], b: set[str]) -> float:
    """Fraction of a that b covers."""
    return len(a & b) / len(a) if a else 0.0


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1].strip()
    return value


def slug_to_path(slug: str) -> Path | None:
    """Resolve a project slug to a directory, disambiguating dashes by what exists on disk."""
    parts = [p for p in slug.split("-") if p]

    def walk(base: Path, rest: list[str]) -> Path | None:
        if not rest:
            return base
        for take in range(len(rest), 0, -1):
            candidate = base / "-".join(rest[:take])
            if candidate.is_dir():
                hit = walk(candidate, rest[take:])
                if hit is not None:
                    return hit
        return None

    return walk(Path("/"), parts)


@dataclass
class Memory:
    path: Path
    slug: str
    project: Path | None
    name: str = ""
    description: str = ""
    mtype: str = ""
    body: str = ""
    raw: str = ""
    age_days: int = 0
    body_lines: int = 0
    defects: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.slug}/{self.path.name}"

    @property
    def subject(self) -> set[str]:
        return tokens(self.description) | name_tokens(self.path.stem)


def parse_memory(path: Path, slug: str, project: Path | None) -> Memory:
    raw = path.read_text(encoding="utf-8", errors="replace")
    mem = Memory(path=path, slug=slug, project=project, raw=raw)
    recorded = None

    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end == -1:
            mem.defects.append("unterminated-frontmatter")
            front, mem.body = raw[3:], ""
        else:
            front, mem.body = raw[3:end], raw[end + 4 :]
        for line in front.splitlines():
            stripped = line.strip()
            if line.startswith("name:"):
                mem.name = unquote(line.split(":", 1)[1])
            elif line.startswith("description:"):
                mem.description = unquote(line.split(":", 1)[1])
            elif stripped.startswith("type:"):
                mem.mtype = unquote(stripped.split(":", 1)[1])
            elif stripped.startswith("modified:"):
                try:
                    recorded = datetime.fromisoformat(
                        unquote(stripped.split(":", 1)[1]).replace("Z", "+00:00")
                    )
                except ValueError:
                    recorded = None
    else:
        mem.body = raw
        mem.defects.append("no-frontmatter")

    if recorded:
        mem.age_days = int((datetime.now(timezone.utc) - recorded).total_seconds() / 86400)
    else:
        mem.age_days = int((time.time() - path.stat().st_mtime) / 86400)
    mem.body_lines = len([l for l in mem.body.splitlines() if l.strip()])

    if not mem.name:
        mem.defects.append("missing-name")
    elif mem.name != path.stem:
        mem.defects.append(f"name-filename-mismatch (name: {mem.name})")
    if not mem.description:
        mem.defects.append("missing-description")
    elif len(mem.description) < 25:
        mem.defects.append("thin-description")
    if not mem.mtype:
        mem.defects.append("missing-type")
    elif mem.mtype not in VALID_TYPES:
        mem.defects.append(f"invalid-type ({mem.mtype})")
    if mem.mtype in {"feedback", "project"} and "**Why:**" not in mem.body:
        mem.defects.append("missing-why")
    if mem.mtype == "feedback" and "**How to apply:**" not in mem.body:
        mem.defects.append("missing-how-to-apply")
    if not mem.body.strip():
        mem.defects.append("empty-body")
    if mem.body_lines > 25:
        mem.defects.append(f"long-body ({mem.body_lines} lines)")
    for hit in RELATIVE_DATES.findall(mem.raw):
        mem.defects.append(f'relative-date ("{hit}")')

    return mem


def check_references(mem: Memory, names: set[str], roots: list[Path]) -> None:
    for target in WIKILINK.findall(mem.raw):
        if target.strip() not in names:
            mem.defects.append(f"dangling-link ([[{target.strip()}]])")
    for token in BACKTICKED.findall(mem.raw):
        token = token.strip()
        if not PATHISH.match(token) or token.endswith("/") or "..." in token:
            continue
        token = token.split(":", 1)[0]
        if any((root / token).exists() for root in roots):
            continue
        if Path(token).expanduser().exists():
            continue
        mem.defects.append(f"path-unverified (`{token}`)")


def scan_dir(memory_dir: Path) -> tuple[list[Memory], list[str], Path | None]:
    slug = memory_dir.parent.name
    project = slug_to_path(slug)
    files = sorted(p for p in memory_dir.glob("*.md") if p.name != "MEMORY.md")
    memories = [parse_memory(p, slug, project) for p in files]
    names = {m.path.stem for m in memories}
    roots = [project, project.parent if project else None, Path.home()]
    roots = [r for r in roots if r is not None]
    for mem in memories:
        check_references(mem, names, roots)

    notes: list[str] = []
    index = memory_dir / "MEMORY.md"
    if not index.exists():
        if memories:
            notes.append(f"MEMORY.md missing while {len(memories)} memories exist")
    else:
        text = index.read_text(encoding="utf-8", errors="replace")
        listed = {Path(t).stem for t in INDEX_LINK.findall(text)}
        notes += [f"not listed in MEMORY.md: {stem}.md" for stem in sorted(names - listed)]
        notes += [
            f"MEMORY.md points at a missing file: {stem}.md" for stem in sorted(listed - names)
        ]
        prose = [
            l for l in text.splitlines()
            if l.strip() and not l.startswith(("#", "-", "*", " "))
        ]
        if prose:
            notes.append(f"MEMORY.md holds {len(prose)} non-pointer line(s) of content")
    return memories, notes, project


def claude_md_overlap(memories: list[Memory]) -> list[str]:
    """Flag memories whose claim a CLAUDE.md already states, making the memory dead weight."""
    cache: dict[Path, list[tuple[str, set[str]]]] = {}
    findings = []
    for mem in memories:
        subject = tokens(mem.description)
        if len(subject) < 4:
            continue
        candidates = [Path.home() / ".claude" / "CLAUDE.md"]
        if mem.project:
            candidates += [mem.project / "CLAUDE.md", mem.project.parent / "CLAUDE.md"]
        for md in candidates:
            if md not in cache:
                cache[md] = (
                    [
                        (l.strip(), tokens(l))
                        for l in md.read_text(encoding="utf-8", errors="replace").splitlines()
                        if len(l.strip()) > 30
                    ]
                    if md.exists()
                    else []
                )
            hit = next(
                (l for l, lt in cache[md] if containment(subject, lt) >= 0.5), None
            )
            if hit:
                findings.append(f"{mem.key}\n      already in {md}: {hit[:120]}")
                break
    return findings


def duplicate_pairs(memories: list[Memory]) -> tuple[list[str], list[str]]:
    digest = {m.key: hashlib.sha256(m.body.strip().encode()).hexdigest() for m in memories}
    groups: dict[str, list[Memory]] = {}
    for mem in memories:
        groups.setdefault(digest[mem.key], []).append(mem)
    identical = [
        " == ".join(m.key for m in group) for group in groups.values() if len(group) > 1
    ]

    similar = []
    profiles = [(m, m.subject, tokens(m.body)) for m in memories]
    for i, (a, sa, ba) in enumerate(profiles):
        for b, sb, bb in profiles[i + 1 :]:
            if digest[a.key] == digest[b.key]:
                continue
            scores = [jaccard(name_tokens(a.path.stem), name_tokens(b.path.stem))]
            if len(sa) >= 5 and len(sb) >= 5:
                scores += [containment(sa, sb), containment(sb, sa)]
            if len(ba) >= 30 and len(bb) >= 30:
                scores += [containment(ba, bb), containment(bb, ba)]
            score = max(scores)
            if score >= SIMILAR_THRESHOLD:
                scope = "same project" if a.slug == b.slug else "across projects"
                similar.append(f"{score:.2f} {scope}: {a.key} ~ {b.key}")
    similar.sort(reverse=True)
    return identical, similar


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", action="append", default=[],
                    help="limit to project paths or slug substrings; repeatable")
    ap.add_argument("--json", default=None, help="write full detail to this path")
    ap.add_argument("--backup", action="store_true",
                    help="snapshot every scanned memory directory before reporting")
    args = ap.parse_args()

    dirs = sorted(p for p in PROJECTS_ROOT.glob("*/memory") if p.is_dir())
    if args.project:
        wanted = [w.strip("/").replace("/", "-").lower() for w in args.project]
        dirs = [d for d in dirs if any(w in d.parent.name.lower() for w in wanted)]
    dirs = [d for d in dirs if any(d.glob("*.md"))]
    if not dirs:
        print("no memory directories with content found")
        return 1

    backup_path = None
    if args.backup:
        backup_path = BACKUP_ROOT / time.strftime("%Y%m%d-%H%M%S")
        for d in dirs:
            shutil.copytree(d, backup_path / d.parent.name, dirs_exist_ok=True)

    memories: list[Memory] = []
    index_defects: dict[str, list[str]] = {}
    unresolved: list[str] = []
    for d in dirs:
        found, notes, project = scan_dir(d)
        memories += found
        if notes:
            index_defects[d.parent.name] = notes
        if project is None:
            unresolved.append(d.parent.name)

    identical, similar = duplicate_pairs(memories)
    overlap = claude_md_overlap(memories)

    print(f"memory-audit scan: {len(memories)} memories across {len(dirs)} project(s)")
    if backup_path:
        print(f"backup: {backup_path}")
    if unresolved:
        print(f"slugs that resolve to no directory (project may be gone): {', '.join(unresolved)}")

    print("\n== ROSTER (type | days since written | name — description)")
    for d in dirs:
        slug = d.parent.name
        group = sorted((m for m in memories if m.slug == slug), key=lambda m: m.path.name)
        label = group[0].project if group and group[0].project else slug
        print(f"\n{label}  [{len(group)} memories]  slug: {slug}")
        for m in group:
            print(f"  {m.mtype or '?':<9} {m.age_days:>4}d  {m.path.stem} — {m.description}")

    print("\n== INDEX DEFECTS")
    for slug, notes in index_defects.items():
        print(f"  {slug}")
        for note in notes:
            print(f"    {note}")
    if not index_defects:
        print("  none")

    print("\n== FILE DEFECTS")
    for m in memories:
        if m.defects:
            print(f"  {m.key}: {'; '.join(sorted(set(m.defects)))}")
    if not any(m.defects for m in memories):
        print("  none")

    print("\n== OVERLAPPING PAIRS (duplicate, or contradicting each other)")
    for line in identical:
        print(f"  identical: {line}")
    for line in similar:
        print(f"  similar {line}")
    if not identical and not similar:
        print("  none")

    print("\n== ALREADY STATED IN A CLAUDE.md THE SESSION LOADS ANYWAY")
    for line in overlap:
        print(f"  {line}")
    if not overlap:
        print("  none")

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {
                    "backup": str(backup_path) if backup_path else None,
                    "memories": [
                        {
                            "path": str(m.path), "slug": m.slug,
                            "project": str(m.project) if m.project else None,
                            "name": m.name, "description": m.description, "type": m.mtype,
                            "age_days": m.age_days, "body_lines": m.body_lines,
                            "defects": sorted(set(m.defects)),
                        }
                        for m in memories
                    ],
                    "index_defects": index_defects,
                    "overlapping": {"identical": identical, "similar": similar},
                    "claude_md_overlap": overlap,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\nfull detail: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
