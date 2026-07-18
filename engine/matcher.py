"""
engine/matcher.py

Deterministic non-scoring matching between a ParsedResume and JobDescription.
"""

from __future__ import annotations

from engine.models import JDMatchType, JobDescription, MatchedSkill, ParsedResume, ScoredCandidate


def match_candidate(resume: ParsedResume, jd: JobDescription) -> ScoredCandidate:
    candidate = ScoredCandidate(resume=resume, job_id=jd.job_id)
    if resume.is_failed:
        return candidate

    resume_skills = _skill_name_map(resume)
    candidate.matched_required = _matched_skills(jd.required_skills, resume_skills, is_required=True)
    candidate.matched_preferred = _matched_skills(jd.preferred_skills, resume_skills, is_required=False)
    candidate.missing_required = [
        skill for skill in jd.required_skills if skill.casefold() not in resume_skills
    ]
    return candidate


def _skill_name_map(resume: ParsedResume) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for skill in resume.skills:
        mapped.setdefault(skill.name.casefold(), skill.name)
    return mapped


def _matched_skills(
    jd_skills: list[str], resume_skills: dict[str, str], *, is_required: bool
) -> list[MatchedSkill]:
    matches: list[MatchedSkill] = []
    for jd_skill in jd_skills:
        if jd_skill.casefold() in resume_skills:
            matches.append(
                MatchedSkill(
                    name=jd_skill,
                    match_type=JDMatchType.EXACT,
                    is_required=is_required,
                )
            )
    return matches


__all__ = ["match_candidate"]
