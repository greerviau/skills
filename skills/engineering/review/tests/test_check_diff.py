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

    def test_keyword_argument_at_call_site_is_not_reported(self):
        self.repository.write("app.py", "loader = DataLoader(dataset, num_workers=4)\n")
        self.repository.commit("add loader")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "naming")

    def test_abbreviated_parameter_in_own_definition_is_reported(self):
        self.repository.write(
            "app.py", "def load(path, num_items=3):\n    return path\n"
        )
        self.repository.commit("add load")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "naming")

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


class GitFailureTests(CheckDiffTestCase):
    def test_unrelated_base_exits_two_instead_of_passing(self):
        git(self.repository.path, "checkout", "-q", "--orphan", "unrelated")
        git(self.repository.path, "rm", "-rfq", ".")
        self.repository.write("other.txt", "other\n")
        self.repository.commit("unrelated root")
        git(self.repository.path, "branch", "-f", "base")
        git(self.repository.path, "checkout", "-q", "main")
        self.repository.write("app.py", "cfg = 1\n")
        self.repository.commit("add cfg")

        exit_code, _ = self.repository.check()

        self.assertEqual(exit_code, 2)

    def test_invalid_utf8_line_is_checked_without_crashing(self):
        (self.repository.path / "app.py").write_bytes(b"cfg = 1  # caf\xe9\n")
        self.repository.commit("add latin-1 file")

        exit_code, findings = self.repository.check()

        self.assertEqual(exit_code, 1)
        self.assertFinding(findings, "app.py:1", "naming")


class PathTests(CheckDiffTestCase):
    def test_noprefix_diff_configuration_does_not_hide_files(self):
        git(self.repository.path, "config", "diff.noprefix", "true")
        self.repository.write("app.py", "cfg = 1\n")
        self.repository.commit("add cfg")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "naming")

    def test_path_with_space_is_checked(self):
        self.repository.write("my app.py", "cfg = 1\n")
        self.repository.commit("add cfg")

        _, findings = self.repository.check()

        self.assertFinding(findings, "my app.py:1", "naming")

    def test_non_ascii_path_is_checked(self):
        self.repository.write("caf\u00e9.py", "cfg = 1\n")
        self.repository.commit("add cfg")

        _, findings = self.repository.check()

        self.assertFinding(findings, "caf\u00e9.py:1", "naming")

    def test_added_line_starting_with_plus_signs_keeps_its_file(self):
        self.repository.write("notes.md", "one\n++ We leverage it.\n")
        self.repository.commit("add notes")

        _, findings = self.repository.check()

        self.assertFinding(findings, "notes.md:2", "plain-language")

    def test_untracked_file_is_checked(self):
        self.repository.write("draft.md", "A seamless setup.\n")

        _, findings = self.repository.check()

        self.assertFinding(findings, "draft.md:1", "plain-language")

    def test_run_from_subdirectory_checks_the_whole_repository(self):
        self.repository.write("src/app.py", "x = 1\n")
        self.repository.commit("add src")
        self.repository.write("draft.md", "A seamless setup.\n")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "base"],
            cwd=self.repository.path / "src",
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertIn("draft.md:1: plain-language:", result.stdout)

    def test_unchecked_file_type_is_named_on_stderr(self):
        self.repository.write("schema.proto", "message Totals {}\n")
        self.repository.commit("add schema")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "base"],
            cwd=self.repository.path,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertIn("schema.proto", result.stderr)


class DocumentationCommentTests(CheckDiffTestCase):
    def test_go_doc_comment_above_declaration_is_not_comment_form(self):
        self.repository.write(
            "totals.go",
            "package totals\n\n// Sum adds the values.\n// It returns zero for an empty slice.\n"
            "// It never panics.\nfunc Sum(values []int) int { return 0 }\n",
        )
        self.repository.commit("add sum")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "comment-form")

    def test_jsdoc_and_rust_doc_blocks_are_not_comment_form(self):
        self.repository.write(
            "totals.js",
            "/**\n * Adds the values.\n * @param values numbers\n */\nfunction sum(values) {}\n",
        )
        self.repository.write(
            "totals.rs",
            "/// Adds the values.\n/// Returns zero.\n/// Never panics.\nfn sum() {}\n",
        )
        self.repository.commit("add sum")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "comment-form")

    def test_pointer_dereference_is_code(self):
        self.repository.write("buffer.c", "void reset(int *ptr) {\n    *ptr = 0;\n}\n")
        self.repository.commit("add reset")

        _, findings = self.repository.check()

        self.assertFinding(findings, "buffer.c:2", "naming")

    def test_python_docstring_is_prose(self):
        self.repository.write(
            "app.py",
            'def load():\n    """Load the cfg file.\n\n    We utilize a cache.\n    """\n',
        )
        self.repository.commit("add load")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "naming")
        self.assertFinding(findings, "app.py:4", "plain-language")


class CommentRunTests(CheckDiffTestCase):
    def test_line_added_to_existing_two_line_comment_is_reported(self):
        self.repository.write("app.py", "# one\n# two\nx = 1\n")
        self.repository.commit("add constant")
        git(self.repository.path, "branch", "-f", "base")
        self.repository.write("app.py", "# one\n# two\n# three\nx = 1\n")
        self.repository.commit("extend comment")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:3", "comment-form")

    def test_trailing_comment_without_space_is_checked(self):
        self.repository.write("app.py", "x = 1 #see #12\n")
        self.repository.write("app.js", "run(); //we leverage it\n")
        self.repository.commit("add code")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "issue-reference")
        self.assertFinding(findings, "app.js:1", "plain-language")


class LanguageCoverageTests(CheckDiffTestCase):
    def test_typescript_module_test_file_is_checked_for_flakiness(self):
        self.repository.write("tests/a.test.mts", "await sleep(1);\n")
        self.repository.commit("add test")

        _, findings = self.repository.check()

        self.assertFinding(findings, "tests/a.test.mts:1", "flakiness")

    def test_capitalized_tests_directory_is_a_test_path(self):
        self.repository.write("Tests/WorkerTests.swift", "sleep(1)\n")
        self.repository.commit("add test")

        _, findings = self.repository.check()

        self.assertFinding(findings, "Tests/WorkerTests.swift:1", "flakiness")

    def test_sql_dockerfile_and_php_comments_are_checked(self):
        self.repository.write("query.sql", "-- see #12\nSELECT 1;\n")
        self.repository.write("Dockerfile", "# see #13\nFROM scratch\n")
        self.repository.write("index.php", "<?php\n# see #14\n")
        self.repository.commit("add files")

        _, findings = self.repository.check()

        self.assertFinding(findings, "query.sql:1", "issue-reference")
        self.assertFinding(findings, "Dockerfile:1", "issue-reference")
        self.assertFinding(findings, "index.php:2", "issue-reference")

    def test_every_banned_word_in_standards_is_checked(self):
        self.repository.write(
            "README.md", "# Project\n\nBegin here.\n\nNotes concerning setup.\n"
        )
        self.repository.commit("document setup")

        _, findings = self.repository.check()

        self.assertFinding(findings, "README.md:3", "plain-language")
        self.assertFinding(findings, "README.md:5", "plain-language")


class LexingTests(CheckDiffTestCase):
    def test_multi_line_python_string_is_not_code_or_docstring(self):
        self.repository.write(
            "app.py",
            'SQL = """\n# e.g. a select\ncfg = 1\n"""\n\n\ndef run():\n    idx = 1\n    return idx\n',
        )
        self.repository.commit("add query")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "comment-form")
        self.assertFalse(
            [line for line in findings if line.startswith("app.py:3:")], findings
        )
        self.assertFinding(findings, "app.py:8", "naming")

    def test_prefixed_and_dedented_python_strings_are_strings(self):
        self.repository.write(
            "tests/test_render.py",
            'import textwrap\n\nEXPECTED = textwrap.dedent(f"""\n    cfg = {1}\n    """)\nidx = 2\n',
        )
        self.repository.commit("add render test")

        _, findings = self.repository.check()

        self.assertFalse([line for line in findings if ":4:" in line], findings)
        self.assertFinding(findings, "tests/test_render.py:6", "naming")

    def test_comment_without_space_before_hash_is_a_comment(self):
        self.repository.write("app.py", "y = 2# e.g. four\n")
        self.repository.commit("add constant")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "comment-form")

    def test_line_numbers_survive_form_feed(self):
        self.repository.write("app.py", "x = 1\n\x0c\n# e.g. this\n")
        self.repository.commit("add constant")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:3", "comment-form")

    def test_multi_line_template_literal_is_not_code(self):
        self.repository.write("app.js", "const page = `\n// e.g. a heading\n`;\n")
        self.repository.commit("add page")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "comment-form")

    def test_go_comment_inside_function_body_is_a_comment(self):
        self.repository.write(
            "app.go",
            "package app\n\nfunc run() {\n\t// e.g. inner\n\tvar x = 1\n\t_ = x\n}\n",
        )
        self.repository.commit("add run")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.go:4", "comment-form")

    def test_block_comment_delimiters_do_not_count_as_comment_lines(self):
        self.repository.write("app.c", "/*\n * One line of prose.\n */\nint x = 1;\n")
        self.repository.commit("add constant")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "comment-form")


class IdentifierScopeTests(CheckDiffTestCase):
    def test_tuple_assignment_target_is_an_identifier(self):
        self.repository.write("app.py", "a, idx = 1, 2\n")
        self.repository.commit("add constants")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "naming")

    def test_keyword_argument_on_its_own_line_of_a_call_is_not_reported(self):
        self.repository.write(
            "app.py", "loader = DataLoader(\n    dataset,\n    num_workers=4,\n)\n"
        )
        self.repository.commit("add loader")

        _, findings = self.repository.check()

        self.assertNoFinding(findings, "naming")

    def test_division_is_not_a_path(self):
        self.repository.write("app.py", "ratio = total/cnt\n")
        self.repository.commit("add ratio")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "naming")


class DiffHeaderTests(CheckDiffTestCase):
    def test_path_git_quotes_is_checked(self):
        self.repository.write('q"t.py', "cfg = 1\n")
        self.repository.commit("add quoted file")

        _, findings = self.repository.check()

        self.assertFinding(findings, 'q"t.py:1', "naming")

    def test_added_line_that_looks_like_a_header_pair_keeps_its_file(self):
        self.repository.write("a.sql", "-- old\nSELECT 1;\n")
        self.repository.commit("add query")
        git(self.repository.path, "branch", "-f", "base")
        self.repository.write("a.sql", "++ b/zz.sql\nSELECT 1;\n-- e.g. here\n")
        self.repository.commit("edit query")

        _, findings = self.repository.check()

        self.assertFinding(findings, "a.sql:3", "comment-form")

    def test_unknown_base_error_names_the_cause(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "no-such-ref"],
            cwd=self.repository.path,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertRegex(result.stderr, r"no-such-ref.*\S+$")
        self.assertNotRegex(result.stderr.strip(), r":\s*$")


class EscapeTests(CheckDiffTestCase):
    def test_escaped_backslash_closes_template_literal(self):
        self.repository.write(
            "app.js", "const s = `C:\\\\`;\nconst tmp_cnt = 1; // regarding\n"
        )
        self.repository.commit("add path")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.js:2", "naming")
        self.assertFinding(findings, "app.js:2", "plain-language")

    def test_escaped_backslash_closes_double_quoted_string(self):
        self.repository.write(
            "app.js", 'const s = "a\\\\"; const tmp_cnt = 1; // regarding\n'
        )
        self.repository.commit("add string")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.js:1", "naming")
        self.assertFinding(findings, "app.js:1", "plain-language")

    def test_go_raw_string_has_no_escapes(self):
        self.repository.write(
            "app.go", "package app\n\nvar s = `\\`\nvar tmpCnt = 1 // regarding\n"
        )
        self.repository.commit("add raw string")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.go:4", "naming")

    def test_shell_single_quote_has_no_escapes(self):
        self.repository.write("run.sh", "sep='\\'; tmp_cnt=1 # regarding\n")
        self.repository.commit("add separator")

        _, findings = self.repository.check()

        self.assertFinding(findings, "run.sh:1", "plain-language")

    def test_regex_literal_with_backtick_is_not_a_template(self):
        self.repository.write(
            "app.js", "const tick = /`/;\nconst tmp_cnt = 1; // regarding\n"
        )
        self.repository.commit("add regex")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.js:2", "naming")
        self.assertFinding(findings, "app.js:2", "plain-language")


class PythonDocstringEdgeTests(CheckDiffTestCase):
    def test_docstring_prose_keeps_its_first_and_last_letters(self):
        self.repository.write(
            "app.py",
            'def run():\n    """Utilize the buffer."""\n\n\ndef stop():\n    """Regarding stop."""\n',
        )
        self.repository.commit("add functions")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:2", "plain-language")
        self.assertFinding(findings, "app.py:6", "plain-language")

    def test_one_line_definition_docstring_is_prose(self):
        self.repository.write(
            "app.py",
            'def run(): "Utilize the buffer."\n\n\nclass Job: "Regarding jobs."\n',
        )
        self.repository.commit("add definitions")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "plain-language")
        self.assertFinding(findings, "app.py:4", "plain-language")

    def test_tokenize_failure_falls_back_instead_of_crashing(self):
        (self.repository.path / "app.py").write_bytes(
            b"x = 1  # a\r\xc3\xa9\ncfg = 2\n"
        )
        self.repository.commit("add odd file")

        exit_code, findings = self.repository.check()

        self.assertEqual(exit_code, 1)
        self.assertFinding(findings, "app.py:2", "naming")


class PythonKeywordEdgeTests(CheckDiffTestCase):
    def test_lambda_default_inside_call_is_reported(self):
        self.repository.write("app.py", "items.sort(key=lambda tmp_cnt=1: 0)\n")
        self.repository.commit("add sort")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "naming")

    def test_generic_function_parameter_is_reported(self):
        self.repository.write(
            "app.py", "def first[T](tmp_cnt=1):\n    return tmp_cnt\n"
        )
        self.repository.commit("add generic")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:1", "naming")


class GitAttributeTests(CheckDiffTestCase):
    def test_textconv_does_not_shift_line_numbers(self):
        self.repository.write("app.py", "x = 1\n")
        self.repository.commit("add constant")
        git(self.repository.path, "branch", "-f", "base")
        (self.repository.path / ".git" / "info").mkdir(exist_ok=True)
        (self.repository.path / ".git" / "info" / "attributes").write_text(
            "*.py diff=doubled\n"
        )
        git(self.repository.path, "config", "diff.doubled.textconv", "sed p")
        self.repository.write("app.py", "x = 1\ncfg = 2\n")
        self.repository.commit("add cfg")

        _, findings = self.repository.check()

        self.assertFinding(findings, "app.py:2", "naming")

    def test_file_git_treats_as_binary_is_named_on_stderr(self):
        (self.repository.path / ".git" / "info").mkdir(exist_ok=True)
        (self.repository.path / ".git" / "info" / "attributes").write_text(
            "b.py -diff\n"
        )
        self.repository.write("b.py", "msg_cnt = 1\n")
        self.repository.commit("add b")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "base"],
            cwd=self.repository.path,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertIn("b.py", result.stderr)


if __name__ == "__main__":
    unittest.main()
