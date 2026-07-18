from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.matcher import match_candidate
from engine.models import ExtractedSkill, ExtractionMatchType, JobDescription, ParseQuality, ParsedResume


class MatcherTests(unittest.TestCase):
    def test_matches_required_and_preferred_skills_without_scoring(self):
        resume = ParsedResume(
            file_path="resume.pdf",
            parse_quality=ParseQuality.CLEAN,
            skills=[
                ExtractedSkill("Python", ExtractionMatchType.EXACT),
                ExtractedSkill("Docker", ExtractionMatchType.EXACT),
            ],
        )
        jd = JobDescription(
            job_id="jd",
            title="Role",
            slot_count=1,
            required_skills=["python", "SQL"],
            preferred_skills=["Docker"],
        )

        candidate = match_candidate(resume, jd)

        self.assertEqual([skill.name for skill in candidate.matched_required], ["python"])
        self.assertEqual([skill.name for skill in candidate.matched_preferred], ["Docker"])
        self.assertEqual(candidate.missing_required, ["SQL"])
        self.assertIsNone(candidate.score_breakdown)
        self.assertIsNone(candidate.confidence)

    def test_failed_resume_returns_unmatched_shell(self):
        resume = ParsedResume(file_path="resume.pdf", parse_quality=ParseQuality.FAILED)
        jd = JobDescription(job_id="jd", title="Role", slot_count=1, required_skills=["Python"])

        candidate = match_candidate(resume, jd)

        self.assertEqual(candidate.matched_required, [])
        self.assertEqual(candidate.missing_required, [])


if __name__ == "__main__":
    unittest.main()
