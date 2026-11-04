import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import roadmap
import system_profile
import validate_repo
import session_plan

class SystemProfileTests(unittest.TestCase):
    def test_low_memory_means_light(self):
        self.assertEqual(system_profile.classify_tier(8, 4, 100), 'light')
    def test_unknown_memory_conservative(self):
        self.assertEqual(system_profile.classify_tier(8, None, 200), 'light')
    def test_medium_available(self):
        self.assertEqual(system_profile.classify_tier(4, 12, 50), 'moderate')
    def test_large_enough_full(self):
        self.assertEqual(system_profile.classify_tier(8, 32, 90), 'full')
    def test_profile_excludes_identifiers(self):
        p=system_profile.get_profile()
        for field in ('hostname','username','ip','serial','home_path','token'):
            self.assertNotIn(field,p)
        self.assertIn(p['resource_tier'], ('light','moderate','full'))

class RoadmapTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state=Path(self.tmp.name)/'progress.json'
        self.original=roadmap.STATE
        roadmap.STATE=self.state
        self.addCleanup(lambda: setattr(roadmap,'STATE',self.original))
        self.modules=roadmap.load_curriculum()
    def test_init_and_prerequisites(self):
        roadmap.init('student')
        data=roadmap.load_state()
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            roadmap.start('01',self.modules,data)
    def test_initial_stage(self):
        roadmap.init('student')
        data=roadmap.load_state()
        roadmap.start('00',self.modules,data)
        self.assertEqual(roadmap.load_state()['in_progress'],'00')
    def test_completion_requires_reflection(self):
        roadmap.init('student')
        with self.assertRaises(ValueError):
            roadmap.complete('00','PR #1','too short','answer to questions',self.modules,roadmap.load_state())
    def test_completed_is_self_reported(self):
        roadmap.init('student')
        data=roadmap.load_state()
        with contextlib.redirect_stdout(io.StringIO()):
            roadmap.complete('00','PR #1','I wrote and tested a solution locally, and reviewed its tradeoffs and limitations.',
                             'I can describe retries and why they create duplicates.',self.modules,data)
        record=roadmap.load_state()['completed']['00']
        self.assertEqual(record['verification'],'self_reported_not_independently_verified')
        self.assertEqual(roadmap.first_next(self.modules,roadmap.load_state())['id'],'01')
    def test_sanitized_summary(self):
        roadmap.init('student')
        root=roadmap.ROOT
        with tempfile.TemporaryDirectory() as temp:
            roadmap.ROOT=Path(temp)
            self.addCleanup(lambda: setattr(roadmap,'ROOT',root))
            (Path(temp)/'learner').mkdir()
            with contextlib.redirect_stdout(io.StringIO()):
                roadmap.export_summary(self.modules,roadmap.load_state())
            public=(Path(temp)/'learner/learning-status.md').read_text()
            self.assertNotIn('student',public)
            self.assertNotIn('token',public.lower())
            self.assertIn('Next suggested stage: 00',public)
    def test_no_overwrite(self):
        roadmap.init('student')
        with self.assertRaisesRegex(ValueError,'refusing overwrite'):
            roadmap.init('student')

class SessionPlanTests(unittest.TestCase):
    def test_default_session(self):
        plan=session_plan.make_plan('builder','beginner',50)
        self.assertIn(plan['stage'], [f'{i:02}' for i in range(14)])
        self.assertEqual(plan['minutes'],plan['micro_lesson_min']+plan['independent_lab_min']+plan['reflection_min'])
        self.assertIn('write',plan['next_action'])

class RepoValidationTests(unittest.TestCase):
    def test_repo_valid(self):
        self.assertEqual(validate_repo.validate(),[])

if __name__=='__main__':
    unittest.main()
