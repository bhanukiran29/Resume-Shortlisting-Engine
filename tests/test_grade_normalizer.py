from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.grade_normalizer import normalize_grade, normalize_raw_cgpa
from engine.models import ParsedResume, ParseQuality


class GradeNormalizerTests(unittest.TestCase):
    def test_supported_raw_formats_normalize_to_ten_point_scale(self):
        cases = {
            "8.7": 8.7,
            "8.7/10": 8.7,
            "CGPA: 9.1": 9.1,
            "9.1 CGPA": 9.1,
            "87%": 8.7,
            "85.5%": 8.55,
            "3.6/4": 9.0,
            "3.75 / 4.0": 9.38,
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_raw_cgpa(raw), expected)

    def test_unsupported_or_ambiguous_formats_return_none(self):
        cases = [
            None,
            "",
            "A grade",
            "First class",
            "11",
            "101%",
            "4.2/4",
            "7.2/9",
            "CGPA: 9.1 out of 10",
            "8.7 9.1",
        ]

        for raw in cases:
            with self.subTest(raw=raw):
                self.assertIsNone(normalize_raw_cgpa(raw))

    def test_mutates_resume_without_changing_raw_cgpa(self):
        resume = ParsedResume(
            file_path="candidate.pdf",
            parse_quality=ParseQuality.CLEAN,
            raw_cgpa="3.6/4",
            normalized_cgpa=None,
            grade_scale_assumption="previous",
        )

        result = normalize_grade(resume)

        self.assertIs(result, resume)
        self.assertEqual(resume.raw_cgpa, "3.6/4")
        self.assertEqual(resume.normalized_cgpa, 9.0)
        self.assertIsNone(resume.grade_scale_assumption)

    def test_sets_normalized_cgpa_none_for_ambiguous_resume_grade(self):
        resume = ParsedResume(
            file_path="candidate.pdf",
            parse_quality=ParseQuality.PARTIAL,
            raw_cgpa="7.2/9",
            normalized_cgpa=8.0,
        )

        normalize_grade(resume)

        self.assertEqual(resume.raw_cgpa, "7.2/9")
        self.assertIsNone(resume.normalized_cgpa)


if __name__ == "__main__":
    unittest.main()
