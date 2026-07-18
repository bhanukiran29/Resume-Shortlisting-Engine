"""
engine/score_engine.py

Apply deterministic scoring weights to matcher output.
"""

from __future__ import annotations

from config import (
    CGPA_PENALTY_PER_POINT_GAP,
    CGPA_WEIGHT,
    CONFLICT_ADJUSTMENT_MAX,
    PRACTICAL_SIGNAL_WEIGHT,
    PREFERRED_SKILL_WEIGHT,
    REQUIRED_SKILL_WEIGHT,
)
from engine.models import JobDescription, ScoreBreakdown, ScoredCandidate


def score_candidate(candidate: ScoredCandidate, jd: JobDescription) -> ScoredCandidate:
    if candidate.resume.is_failed:
        candidate.score_breakdown = None
        return candidate

    candidate.score_breakdown = ScoreBreakdown(
        required_skill_score=_skill_component(
            len(candidate.matched_required), len(jd.required_skills), REQUIRED_SKILL_WEIGHT
        ),
        preferred_skill_score=_skill_component(
            len(candidate.matched_preferred), len(jd.preferred_skills), PREFERRED_SKILL_WEIGHT
        ),
        cgpa_score=_cgpa_component(candidate.resume.normalized_cgpa, jd.min_cgpa),
        practical_signal_score=_practical_component(candidate.resume.practical_experience),
        conflict_adjustment=_conflict_adjustment(candidate, jd),
    )
    return candidate


def _skill_component(matched_count: int, total_count: int, weight: float) -> float:
    if total_count <= 0:
        return weight
    return round((matched_count / total_count) * weight, 2)


def _cgpa_component(candidate_cgpa: float | None, min_cgpa: float | None) -> float:
    if min_cgpa is None:
        return CGPA_WEIGHT
    if candidate_cgpa is None:
        return 0.0
    if candidate_cgpa >= min_cgpa:
        return CGPA_WEIGHT
    gap = min_cgpa - candidate_cgpa
    return round(max(0.0, CGPA_WEIGHT - (gap * CGPA_PENALTY_PER_POINT_GAP)), 2)


def _practical_component(practical_experience: list[str]) -> float:
    return PRACTICAL_SIGNAL_WEIGHT if practical_experience else 0.0


def _conflict_adjustment(candidate: ScoredCandidate, jd: JobDescription) -> float:
    if not jd.required_skills:
        return 0.0
    missing_ratio = len(candidate.missing_required) / len(jd.required_skills)
    return round(-CONFLICT_ADJUSTMENT_MAX * missing_ratio, 2)


__all__ = ["score_candidate"]
