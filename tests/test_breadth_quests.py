import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import breadth_quest


class BreadthQuestTests(unittest.TestCase):
    def test_manifest_and_complete_stage_coverage(self):
        quests = breadth_quest.load_quests()
        self.assertEqual(breadth_quest.validate_quests(quests), [])
        self.assertEqual(len(quests), 12)

    def test_recommendation_has_matching_stage(self):
        quests = breadth_quest.load_quests()
        selected = [q for q in quests if "03" in q["stages"]]
        self.assertTrue(selected)
        self.assertTrue(any(q["id"] == "Q04" for q in selected))

    def test_cli_offline_check(self):
        result = subprocess.run([sys.executable, str(ROOT/"scripts"/"breadth_quest.py"), "check"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("12 quests", result.stdout)

    def test_cli_invalid_stage_fails(self):
        result = subprocess.run([sys.executable, str(ROOT/"scripts"/"breadth_quest.py"),
                                 "recommend", "--stage", "99"],
                                capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
