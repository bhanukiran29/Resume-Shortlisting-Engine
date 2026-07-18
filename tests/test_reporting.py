from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.models import (
    ConfidenceTier,
    JDMatchType,
    MatchedSkill,
    ParseQuality,
    ParsedResume,
    ScoreBreakdown,
    ScoredCandidate,
)
from engine.reporting import candidate_report, report_to_json


class ReportingTests(unittest.TestCase):
    def test_candidate_report_is_presentation_only_dict(self):
        resume = ParsedResume(
            file_path="C:/tmp/resume.pdf",
            parse_quality=ParseQuality.CLEAN,
            name="Asha Rao",
            raw_cgpa="8.7",
            normalized_cgpa=8.7,
        )
        candidate = ScoredCandidate(
            resume=resume,
            job_id="jd",
            score_breakdown=ScoreBreakdown(required_skill_score=40),
            confidence=ConfidenceTier.HIGH,
            matched_required=[MatchedSkill("Python", JDMatchType.EXACT, True)],
        )

        report = candidate_report(candidate)

        self.assertEqual(report["file_name"], "resume.pdf")
        self.assertEqual(report["overall_score"], 40.0)
        self.assertEqual(report["confidence"], "High")
        self.assertEqual(report["matched_required"][0]["name"], "Python")
        self.assertIn('"overall_score": 40.0', report_to_json(candidate))


if __name__ == "__main__":
    unittest.main()
