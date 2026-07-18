from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.confidence_engine import assign_confidence
from engine.models import (
    ConfidenceTier,
    JDMatchType,
    MatchedSkill,
    ParseQuality,
    ParsedResume,
    ScoredCandidate,
)


class ConfidenceEngineTests(unittest.TestCase):
    def test_high_when_clean_complete_and_exact_matches(self):
        resume = ParsedResume(
            file_path="resume.pdf",
            parse_quality=ParseQuality.CLEAN,
            name="Asha Rao",
            email="a@example.com",
            college="College",
            grad_year=2024,
        )
        candidate = ScoredCandidate(
            resume=resume,
            job_id="jd",
            matched_required=[MatchedSkill("Python", JDMatchType.EXACT, True)],
        )

        assign_confidence(candidate)

        self.assertEqual(candidate.confidence, ConfidenceTier.HIGH)

    def test_partial_parse_caps_at_medium(self):
        resume = ParsedResume(
            file_path="resume.pdf",
            parse_quality=ParseQuality.PARTIAL,
            name="Asha Rao",
            email="a@example.com",
            college="College",
            grad_year=2024,
        )
        candidate = ScoredCandidate(
            resume=resume,
            job_id="jd",
            matched_required=[MatchedSkill("Python", JDMatchType.EXACT, True)],
        )

        assign_confidence(candidate)

        self.assertEqual(candidate.confidence, ConfidenceTier.MEDIUM)

    def test_missing_many_fields_or_no_matches_is_low(self):
        resume = ParsedResume(file_path="resume.pdf", parse_quality=ParseQuality.CLEAN)
        candidate = ScoredCandidate(resume=resume, job_id="jd")

        assign_confidence(candidate)

        self.assertEqual(candidate.confidence, ConfidenceTier.LOW)


if __name__ == "__main__":
    unittest.main()
