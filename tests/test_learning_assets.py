import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import validate_repo

class EducationalAssetTests(unittest.TestCase):
    def test_learning_asset_validation(self):
        self.assertEqual(validate_repo.validate_learning_assets(ROOT), [])

    def test_all_stages_have_independent_exit_criteria(self):
        import json
        data=json.loads((ROOT/'curriculum/curriculum.json').read_text(encoding='utf8'))
        self.assertEqual(len(data['modules']),14)
        self.assertTrue(all(m.get('exit_criteria') and m.get('deliverable') for m in data['modules']))

    def test_documentation_references_resources(self):
        readme=(ROOT/'README.md').read_text(encoding='utf8')
        for required in ['docs/VIDEO-LEARNING.he.md','docs/MASTERY-MATRIX.he.md','docs/TROUBLESHOOTING.he.md', 'docs/LEARNER-HANDBOOK.he.md','notebooks/00_data_journey.ipynb']:
            self.assertIn(required,readme)

    def test_no_remote_video_in_repository(self):
        self.assertFalse(list(ROOT.rglob('*.mp4')))
        self.assertFalse(list(ROOT.rglob('*.webm')))

if __name__ == '__main__':
    unittest.main()
