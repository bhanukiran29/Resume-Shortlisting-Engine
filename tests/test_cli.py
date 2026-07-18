from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cli
from engine.models import ParseQuality, ParsedResume


class CLITests(unittest.TestCase):
    def test_run_pipeline_wires_deterministic_stages(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            jd_path = Path(tmp_dir) / "jd.json"
            jd_path.write_text(
                '{"job_id":"jd","title":"Role","slot_count":1,'
                '"required_skills":["Python"],"min_cgpa":8.0}',
                encoding="utf-8",
            )
            parsed = ParsedResume(
                file_path="resume.pdf",
                parse_quality=ParseQuality.PARTIAL,
                raw_text="Asha Rao\nasha@example.com\nEducation\nCGPA: 8.7\nSkills Python",
                word_count=60,
            )

            with patch("cli.parse_pdf", return_value=parsed), patch("cli.apply_ocr_fallback") as ocr:
                candidate = cli.run_pipeline("resume.pdf", jd_path)

        ocr.assert_not_called()
        self.assertEqual(candidate.job_id, "jd")
        self.assertIsNotNone(candidate.score_breakdown)
        self.assertIsNotNone(candidate.confidence)
        self.assertEqual([skill.name for skill in candidate.matched_required], ["Python"])


if __name__ == "__main__":
    unittest.main()
