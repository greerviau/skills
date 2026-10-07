import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_diff.py"


def git(repository, *arguments):
    subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )


class DiffRepository:
    """A throwaway repository with a `base` branch and a working change on top."""

    def __init__(self):
        self._directory = tempfile.TemporaryDirectory()
        self.path = Path(self._directory.name)
        git(self.path, "init", "-q", "-b", "main")
        git(self.path, "config", "user.name", "Test Author")
        git(self.path, "config", "user.email", "author@example.com")
        self.write("README.md", "# Project\n")
        self.commit("initial")
        git(self.path, "branch", "base")

    def write(self, relative_path, content):
        file_path = self.path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def commit(self, message):
        git(self.path, "add", "-A")
        git(self.path, "commit", "-q", "-m", message)

    def check(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "base"],
            cwd=self.path,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout.splitlines()

    def close(self):
        self._directory.cleanup()


class CheckDiffTestCase(unittest.TestCase):
    def setUp(self):
        self.repository = DiffRepository()
        self.addCleanup(self.repository.close)

    def assertFinding(self, findings, location, check):
        matches = [
            line for line in findings if line.startswith(f"{location}: {check}:")
        ]
        self.assertTrue(matches, f"no {check} finding at {location} in {findings}")

    def assertNoFinding(self, findings, check):
        matches = [line for line in findings if f": {check}:" in line]
        self.assertFalse(matches, f"unexpected {check} findings: {matches}")


class CleanDiffTests(CheckDiffTestCase):
    def test_clean_change_exits_zero_with_no_output(self):
        self.repository.write("app.py", "def total(values):\n    return sum(values)\n")
        self.repository.commit("add total")

        exit_code, findings = self.repository.check()

        self.assertEqual(exit_code, 0)
        self.assertEqual(findings, [])

    def test_unknown_base_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "no-such-ref"],
            cwd=self.repository.path,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)


class FlakinessTests(CheckDiffTestCase):
    def test_real_clock_in_test_file_is_reported_at_its_line(self):
        self.repository.write(
            "tests/test_worker.py",
            "import time\n\ndef test_worker():\n    time.sleep(1)\n",
        )
        self.repository.commit("add worker test")

        exit_code, findings = self.repository.check()

        self.assertEqual(exit_code, 1)
        self.assertFinding(findings, "tests/test_worker.py:4", "flakiness")

    def test_unseeded_random_and_network_in_test_file_are_reported(self):
        self.repository.write(
            "tests/test_client.py",
            "import random\nimport requests\n\ndef test_client():\n"
            "    value = random.random()\n    requests.get('https://example.com')\n",
        )
        self.repository.commit("add client test")

        _, findings = self.repository.check()

        self.assertFinding(findings, "tests/test_client.py:5", "flakiness")
        self.assertFinding(findings, "tests/test_client.py:6", "flakiness")

    def test_call_inside_string_literal_is_not_a_flakiness_finding(self):
        self.repository.write(
            "tests/test_fixture.py", 'SOURCE = "import time; time.sleep(1)"\n'
        )
        self.repository.commit("add fixture source")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "flakiness")

    def test_clock_in_production_code_is_not_a_flakiness_finding(self):
        self.repository.write(
            "worker.py", "import time\n\ndef wait():\n    time.sleep(1)\n"
        )
        self.repository.commit("add worker")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "flakiness")


class AttributionTests(CheckDiffTestCase):
    def test_agent_co_author_trailer_is_reported(self):
        self.repository.write("app.py", "def total(values):\n    return sum(values)\n")
        self.repository.commit(
            "add total\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
        )

        exit_code, findings = self.repository.check()

        self.assertEqual(exit_code, 1)
        self.assertTrue(
            any(
                ": attribution:" in line and line.startswith("commit ")
                for line in findings
            ),
            findings,
        )

    def test_generated_by_note_is_reported(self):
        self.repository.write("app.py", "def total(values):\n    return sum(values)\n")
        self.repository.commit("add total\n\nGenerated with Claude Code")

        _, findings = self.repository.check()

        self.assertTrue(any(": attribution:" in line for line in findings), findings)

    def test_human_co_author_is_not_reported(self):
        self.repository.write("app.py", "def total(values):\n    return sum(values)\n")
        self.repository.commit(
            "add total\n\nCo-Authored-By: Ada Lovelace <ada@example.com>"
        )

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "attribution")


class NamingTests(CheckDiffTestCase):
    def test_abbreviated_identifier_is_reported(self):
        self.repository.write(
            "app.py", "def load():\n    cfg = read_settings()\n    return cfg\n"
        )
        self.repository.commit("add load")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:2", "naming")

    def test_abbreviation_inside_snake_and_camel_case_is_reported(self):
        self.repository.write(
            "app.ts",
            "const rowIdx = 0;\nconst n_samps = 3;\n",
        )
        self.repository.commit("add constants")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.ts:1", "naming")
        self.assertFinding(findings, "app.ts:2", "naming")

    def test_full_word_identifier_is_not_reported(self):
        self.repository.write(
            "app.py",
            "def load():\n    configuration = read_settings()\n    return configuration\n",
        )
        self.repository.commit("add load")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "naming")

    def test_path_segments_are_not_identifiers(self):
        self.repository.write(
            "run.sh",
            "#!/usr/bin/env bash\nlog_file=/tmp/run.log\ncp $log_file /usr/local/share/\n",
        )
        self.repository.commit("add run script")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "naming")

    def test_framework_fixture_names_are_not_reported(self):
        self.repository.write(
            "tests/test_export.py",
            "def test_export(tmp_path):\n    assert tmp_path.exists()\n",
        )
        self.repository.commit("add export test")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "naming")

    def test_abbreviation_in_markdown_prose_is_not_a_naming_finding(self):
        self.repository.write("README.md", "# Project\n\nSet the cfg value.\n")
        self.repository.commit("document cfg")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "naming")


class CommentFormTests(CheckDiffTestCase):
    def test_third_consecutive_comment_line_is_reported(self):
        self.repository.write(
            "app.py",
            "# one\n# two\n# three\ndef total(values):\n    return sum(values)\n",
        )
        self.repository.commit("add total")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:3", "comment-form")

    def test_example_in_comment_is_reported(self):
        self.repository.write(
            "app.js", "// accepts a list, e.g. [1, 2]\nfunction total(values) {}\n"
        )
        self.repository.commit("add total")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.js:1", "comment-form")

    def test_two_line_comment_is_not_reported(self):
        self.repository.write(
            "app.py",
            "# The upstream API rounds down.\n# Callers pass whole cents.\nx = 1\n",
        )
        self.repository.commit("add constant")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "comment-form")

    def test_module_docstring_block_is_not_a_comment(self):
        self.repository.write(
            "app.py", '"""Totals.\n\nOne.\nTwo.\nThree.\n"""\nx = 1\n'
        )
        self.repository.commit("add module")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "comment-form")


class IssueReferenceTests(CheckDiffTestCase):
    def test_local_issue_and_pr_references_are_reported(self):
        self.repository.write(
            "app.py", "x = 1  # fix for #123\n# added in PR #88\ny = 2\n"
        )
        self.repository.commit("add constants")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "issue-reference")
        self.assertFinding(findings, "app.py:2", "issue-reference")

    def test_external_tracker_link_is_reported_for_settling(self):
        self.repository.write(
            "app.go",
            "// requests drops the header, see https://github.com/psf/requests/issues/2949\n"
            "package app\n",
        )
        self.repository.commit("add package")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.go:1", "issue-reference")

    def test_comment_marker_inside_string_literal_is_not_a_comment(self):
        self.repository.write("app.py", 'SOURCE = "x = 1  # fix for #123"\n')
        self.repository.commit("add source")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "issue-reference")

    def test_hex_color_and_plain_numbers_are_not_reported(self):
        self.repository.write("app.py", 'color = "#123abc"\nretries = 3  # 3 retries\n')
        self.repository.commit("add constants")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "issue-reference")


class PlainLanguageTests(CheckDiffTestCase):
    def test_banned_word_in_markdown_is_reported(self):
        self.repository.write("README.md", "# Project\n\nWe utilize a cache.\n")
        self.repository.commit("document cache")

        exit_code, findings = self.repository.check()

        self.assertEqual(exit_code, 1)
        self.assertFinding(findings, "README.md:3", "plain-language")

    def test_banned_phrase_in_comment_is_reported(self):
        self.repository.write("app.py", "# Runs prior to the export.\nx = 1\n")
        self.repository.commit("add constant")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "plain-language")

    def test_banned_word_in_code_identifier_is_not_reported(self):
        self.repository.write(
            "app.py", "def leverage_ratio(debt, equity):\n    return debt / equity\n"
        )
        self.repository.commit("add ratio")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "plain-language")


class DiffScopeTests(CheckDiffTestCase):
    def test_uncommitted_change_is_checked(self):
        self.repository.write("README.md", "# Project\n\nA seamless setup.\n")

        _, findings = self.repository.check()

        self.assertFinding(findings, "README.md:3", "plain-language")

    def test_line_numbers_follow_the_new_file(self):
        self.repository.write("notes.md", "one\ntwo\nthree\nfour\n")
        self.repository.commit("add notes")
        git(self.repository.path, "branch", "-f", "base")
        self.repository.write("notes.md", "one\ntwo\nthree\nWe leverage it.\nfour\n")
        self.repository.commit("edit notes")

        _, findings = self.repository.check()

        self.assertFinding(findings, "notes.md:4", "plain-language")

    def test_lines_already_on_the_base_are_not_reported(self):
        self.repository.write("README.md", "# Project\n\nWe utilize a cache.\n")
        self.repository.commit("document cache")
        git(self.repository.path, "branch", "-f", "base")
        self.repository.write("app.py", "x = 1\n")
        self.repository.commit("add constant")

        exit_code, findings = self.repository.check()

        self.assertEqual(exit_code, 0)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
