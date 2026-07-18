"""
engine/skill_extractor.py

Deterministic vocabulary-based skill extraction from ParsedResume.raw_text.

This module does not score, match against JDs, infer synonyms, use fuzzy
matching, call embeddings, or fall back to LLMs. A skill is emitted only
when raw resume text explicitly matches a configured vocabulary alias.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from config import SKILLS_VOCAB_PATH
from engine.models import ExtractedSkill, ExtractionMatchType, ParsedResume


@dataclass(frozen=True)
class SkillAlias:
    canonical_name: str
    alias: str
    pattern: re.Pattern[str]


def extract_skills(resume: ParsedResume) -> ParsedResume:
    """
    Mutate resume.skills from explicit vocabulary matches and return resume.
    """
    resume.skills = extract_skills_from_text(resume.raw_text)
    return resume


def extract_skills_from_text(text: str | None) -> list[ExtractedSkill]:
    if not text:
        return []

    matches: list[tuple[int, int, str]] = []
    for skill_alias in _load_skill_aliases():
        for match in skill_alias.pattern.finditer(text):
            matches.append((match.start(), match.end(), skill_alias.canonical_name))

    matches.sort(key=lambda item: (item[0], item[1], item[2].lower()))
    return _dedupe_by_first_occurrence(matches)


def _dedupe_by_first_occurrence(
    matches: Iterable[tuple[int, int, str]]
) -> list[ExtractedSkill]:
    seen: set[str] = set()
    skills: list[ExtractedSkill] = []
    for _start, _end, canonical_name in matches:
        key = canonical_name.casefold()
        if key in seen:
            continue
        seen.add(key)
        skills.append(
            ExtractedSkill(
                name=canonical_name,
                match_type=ExtractionMatchType.EXACT,
            )
        )
    return skills


def _load_skill_aliases(vocab_path: Path = SKILLS_VOCAB_PATH) -> list[SkillAlias]:
    if not vocab_path.exists():
        return []

    with vocab_path.open("r", encoding="utf-8") as vocab_file:
        raw_vocab = json.load(vocab_file)

    aliases: list[SkillAlias] = []
    for entry in raw_vocab:
        canonical_name = entry["name"]
        raw_aliases = entry.get("aliases", [])
        for alias in raw_aliases:
            aliases.append(
                SkillAlias(
                    canonical_name=canonical_name,
                    alias=alias,
                    pattern=_compile_alias_pattern(alias),
                )
            )

    aliases.sort(key=lambda item: (-len(item.alias), item.canonical_name.lower(), item.alias))
    return aliases


def _compile_alias_pattern(alias: str) -> re.Pattern[str]:
    escaped = re.escape(alias)
    return re.compile(rf"(?<![A-Za-z0-9+#.]){escaped}(?![A-Za-z0-9+#.])", re.I)


__all__ = ["extract_skills", "extract_skills_from_text"]
