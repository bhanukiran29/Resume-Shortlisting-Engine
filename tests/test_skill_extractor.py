from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.models import ExtractionMatchType, ParsedResume, ParseQuality
from engine.skill_extractor import extract_skills, extract_skills_from_text


def skill_names(text: str | None) -> list[str]:
    return [skill.name for skill in extract_skills_from_text(text)]


class SkillExtractorTests(unittest.TestCase):
    def test_empty_resume_returns_empty_list(self):
        self.assertEqual(skill_names(None), [])
        self.assertEqual(skill_names(""), [])

    def test_duplicate_skills_are_stored_once(self):
        self.assertEqual(skill_names("Python python PYTHON"), ["Python"])

    def test_mixed_casing_normalizes_to_vocab_name(self):
        self.assertEqual(skill_names("python SQL mongoDB"), ["Python", "SQL", "MongoDB"])

    def test_punctuation_does_not_block_explicit_matches(self):
        self.assertEqual(
            skill_names("Skills: Python, Java; Docker/Git (SQL)."),
            ["Python", "Java", "Docker", "Git", "SQL"],
        )

    def test_c_does_not_match_inside_cloud(self):
        self.assertEqual(skill_names("Cloud computing with C and Git"), ["C", "Git"])

    def test_go_does_not_match_ordinary_word_fragments(self):
        self.assertEqual(skill_names("I undergo training and go-live work with Golang"), ["Go"])

    def test_nodejs_normalizes_to_node_dot_js(self):
        self.assertEqual(skill_names("Built APIs with Node and nodejs"), ["Node.js"])

    def test_reactjs_normalizes_to_react(self):
        self.assertEqual(skill_names("Frontend work in ReactJS and react.js"), ["React"])

    def test_ordering_preserves_first_occurrence(self):
        self.assertEqual(
            skill_names("Docker before Python, then SQL before Java"),
            ["Docker", "Python", "SQL", "Java"],
        )

    def test_unknown_skills_are_ignored(self):
        self.assertEqual(skill_names("Rust Elixir Kubernetes"), [])

    def test_mutates_resume_skills_only(self):
        resume = ParsedResume(
            file_path="candidate.pdf",
            parse_quality=ParseQuality.CLEAN,
            raw_text="Python and Docker",
            name="Asha Rao",
        )

        result = extract_skills(resume)

        self.assertIs(result, resume)
        self.assertEqual([skill.name for skill in resume.skills], ["Python", "Docker"])
        self.assertTrue(
            all(skill.match_type == ExtractionMatchType.EXACT for skill in resume.skills)
        )
        self.assertEqual(resume.name, "Asha Rao")


if __name__ == "__main__":
    unittest.main()
