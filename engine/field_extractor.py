"""
engine/field_extractor.py

Deterministic field extraction for ParsedResume objects.

This module owns only literal profile fields. It does not score, infer,
normalize grades, extract skills, call LLMs, or suppress multi-column
resumes. Every extractor reads only its assigned region and leaves missing
or uncertain fields as None.
"""

from __future__ import annotations

import re
from typing import Iterable, Sequence

try:
    from config import GRAD_YEAR_MAX, GRAD_YEAR_MIN, HEADER_WINDOW_LINES
except ImportError:  # pragma: no cover - standalone script fallback
    HEADER_WINDOW_LINES = 12
    GRAD_YEAR_MIN = 1990
    GRAD_YEAR_MAX = 2035
except AttributeError:  # pragma: no cover - older config fallback
    HEADER_WINDOW_LINES = 12
    GRAD_YEAR_MIN = 1990
    GRAD_YEAR_MAX = 2035


EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.+-])"
)

PHONE_CANDIDATE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"
)

URL_PATTERN = re.compile(r"\b(?:https?://|www\.|linkedin\.com|github\.com)\S*", re.I)

NAME_PATTERN = re.compile(
    r"^(?:[A-Z][a-z]+|[A-Z]{2,})(?:[-'][A-Z][a-z]+)?"
    r"(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,})(?:[-'][A-Z][a-z]+)?){1,3}$"
)

NAME_REJECT_WORDS = {
    "analyst",
    "architect",
    "backend",
    "consultant",
    "developer",
    "education",
    "engineer",
    "experience",
    "frontend",
    "intern",
    "manager",
    "objective",
    "professional",
    "profile",
    "resume",
    "scientist",
    "specialist",
    "skills",
    "summary",
}

EDUCATION_HEADER_PATTERN = re.compile(
    r"^\s*(?:education|academic(?:\s+background|\s+qualification|s)?|"
    r"educational\s+qualification|qualifications|academics)\s*:?\s*$",
    re.I,
)

SECTION_HEADER_PATTERN = re.compile(
    r"^\s*(?:experience|work\s+experience|employment|projects?|skills?|"
    r"technical\s+skills|certifications?|achievements?|awards?|publications?|"
    r"summary|profile|objective|contact|personal\s+details|references?|"
    r"languages?|interests?|hobbies|training|internships?)\s*:?\s*$",
    re.I,
)

INSTITUTION_KEYWORDS = (
    "university",
    "college",
    "institute",
    "school",
    "academy",
    "polytechnic",
)

DEGREE_KEYWORD_PATTERN = re.compile(
    r"\b(?:b\.?\s?tech|m\.?\s?tech|b\.?\s?e\.?|m\.?\s?e\.?|b\.?\s?sc|"
    r"m\.?\s?sc|b\.?\s?a\.?|m\.?\s?a\.?|b\.?\s?com|m\.?\s?com|"
    r"bba|bca|b\.?\s?des|bfa|mba|"
    r"ph\.?\s?d|doctorate|bachelor(?:'s)?|master(?:'s)?|degree|diploma|"
    r"engineering|science|arts|commerce|computer\s+applications)\b",
    re.I,
)

GRAD_CONTEXT_PATTERN = re.compile(
    r"\b(?:graduat(?:ed|ion|ing)?|class\s+of|expected|completed|completion|"
    r"passing|pass(?:ed)?\s+out|year)\b",
    re.I,
)

CGPA_PATTERN = re.compile(
    r"\b(?:cgpa|gpa)\b\s*[:=-]?\s*"
    r"(?P<grade>\d+(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?)?|"
    r"\d+(?:\.\d+)?\s+out\s+of\s+\d+(?:\.\d+)?)"
    r"|\b(?:percentage|percent)\b\s*[:=-]?\s*"
    r"(?P<percent>\d+(?:\.\d+)?\s*%)",
    re.I,
)

PHONE_MIN_DIGITS = 10


def extract_fields(resume):
    """
    Mutate and return the same ParsedResume-like instance.
    """
    text = _resume_text(resume)
    lines = _non_empty_lines(text)
    header_lines = lines[:HEADER_WINDOW_LINES]
    header_text = "\n".join(header_lines)
    education_lines = _education_block(lines)
    education_text = "\n".join(education_lines)

    _set_field(resume, "email", _extract_email(header_text, text))
    _set_field(resume, "phone", _extract_phone(header_text, text))
    _set_field(resume, "name", _extract_name(header_lines[:3]))
    _set_field(resume, "college", _extract_college(education_lines))
    _set_field(resume, "degree", _extract_degree(education_lines))
    _set_field(resume, "grad_year", _extract_grad_year(education_lines))
    _set_field(resume, "raw_cgpa", _extract_raw_cgpa(education_text))

    return resume


def _resume_text(resume) -> str:
    for attr in ("raw_text", "extracted_text"):
        value = getattr(resume, attr, None)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _set_field(resume, field_name: str, value) -> None:
    try:
        setattr(resume, field_name, value)
    except (AttributeError, ValueError):
        object.__setattr__(resume, field_name, value)


def _non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _dedupe_preserve_order(matches: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for match in matches:
        if match not in seen:
            seen.add(match)
            deduped.append(match)
    return deduped


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    matches = _dedupe_preserve_order(match.group(0).strip() for match in pattern.finditer(text))
    return matches[0] if matches else None


def _extract_email(header_text: str, full_text: str) -> str | None:
    return _first_match(EMAIL_PATTERN, header_text) or _first_match(EMAIL_PATTERN, full_text)


def _extract_phone(header_text: str, full_text: str) -> str | None:
    return _first_phone_in_region(header_text) or _first_phone_in_region(full_text)


def _first_phone_in_region(text: str) -> str | None:
    candidates = _dedupe_preserve_order(
        match.group(0).strip(" .,-()") for match in PHONE_CANDIDATE_PATTERN.finditer(text)
    )
    for candidate in candidates:
        digits = re.sub(r"\D", "", candidate)
        if len(digits) >= PHONE_MIN_DIGITS:
            return candidate
    return None


def _extract_name(candidate_lines: Sequence[str]) -> str | None:
    for line in candidate_lines:
        candidate = line.strip()
        if EMAIL_PATTERN.search(candidate) or URL_PATTERN.search(candidate):
            continue
        if any(char.isdigit() for char in candidate):
            continue
        if any(word.lower() in NAME_REJECT_WORDS for word in candidate.split()):
            continue
        if NAME_PATTERN.fullmatch(candidate):
            return candidate
    return None


def _education_block(lines: Sequence[str]) -> list[str]:
    start_index = None
    for index, line in enumerate(lines):
        if EDUCATION_HEADER_PATTERN.fullmatch(line):
            start_index = index + 1
            break

    if start_index is None:
        return []

    block: list[str] = []
    for line in lines[start_index:]:
        if SECTION_HEADER_PATTERN.fullmatch(line):
            break
        if EDUCATION_HEADER_PATTERN.fullmatch(line):
            continue
        block.append(line)
    return block


def _extract_college(education_lines: Sequence[str]) -> str | None:
    candidates: list[str] = []
    for line in education_lines:
        lower_line = line.lower()
        if any(keyword in lower_line for keyword in INSTITUTION_KEYWORDS):
            if DEGREE_KEYWORD_PATTERN.search(line) and not _has_institution_keyword(lower_line):
                continue
            candidates.append(_clean_trailing_years_and_scores(line))

    candidates = [candidate for candidate in _dedupe_preserve_order(candidates) if candidate]
    return candidates[0] if candidates else None


def _has_institution_keyword(lower_line: str) -> bool:
    return any(keyword in lower_line for keyword in INSTITUTION_KEYWORDS)


def _extract_degree(education_lines: Sequence[str]) -> str | None:
    candidates = [
        _clean_trailing_years_and_scores(line)
        for line in education_lines
        if DEGREE_KEYWORD_PATTERN.search(line)
    ]
    candidates = [candidate for candidate in _dedupe_preserve_order(candidates) if candidate]
    return candidates[0] if candidates else None


def _extract_grad_year(education_lines: Sequence[str]) -> int | None:
    contextual_lines = [line for line in education_lines if GRAD_CONTEXT_PATTERN.search(line)]
    degree_or_school_lines = [
        line
        for line in education_lines
        if DEGREE_KEYWORD_PATTERN.search(line) or _has_institution_keyword(line.lower())
    ]

    for group in (contextual_lines, degree_or_school_lines, list(education_lines)):
        year = _first_valid_year(group)
        if year is not None:
            return year
    return None


def _first_valid_year(lines: Sequence[str]) -> int | None:
    for line in lines:
        years = [
            int(match.group(0))
            for match in re.finditer(r"\b(?:19|20)\d{2}\b", line)
            if GRAD_YEAR_MIN <= int(match.group(0)) <= GRAD_YEAR_MAX
        ]
        if len(years) >= 2 and re.search(r"\b(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\b", line):
            return years[1]
        if years:
            return years[0]
    return None


def _extract_raw_cgpa(education_text: str) -> str | None:
    matches = _dedupe_preserve_order(
        (match.group("grade") or match.group("percent")).strip()
        for match in CGPA_PATTERN.finditer(education_text)
    )
    return matches[0] if matches else None


def _clean_trailing_years_and_scores(text: str) -> str:
    cleaned = re.sub(r"\b(?:19|20)\d{2}\b", "", text)
    cleaned = re.sub(r"\b(?:cgpa|gpa)\b\s*[:=-]?\s*\d+(?:\.\d+)?(?:\s*/\s*\d+(?:\.\d+)?)?", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip(" -|,;")


__all__ = ["extract_fields"]
