from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.matcher import match_candidate
from engine.models import ExtractedSkill, ExtractionMatchType, JobDescription, ParseQuality, ParsedResume
from engine.score_engine import score_candidate


class ScoreEngineTests(unittest.TestCase):
    def test_scores_components_from_matcher_output(self):
        resume = ParsedResume(
            file_path="resume.pdf",
            parse_quality=ParseQuality.CLEAN,
            normalized_cgpa=8.0,
            skills=[
                ExtractedSkill("Python", ExtractionMatchType.EXACT),
                ExtractedSkill("Docker", ExtractionMatchType.EXACT),
            ],
            practical_experience=["Project"],
        )
        jd = JobDescription(
            job_id="jd",
            title="Role",
            slot_count=1,
            required_skills=["Python", "SQL"],
            preferred_skills=["Docker"],
            min_cgpa=9.0,
        )
        candidate = match_candidate(resume, jd)

        score_candidate(candidate, jd)

        breakdown = candidate.score_breakdown
        self.assertIsNotNone(breakdown)
        self.assertEqual(breakdown.required_skill_score, 20.0)
        self.assertEqual(breakdown.preferred_skill_score, 15.0)
        self.assertEqual(breakdown.cgpa_score, 10.0)
        self.assertEqual(breakdown.practical_signal_score, 20)
        self.assertEqual(breakdown.conflict_adjustment, -5.0)

    def test_failed_resume_remains_unscored(self):
        resume = ParsedResume(file_path="resume.pdf", parse_quality=ParseQuality.FAILED)
        jd = JobDescription(job_id="jd", title="Role", slot_count=1)
        candidate = match_candidate(resume, jd)

        score_candidate(candidate, jd)

        self.assertIsNone(candidate.score_breakdown)

    def test_missing_required_penalty_never_makes_total_negative(self):
        resume = ParsedResume(file_path="resume.pdf", parse_quality=ParseQuality.CLEAN)
        jd = JobDescription(
            job_id="jd",
            title="Role",
            slot_count=1,
            required_skills=["Python", "SQL"],
            preferred_skills=["Docker"],
            min_cgpa=8.0,
        )
        candidate = match_candidate(resume, jd)

        score_candidate(candidate, jd)

        self.assertEqual(candidate.total_score, 0.0)


if __name__ == "__main__":
    unittest.main()
