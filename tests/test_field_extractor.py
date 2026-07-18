from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.field_extractor import extract_fields


class FieldExtractorTests(unittest.TestCase):
    def test_extracts_owned_fields_and_mutates_same_resume(self):
        resume = SimpleNamespace(
            raw_text="""
Jane Priya Shah
Portfolio: https://example.com
jane.shah@example.com | +91 98765 43210

Summary
Engineer with backend experience.

Education
B.Tech Computer Science
National Institute of Technology Delhi
2018 - 2022
CGPA: 8.7/10

Skills
Python, SQL
""",
            is_multi_column=True,
        )

        result = extract_fields(resume)

        self.assertIs(result, resume)
        self.assertEqual(resume.name, "Jane Priya Shah")
        self.assertEqual(resume.email, "jane.shah@example.com")
        self.assertEqual(resume.phone, "+91 98765 43210")
        self.assertEqual(resume.degree, "B.Tech Computer Science")
        self.assertEqual(resume.college, "National Institute of Technology Delhi")
        self.assertEqual(resume.grad_year, 2022)
        self.assertEqual(resume.raw_cgpa, "8.7/10")

    def test_email_and_phone_fallback_to_whole_document(self):
        resume = SimpleNamespace(
            raw_text="""
Not A Name 2024
www.example.com
Backend Engineer
Header line four
Header line five
Header line six
Header line seven
Header line eight
Header line nine
Header line ten
Header line eleven
Header line twelve
Contact later@example.com after the header
Phone 555-123-4567 after the header
""",
        )

        extract_fields(resume)

        self.assertIsNone(resume.name)
        self.assertEqual(resume.email, "later@example.com")
        self.assertEqual(resume.phone, "555-123-4567")

    def test_education_fields_do_not_escape_education_block(self):
        resume = SimpleNamespace(
            raw_text="""
Ravi Kumar
ravi@example.com
9999999999

Experience
Built tools at Example University Labs in 2021.
GPA: 4.0
""",
        )

        extract_fields(resume)

        self.assertEqual(resume.name, "Ravi Kumar")
        self.assertIsNone(resume.college)
        self.assertIsNone(resume.degree)
        self.assertIsNone(resume.grad_year)
        self.assertIsNone(resume.raw_cgpa)


if __name__ == "__main__":
    unittest.main()
