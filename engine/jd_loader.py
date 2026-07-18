"""
engine/jd_loader.py

Load and validate structured job-description JSON files.

This module does not score, match, infer requirements, or parse freeform
text. It only converts explicit JSON fields into the existing
JobDescription dataclass.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from engine.models import JobDescription


@dataclass(frozen=True)
class JDValidationError(ValueError):
    errors: list[str]

    def __str__(self) -> str:
        return "Invalid job description: " + "; ".join(self.errors)


def load_jd(file_path: str | Path) -> JobDescription:
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as jd_file:
            payload = json.load(jd_file)
    except json.JSONDecodeError as exc:
        raise JDValidationError([f"JSON parse error at line {exc.lineno}, column {exc.colno}"]) from exc
    except OSError as exc:
        raise JDValidationError([f"Could not read file: {exc}"]) from exc

    return parse_jd_payload(payload)


def parse_jd_payload(payload: Any) -> JobDescription:
    errors: list[str] = []
    if not isinstance(payload, dict):
        raise JDValidationError(["top-level value must be an object"])

    job_id = _required_string(payload, "job_id", errors)
    title = _required_string(payload, "title", errors)
    slot_count = _required_positive_int(payload, "slot_count", errors)
    required_skills = _optional_string_list(payload, "required_skills", errors)
    preferred_skills = _optional_string_list(payload, "preferred_skills", errors)
    min_cgpa = _optional_number(payload, "min_cgpa", errors)
    raw_description = _optional_string(payload, "raw_description", errors)

    if min_cgpa is not None and not 0 <= min_cgpa <= 10:
        errors.append("min_cgpa must be between 0 and 10 when provided")

    if errors:
        raise JDValidationError(errors)

    return JobDescription(
        job_id=job_id,
        title=title,
        slot_count=slot_count,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        min_cgpa=min_cgpa,
        raw_description=raw_description,
    )


def _required_string(payload: dict[str, Any], field_name: str, errors: list[str]) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field_name} must be a non-empty string")
        return ""
    return value.strip()


def _optional_string(payload: dict[str, Any], field_name: str, errors: list[str]) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field_name} must be a string when provided")
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _required_positive_int(payload: dict[str, Any], field_name: str, errors: list[str]) -> int:
    value = payload.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        errors.append(f"{field_name} must be a positive integer")
        return 0
    return value


def _optional_number(payload: dict[str, Any], field_name: str, errors: list[str]) -> float | None:
    value = payload.get(field_name)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{field_name} must be a number when provided")
        return None
    return float(value)


def _optional_string_list(payload: dict[str, Any], field_name: str, errors: list[str]) -> list[str]:
    value = payload.get(field_name, [])
    if not isinstance(value, list):
        errors.append(f"{field_name} must be a list of strings")
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{field_name}[{index}] must be a non-empty string")
            continue
        stripped = item.strip()
        key = stripped.casefold()
        if key not in seen:
            seen.add(key)
            normalized.append(stripped)
    return normalized


__all__ = ["JDValidationError", "load_jd", "parse_jd_payload"]
