import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


module_path = Path(__file__).parent.parent / "scripts" / "render_star_map.py"
module_spec = importlib.util.spec_from_file_location("render_star_map", module_path)
assert module_spec is not None and module_spec.loader is not None
render_star_map = importlib.util.module_from_spec(module_spec)
sys.modules[module_spec.name] = render_star_map
module_spec.loader.exec_module(render_star_map)


class RenderStarMapTests(unittest.TestCase):
    def test_focus_keeps_parent_and_direct_blocker(self):
        nodes = [
            self.node("acme/repo#1"),
            self.node("acme/repo#2"),
            self.node("acme/repo#3"),
            self.node("acme/repo#4"),
        ]
        edges = [
            {"source": "acme/repo#1", "target": "acme/repo#2", "type": "parent"},
            {"source": "acme/repo#3", "target": "acme/repo#2", "type": "blocks"},
            {"source": "acme/repo#2", "target": "acme/repo#4", "type": "parent"},
        ]

        filtered_nodes, filtered_edges = render_star_map.filter_nodes(
            nodes, edges, ["acme/repo#2"]
        )

        self.assertEqual(
            {node.reference.identifier for node in filtered_nodes},
            {"acme/repo#1", "acme/repo#2", "acme/repo#3", "acme/repo#4"},
        )
        self.assertEqual(len(filtered_edges), 3)

    def test_render_escapes_script_closing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "map.html"
            render_star_map.render(
                {"nodes": [{"title": "</script>"}], "edges": []}, destination
            )
            html = destination.read_text(encoding="utf-8")

        self.assertNotIn("</script>\"", html)
        self.assertIn("\\u003c/script>", html)

    @staticmethod
    def node(identifier):
        repository, number = identifier.split("#")
        return render_star_map.IssueNode(
            reference=render_star_map.IssueReference(repository, int(number)),
            title=identifier,
            body="",
            state="open",
            url="https://github.com/" + repository + "/issues/" + number,
        )


if __name__ == "__main__":
    unittest.main()
