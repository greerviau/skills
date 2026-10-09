import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "memory_scan.py"
MEMORY = """---
name: build-command
description: The project builds with make
metadata:
  type: project
---

Run `make` to build.
"""


def slug(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


class MemoryScanTestCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.home = self.root / "home"
        self.projects = self.home / ".claude" / "projects"
        self.projects.mkdir(parents=True)

    def add_project(self, project, with_log=True):
        project.mkdir(parents=True, exist_ok=True)
        project_directory = self.projects / slug(project)
        (project_directory / "memory").mkdir(parents=True)
        (project_directory / "memory" / "build-command.md").write_text(MEMORY)
        (project_directory / "memory" / "MEMORY.md").write_text(
            "- [Build command](build-command.md) - make\n"
        )
        if with_log:
            record = {"type": "user", "cwd": str(project), "message": {"content": "hi"}}
            (project_directory / "session.jsonl").write_text(json.dumps(record) + "\n")
        return project_directory

    def scan(self, *arguments):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "HOME": str(self.home)},
        )
        return result.stdout

    def assertResolved(self, output, project):
        self.assertNotIn("resolve to no directory", output, output)
        self.assertIn(f"\n{project}  [1 memories]", output, output)


class ProjectResolutionTests(MemoryScanTestCase):
    def test_project_with_dots_and_underscores_resolves_from_its_session_log(self):
        project = self.root / "code" / "skills" / ".worktrees" / "fix_slug.v2"
        self.add_project(project)

        self.assertResolved(self.scan(), project)

    def test_project_without_a_session_log_resolves_by_walking_the_filesystem(self):
        project = self.root / "code" / ".worktrees" / "fix_slug.v2"
        self.add_project(project, with_log=False)

        self.assertResolved(self.scan(), project)

    def test_hyphenated_directory_name_still_resolves(self):
        project = self.root / "code" / "my-project"
        self.add_project(project, with_log=False)

        self.assertResolved(self.scan(), project)

    def test_slug_differing_only_in_case_resolves_on_a_case_insensitive_filesystem(self):
        actual = self.root / "code" / "github" / "calcine"
        actual.mkdir(parents=True)
        if not (self.root / "code" / "GitHub").exists():
            self.skipTest("filesystem is case-sensitive")
        recorded_as = self.root / "code" / "GitHub" / "calcine"
        self.add_project(recorded_as, with_log=False)

        self.assertResolved(self.scan(), actual)

    def test_log_pointing_at_a_deleted_project_is_reported_unresolved(self):
        project = self.root / "code" / "gone.project"
        self.add_project(project)
        project.rmdir()

        self.assertIn("resolve to no directory", self.scan())

    def test_longest_matching_name_wins_when_a_slug_is_ambiguous(self):
        (self.root / "code" / "a" / "b").mkdir(parents=True)
        project = self.root / "code" / "a-b"
        self.add_project(project, with_log=False)

        self.assertResolved(self.scan(), project)


class WalkCostTests(unittest.TestCase):
    def test_missing_deep_path_lists_each_directory_at_most_twice(self):
        spec = importlib.util.spec_from_file_location("memory_scan", SCRIPT)
        memory_scan = importlib.util.module_from_spec(spec)
        sys.modules["memory_scan"] = memory_scan
        self.addCleanup(sys.modules.pop, "memory_scan", None)
        spec.loader.exec_module(memory_scan)
        with tempfile.TemporaryDirectory() as directory:
            deep = Path(directory).resolve()
            for name in "abcdefghijkl":
                deep = deep / name
            deep.mkdir(parents=True)
            calls = []
            real_iterdir = Path.iterdir

            def counting_iterdir(path):
                calls.append(path)
                return real_iterdir(path)

            Path.iterdir = counting_iterdir
            try:
                result = memory_scan.slug_to_path(memory_scan.path_to_slug(str(deep / "gone")))
            finally:
                Path.iterdir = real_iterdir

        self.assertIsNone(result)
        self.assertLessEqual(len(calls), 2 * len(deep.parts), len(calls))


class ProjectFilterTests(MemoryScanTestCase):
    def test_project_flag_accepts_a_path_with_dots(self):
        wanted = self.root / "code" / ".worktrees" / "fix_slug.v2"
        other = self.root / "code" / "other"
        self.add_project(wanted)
        self.add_project(other)

        output = self.scan("--project", str(wanted))

        self.assertIn("1 memories across 1 project(s)", output, output)
        self.assertResolved(output, wanted)


    def test_project_dot_selects_the_current_directory(self):
        wanted = self.root / "code" / "wanted"
        self.add_project(wanted)
        self.add_project(self.root / "code" / "other")

        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--project", "."],
            capture_output=True,
            text=True,
            check=False,
            cwd=wanted,
            env={**os.environ, "HOME": str(self.home)},
        )

        self.assertIn("1 memories across 1 project(s)", result.stdout, result.stdout)
        self.assertResolved(result.stdout, wanted)


if __name__ == "__main__":
    unittest.main()
