"""
engine/grade_normalizer.py

Deterministically normalize ParsedResume.raw_cgpa onto a 10-point scale.

This stage runs after field_extractor.py. It preserves raw_cgpa exactly,
does not inspect raw resume text, and leaves normalized_cgpa as None when
the grade format is ambiguous or unsupported.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional

from engine.models import ParsedResume


NUMBER = r"(?:\d{1,3}(?:\.\d{1,2})?)"

PERCENT_PATTERN = re.compile(rf"^\s*({NUMBER})\s*%\s*$")

FRACTION_PATTERN = re.compile(
    rf"^\s*(?:cgpa|gpa)?\s*:?\s*({NUMBER})\s*/\s*({NUMBER})\s*(?:cgpa|gpa)?\s*$",
    re.I,
)

LABELED_NUMBER_PATTERN = re.compile(
    rf"^\s*(?:(?:cgpa|gpa)\s*:?\s*({NUMBER})|({NUMBER})\s*(?:cgpa|gpa))\s*$",
    re.I,
)

PLAIN_NUMBER_PATTERN = re.compile(rf"^\s*({NUMBER})\s*$")

SUPPORTED_FRACTION_SCALES = {Decimal("4"), Decimal("4.0"), Decimal("10"), Decimal("10.0")}

OUTPUT_QUANT = Decimal("0.01")


def normalize_grade(resume: ParsedResume) -> ParsedResume:
    """
    Mutate and return the same ParsedResume instance.
    """
    resume.normalized_cgpa = normalize_raw_cgpa(resume.raw_cgpa)
    resume.grade_scale_assumption = None
    return resume


def normalize_raw_cgpa(raw_cgpa: Optional[str]) -> Optional[float]:
    if raw_cgpa is None:
        return None

    raw = raw_cgpa.strip()
    if not raw:
        return None

    percent_match = PERCENT_PATTERN.fullmatch(raw)
    if percent_match:
        percent = _to_decimal(percent_match.group(1))
        if percent is None or percent < 0 or percent > 100:
            return None
        return _to_float(percent / Decimal("10"))

    fraction_match = FRACTION_PATTERN.fullmatch(raw)
    if fraction_match:
        value = _to_decimal(fraction_match.group(1))
        scale = _to_decimal(fraction_match.group(2))
        if value is None or scale is None:
            return None
        if scale not in SUPPORTED_FRACTION_SCALES:
            return None
        if value < 0 or value > scale:
            return None
        return _to_float((value / scale) * Decimal("10"))

    labeled_match = LABELED_NUMBER_PATTERN.fullmatch(raw)
    if labeled_match:
        value_text = labeled_match.group(1) or labeled_match.group(2)
        value = _to_decimal(value_text)
        if value is None or value < 0 or value > 10:
            return None
        return _to_float(value)

    plain_match = PLAIN_NUMBER_PATTERN.fullmatch(raw)
    if plain_match:
        value = _to_decimal(plain_match.group(1))
        if value is None or value < 0 or value > 10:
            return None
        return _to_float(value)

    return None


def _to_decimal(text: str) -> Optional[Decimal]:
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _to_float(value: Decimal) -> float:
    return float(value.quantize(OUTPUT_QUANT, rounding=ROUND_HALF_UP))


__all__ = ["normalize_grade", "normalize_raw_cgpa"]
