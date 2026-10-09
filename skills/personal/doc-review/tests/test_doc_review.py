import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "doc_review.py"
spec = importlib.util.spec_from_file_location("doc_review", SCRIPT)
doc_review = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(doc_review)


class FencedCodeTests(unittest.TestCase):
    def test_fence_is_highlighted_inside_the_anchored_code_element(self):
        rendered = doc_review.render('```python\ndef f():\n    return "x"\n```\n')

        self.assertIn('data-line="1:4"', rendered)
        self.assertIn('class="language-python"', rendered)
        self.assertIn('<span class="tok-k">def</span>', rendered)
        self.assertIn('<span class="tok-s2">&quot;x&quot;</span>', rendered)

    def test_mermaid_fence_stays_plain_text(self):
        rendered = doc_review.render("```mermaid\ngraph TD; A-->B;\n```\n")

        self.assertIn('class="language-mermaid">graph TD; A--&gt;B;\n</code>', rendered)

    def test_unknown_language_falls_back_to_escaped_source(self):
        rendered = doc_review.render("```nosuchlang\nraw <b>text</b>\n```\n")

        self.assertIn("raw &lt;b&gt;text&lt;/b&gt;", rendered)
        self.assertNotIn("tok-", rendered)


class DocumentFormatTests(unittest.TestCase):
    def test_format_detection(self):
        self.assertEqual(doc_review.document_format(Path("draft.HTML")), "html")
        self.assertEqual(doc_review.document_format(Path("report.pdf")), "pdf")
        self.assertEqual(doc_review.document_format(Path("memo.docx")), "docx")
        self.assertEqual(doc_review.document_format(Path("notes.md")), "text")

    def test_html_keeps_source_and_adds_line_anchors(self):
        source = '<h1 class="title">Title</h1>\n<p>Hello <strong>world</strong>.</p>\n'

        rendered = doc_review.annotate_html(source)

        self.assertIn('<h1 class="title" data-line="1:1">', rendered)
        self.assertIn('<p data-line="2:2">', rendered)
        self.assertIn("<strong>world</strong>", rendered)

    def test_binary_documents_are_served_without_text_decoding(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "sample.pdf"
            output = Path(directory) / "comments.json"
            document.write_bytes(b"%PDF-test")

            session = doc_review.Session(document, output)

            self.assertEqual(session.format, "pdf")
            self.assertEqual(session.source, b"%PDF-test")
            state = json.loads(session.page.split('<script id="state" type="application/json">', 1)[1].split("</script>", 1)[0])
            self.assertEqual(state["format"], "pdf")
            self.assertIsNone(state["lines"])


class DefaultOutputTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.original_tempdir = tempfile.tempdir
        tempfile.tempdir = self.temporary.name
        self.addCleanup(setattr, tempfile, "tempdir", self.original_tempdir)
        self.documents = Path(self.temporary.name) / "documents"
        (self.documents / "a").mkdir(parents=True)
        (self.documents / "b").mkdir(parents=True)

    def test_same_document_gets_the_same_path(self):
        document = self.documents / "a" / "spec.md"

        self.assertEqual(doc_review.default_output(document), doc_review.default_output(document))

    def test_same_named_documents_get_different_paths(self):
        first = doc_review.default_output(self.documents / "a" / "spec.md")
        second = doc_review.default_output(self.documents / "b" / "spec.md")

        self.assertNotEqual(first, second)

    def test_output_directory_is_private_to_the_user(self):
        directory = doc_review.default_output(self.documents / "a" / "spec.md").parent

        self.assertEqual(directory.stat().st_uid, os.getuid())
        self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)

    def test_loose_permissions_on_the_output_directory_are_tightened(self):
        directory = Path(self.temporary.name) / f"doc-review-{os.getuid()}"
        directory.mkdir(mode=0o777)
        directory.chmod(0o777)

        doc_review.default_output(self.documents / "a" / "spec.md")

        self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)

    def test_symlinked_output_directory_is_refused(self):
        target = Path(self.temporary.name) / "elsewhere"
        target.mkdir()
        (Path(self.temporary.name) / f"doc-review-{os.getuid()}").symlink_to(target)

        with self.assertRaises(OSError):
            doc_review.default_output(self.documents / "a" / "spec.md")


class ReviewOutputTests(unittest.TestCase):
    def start_review(self, document, *arguments):
        process = subprocess.Popen(
            [sys.executable, str(SCRIPT), str(document), "--no-open", "--port", "0", *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(process.kill)
        lines = [process.stdout.readline(), process.stdout.readline()]
        announcement = "".join(lines)
        self.assertIn("the comments land in ", announcement, announcement)
        url = re.search(r"Open (\S+) to comment", announcement).group(1)
        output = Path(announcement.split("the comments land in ")[1].strip())
        return process, url, output

    def submit(self, url, comments):
        request = urllib.request.Request(
            url + "api/submit",
            data=json.dumps({"comments": comments}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            self.assertEqual(response.status, 200)

    def test_finished_review_writes_to_the_temporary_directory_and_not_beside_the_document(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "spec.md"
            document.write_text("# Spec\n")
            process, url, output = self.start_review(document)

            self.submit(url, [{"body": "Tighten this."}])

            self.assertEqual(process.wait(timeout=30), 0)
            self.assertEqual(json.loads(output.read_text())["status"], "submitted")
            self.assertEqual(output.parent, doc_review.default_output(document.resolve()).parent.resolve())
            self.assertEqual(sorted(path.name for path in Path(directory).iterdir()), ["spec.md"])

    def test_out_flag_still_chooses_the_path(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "spec.md"
            document.write_text("# Spec\n")
            chosen = Path(directory) / "comments.json"
            process, url, output = self.start_review(document, "--out", str(chosen))

            self.submit(url, [{"body": "Tighten this."}])

            self.assertEqual(process.wait(timeout=30), 0)
            self.assertEqual(output, chosen.resolve())
            self.assertTrue(chosen.exists())


class RendererTests(unittest.TestCase):
    def test_renders_without_linkify_installed(self):
        real_find_spec = importlib.util.find_spec

        def without_linkify(name, *arguments):
            return None if name == "linkify_it" else real_find_spec(name, *arguments)

        import markdown_it.main

        importlib.util.find_spec = without_linkify
        self.addCleanup(setattr, importlib.util, "find_spec", real_find_spec)
        real_linkify = markdown_it.main.linkify_it
        markdown_it.main.linkify_it = None
        self.addCleanup(setattr, markdown_it.main, "linkify_it", real_linkify)

        rendered = doc_review.make_md().render("| a |\n|---|\n| b |\n\nsee https://example.com\n")

        self.assertIn("<table>", rendered)


if __name__ == "__main__":
    unittest.main()
