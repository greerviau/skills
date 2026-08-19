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
