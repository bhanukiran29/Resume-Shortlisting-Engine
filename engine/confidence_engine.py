"""
engine/confidence_engine.py

Deterministic confidence assignment independent of scoring.
"""

from __future__ import annotations

from config import (
    CORE_FIELDS_FOR_CLEAN,
    PARSE_QUALITY_CONFIDENCE_CAP,
    SKILL_CERTAINTY_HIGH_EXACT_RATIO,
    SKILL_CERTAINTY_MEDIUM_EXACT_RATIO,
)
from engine.models import ConfidenceTier, JDMatchType, ScoredCandidate


_TIER_RANK = {
    ConfidenceTier.LOW: 0,
    ConfidenceTier.MEDIUM: 1,
    ConfidenceTier.HIGH: 2,
}


def assign_confidence(candidate: ScoredCandidate) -> ScoredCandidate:
    if candidate.resume.is_failed:
        candidate.confidence = ConfidenceTier.LOW
        return candidate

    cap = _parse_quality_cap(candidate.resume.parse_quality.value)
    completeness_tier = _field_completeness_tier(candidate)
    certainty_tier = _skill_certainty_tier(candidate)
    candidate.confidence = _min_tier(cap, completeness_tier, certainty_tier)
    return candidate


def _parse_quality_cap(parse_quality: str) -> ConfidenceTier:
    configured = PARSE_QUALITY_CONFIDENCE_CAP.get(parse_quality, "Low")
    return ConfidenceTier(configured)


def _field_completeness_tier(candidate: ScoredCandidate) -> ConfidenceTier:
    missing = [field for field in CORE_FIELDS_FOR_CLEAN if getattr(candidate.resume, field) is None]
    if not missing:
        return ConfidenceTier.HIGH
    if len(missing) <= 2:
        return ConfidenceTier.MEDIUM
    return ConfidenceTier.LOW


def _skill_certainty_tier(candidate: ScoredCandidate) -> ConfidenceTier:
    matched = candidate.matched_required + candidate.matched_preferred
    if not matched:
        return ConfidenceTier.LOW
    exact_count = sum(1 for skill in matched if skill.match_type == JDMatchType.EXACT)
    exact_ratio = exact_count / len(matched)
    if exact_ratio >= SKILL_CERTAINTY_HIGH_EXACT_RATIO:
        return ConfidenceTier.HIGH
    if exact_ratio >= SKILL_CERTAINTY_MEDIUM_EXACT_RATIO:
        return ConfidenceTier.MEDIUM
    return ConfidenceTier.LOW


def _min_tier(*tiers: ConfidenceTier) -> ConfidenceTier:
    return min(tiers, key=lambda tier: _TIER_RANK[tier])


__all__ = ["assign_confidence"]
