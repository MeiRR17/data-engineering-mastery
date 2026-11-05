"""Guard against regressions in English-first Markdown, Jupyter and VS Code UX."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "check_english_content.py"
spec = importlib.util.spec_from_file_location("check_english_content", SOURCE)
english = importlib.util.module_from_spec(spec)
spec.loader.exec_module(english)


class EnglishContentTests(unittest.TestCase):
    def test_repo_has_english_only_text(self):
        self.assertEqual(english.scan_non_english(ROOT), [])

    def test_visual_editor_and_notebooks(self):
        self.assertEqual(english.validate_visual_setup(ROOT), [])

    def test_guard_detects_hebrew_in_markdown_and_notebook(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "unit.md").write_text("# \u05e9\u05dc\u05d5\u05dd\n", encoding="utf-8")
            (root / "note.ipynb").write_text(
                '{"cells":[{"cell_type":"markdown","source":["\u05d4\u05e1\u05d1\u05e8"]}]}',
                encoding="utf-8",
            )
            errors = english.scan_non_english(root)
            self.assertEqual(len(errors), 2, errors)
            self.assertTrue(any("unit.md:1" in x for x in errors))
            self.assertTrue(any("note.ipynb:1" in x for x in errors))

    def test_english_path_filenames_kept_for_backward_compatibility(self):
        self.assertTrue((ROOT / "docs" / "ROADMAP.he.md").is_file())
        self.assertEqual(english.HEBREW.search(
            (ROOT / "docs" / "ROADMAP.he.md").read_text(encoding="utf-8")
        ), None)


if __name__ == "__main__":
    unittest.main()
