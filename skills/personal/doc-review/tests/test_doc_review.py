import importlib.util
import json
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()


class OutputLocationTests(unittest.TestCase):
    def run_review(self, document, *arguments):
        import subprocess
        import sys

        return subprocess.run(
            [sys.executable, str(SCRIPT), str(document), "--no-open", "--timeout", "1", *arguments],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_default_output_goes_to_the_temporary_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "spec.md"
            document.write_text("# Spec\n")

            result = self.run_review(document)

            announced = Path(result.stdout.split("the comments land in ")[1].strip())
            self.assertEqual(announced.parent, Path(tempfile.gettempdir()).resolve())
            self.assertEqual(sorted(path.name for path in Path(directory).iterdir()), ["spec.md"])

    def test_out_flag_still_chooses_the_path(self):
        with tempfile.TemporaryDirectory() as directory:
            document = Path(directory) / "spec.md"
            document.write_text("# Spec\n")
            chosen = Path(directory) / "comments.json"

            result = self.run_review(document, "--out", str(chosen))

            self.assertIn(f"the comments land in {chosen.resolve()}", result.stdout)
