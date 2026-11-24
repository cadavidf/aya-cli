"""Checks for Aya's workspace inspection tools; no model or network needed."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from aya_tools import WorkspaceTools


class ToolsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir()
        (self.root / "src").mkdir()
        (self.root / "src" / "settings.py").write_text("first\nMAGIC_VALUE = 123\n")
        (self.root / "image.bin").write_bytes(b"\x00secret")
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "ignored.txt").write_text("MAGIC_VALUE")
        self.outside = Path(self.tmp.name) / "secret.txt"
        self.outside.write_text("outside secret")
        (self.root / "escape").symlink_to(self.outside)
        (self.root / "outside_dir").symlink_to(Path(self.tmp.name))
        self.tools = WorkspaceTools(self.root)

    def test_read_and_list(self):
        self.assertIn("src/", self.tools.list_files())
        self.assertIn("2: MAGIC_VALUE = 123", self.tools.read_file("src/settings.py"))

    def test_search_text_and_filenames(self):
        result = self.tools.search_files("magic_value")
        self.assertIn("src/settings.py:2: MAGIC_VALUE = 123", result)
        self.assertNotIn("node_modules", result)
        self.assertIn("src/settings.py [filename]", self.tools.search_files("settings.py"))

    def test_escape_rejected(self):
        for path in ("../secret.txt", str(self.outside), "escape", "outside_dir/secret.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.tools.read_file(path)
        self.assertNotIn("outside secret", self.tools.search_files("outside secret"))

    def test_binary_and_invalid_paths(self):
        for path in ("image.bin", "src", "missing"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.tools.read_file(path)

    def test_bounded_read(self):
        (self.root / "large.txt").write_text("x" * (self.tools.MAX_READ_BYTES + 100))
        self.assertIn("[File truncated]", self.tools.read_file("large.txt"))

    def test_invalid_query(self):
        for query in ("", "a\nb", "x" * 257):
            with self.subTest(query=query), self.assertRaises(ValueError):
                self.tools.search_files(query)


if __name__ == "__main__":
    unittest.main(verbosity=2)
