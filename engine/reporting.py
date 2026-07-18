"""
engine/reporting.py

Presentation-only report generation for completed candidate results.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any

from engine.models import ScoredCandidate


def candidate_report(candidate: ScoredCandidate) -> dict[str, Any]:
    resume = candidate.resume
    breakdown = candidate.score_breakdown
    return {
        "file_name": resume.file_name,
        "job_id": candidate.job_id,
        "parse_quality": resume.parse_quality.value,
        "parse_quality_reason": resume.parse_quality_reason,
        "overall_score": candidate.total_score,
        "confidence": candidate.confidence.value if candidate.confidence is not None else None,
        "allocation": candidate.allocation.value,
        "score_breakdown": _dataclass_dict(breakdown),
        "matched_required": [_dataclass_dict(skill) for skill in candidate.matched_required],
        "matched_preferred": [_dataclass_dict(skill) for skill in candidate.matched_preferred],
        "missing_required": list(candidate.missing_required),
        "parsed_fields": {
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "college": resume.college,
            "degree": resume.degree,
            "grad_year": resume.grad_year,
            "raw_cgpa": resume.raw_cgpa,
            "normalized_cgpa": resume.normalized_cgpa,
            "skills": [_dataclass_dict(skill) for skill in resume.skills],
        },
        "warnings": _warnings(candidate),
        "explanation": list(candidate.explanation),
    }


def report_to_json(candidate: ScoredCandidate) -> str:
    return json.dumps(candidate_report(candidate), indent=2, sort_keys=True)


def _dataclass_dict(value):
    if value is None:
        return None
    if is_dataclass(value):
        return asdict(value)
    return value


def _warnings(candidate: ScoredCandidate) -> list[str]:
    warnings: list[str] = []
    resume = candidate.resume
    if resume.is_failed:
        warnings.append("Failed parse; recommend human review.")
    if resume.is_multi_column:
        warnings.append("Resume appears multi-column; extraction may be incomplete.")
    if candidate.missing_required:
        warnings.append("One or more required skills were not matched.")
    if resume.normalized_cgpa is None and resume.raw_cgpa is not None:
        warnings.append("CGPA was present but could not be normalized.")
    return warnings


__all__ = ["candidate_report", "report_to_json"]
