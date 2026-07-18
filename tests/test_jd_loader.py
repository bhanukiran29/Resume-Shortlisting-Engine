from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.jd_loader import JDValidationError, load_jd, parse_jd_payload


class JDLoaderTests(unittest.TestCase):
    def test_parse_valid_payload_normalizes_fields(self):
        jd = parse_jd_payload(
            {
                "job_id": " jd-1 ",
                "title": " Backend Engineer ",
                "slot_count": 2,
                "required_skills": [" Python ", "python", "SQL"],
                "preferred_skills": ["Docker", " Git "],
                "min_cgpa": 7,
                "raw_description": " Build APIs ",
            }
        )

        self.assertEqual(jd.job_id, "jd-1")
        self.assertEqual(jd.title, "Backend Engineer")
        self.assertEqual(jd.slot_count, 2)
        self.assertEqual(jd.required_skills, ["Python", "SQL"])
        self.assertEqual(jd.preferred_skills, ["Docker", "Git"])
        self.assertEqual(jd.min_cgpa, 7.0)
        self.assertEqual(jd.raw_description, "Build APIs")

    def test_rejects_malformed_payload_with_structured_errors(self):
        with self.assertRaises(JDValidationError) as context:
            parse_jd_payload(
                {
                    "job_id": "",
                    "title": "Role",
                    "slot_count": 0,
                    "required_skills": ["Python", ""],
                    "min_cgpa": 11,
                }
            )

        self.assertIn("job_id must be a non-empty string", context.exception.errors)
        self.assertIn("slot_count must be a positive integer", context.exception.errors)
        self.assertIn("required_skills[1] must be a non-empty string", context.exception.errors)
        self.assertIn("min_cgpa must be between 0 and 10 when provided", context.exception.errors)

    def test_load_jd_reads_json_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "jd.json"
            path.write_text(
                '{"job_id":"jd","title":"Role","slot_count":1,"required_skills":["Python"]}',
                encoding="utf-8",
            )

            jd = load_jd(path)

        self.assertEqual(jd.job_id, "jd")
        self.assertEqual(jd.required_skills, ["Python"])


if __name__ == "__main__":
    unittest.main()
