"""
engine/models.py

The single shared data contract for the pipeline. Every other module
imports its shapes from here instead of inventing its own field names by
convention — that's the integration bug we're building this file to
prevent.

Nothing in this file decides anything. No thresholds, no scoring, no
classification logic. If you're about to add a method that answers a
question ("is this Clean?", "did this pass?"), that logic belongs in
parse_quality.py / score_engine.py / confidence_engine.py — not here.
Properties on these classes are limited to pure re-derivations of data
that's already present (e.g. a total that sums fields already on the
object), never a judgment call.

Stage 1 (extraction):  file path            -> ParsedResume
Stage 2 (matching):    ParsedResume + JobDescription -> ScoredCandidate
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Enums
#
# All string-backed (str, Enum) on purpose: they compare equal to plain
# strings ("Clean" == ParseQuality.CLEAN is True) and json.dumps() serializes
# them as their string value with zero custom encoder work in reporting.py.
# ---------------------------------------------------------------------------


class ParseQuality(str, Enum):
    """Outcome of Stage 1 extraction for a single resume file."""

    CLEAN = "Clean"      # core fields found + good text yield
    PARTIAL = "Partial"  # missing fields and/or thin yield, but usable
    FAILED = "Failed"    # no usable text even after OCR fallback


class ExtractionMatchType(str, Enum):
    """
    How skill_extractor found a skill inside the resume's own text, against
    skills_vocab.json. No PARTIAL here on purpose — a skill is either
    present in the resume or it isn't. "Partial" only becomes meaningful
    once you're comparing against one specific JD's requirement, which is
    what JDMatchType (below) is for.
    """

    EXACT = "exact"
    SYNONYM = "synonym"
    IMPLICIT = "implicit"  # embedding-similarity hit, no vocab/synonym string match


class JDMatchType(str, Enum):
    """How skill_matcher tied one of the candidate's skills to a JD entry."""

    EXACT = "exact"
    SYNONYM = "synonym"
    PARTIAL = "partial"
    IMPLICIT = "implicit"


class ConfidenceTier(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AllocationStatus(str, Enum):
    SHORTLIST = "Shortlist"
    RESERVE = "Reserve"
    NOT_SELECTED = "Not Selected"
    UNSCORED = "Unscored"  # default; also where Failed parses stay forever


# ---------------------------------------------------------------------------
# Stage 1 output
# ---------------------------------------------------------------------------


@dataclass
class ExtractedSkill:
    """One skill pulled from a resume's full text, independent of any JD."""

    name: str
    match_type: ExtractionMatchType


@dataclass
class ParsedResume:
    """
    Output of Stage 1. Produced unconditionally for every input file,
    including a Failed one — a Failed resume still has file_path,
    parse_quality, and parse_quality_reason populated; every other field
    stays at its default. Stage 2 must be able to check `.is_failed` and
    skip cleanly without ever touching a null field below it.
    """

    file_path: str
    parse_quality: ParseQuality
    parse_quality_reason: Optional[str] = None  # populated for Partial/Failed

    # Raw extraction — pdf_parser.py / ocr_fallback.py
    raw_text: Optional[str] = None
    word_count: int = 0
    used_ocr: bool = False
    is_multi_column: bool = False

    # Contact / academic fields — field_extractor.py. Missing means None,
    # never guessed at.
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    grad_year: Optional[int] = None

    # Grades — grade_normalizer.py
    raw_cgpa: Optional[str] = None            # exactly as written on the resume
    normalized_cgpa: Optional[float] = None   # unified 10-point scale
    grade_scale_assumption: Optional[str] = None  # set only when the scale was ambiguous

    # Skills — skill_extractor.py
    skills: List[ExtractedSkill] = field(default_factory=list)

    # Practical signal (projects / internships) — feeds score_engine's 20-pt
    # practical-signal component. Flagging in the reply below: no module in
    # the spec is explicitly assigned to populate this field.
    practical_experience: List[str] = field(default_factory=list)

    @property
    def file_name(self) -> str:
        return Path(self.file_path).name

    @property
    def is_failed(self) -> bool:
        return self.parse_quality == ParseQuality.FAILED


# ---------------------------------------------------------------------------
# Stage 2 input — built by jd_loader.py from data/jds/*.json
# ---------------------------------------------------------------------------


@dataclass
class JobDescription:
    """
    One role. A 6th JD means dropping a new JSON file in data/jds/, not
    touching code — so every field here must come from that file, nothing
    hardcoded per-role in Python. No degree field on purpose: the JD table
    carries a CGPA minimum, not a degree requirement.
    """

    job_id: str
    title: str
    slot_count: int
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    min_cgpa: Optional[float] = None
    raw_description: Optional[str] = None  # populated by Bonus C's freeform path


# ---------------------------------------------------------------------------
# Stage 2 output
# ---------------------------------------------------------------------------


@dataclass
class MatchedSkill:
    name: str
    match_type: JDMatchType
    is_required: bool  # required[] vs preferred[] on the JD


@dataclass
class ScoreBreakdown:
    """
    Every component score_engine computes, kept separate rather than
    collapsed into one number so explanation_engine can rank contributions
    instead of re-deriving them from an opaque total.
    """

    required_skill_score: float = 0.0
    preferred_skill_score: float = 0.0
    cgpa_score: float = 0.0
    practical_signal_score: float = 0.0
    conflict_adjustment: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.required_skill_score
            + self.preferred_skill_score
            + self.cgpa_score
            + self.practical_signal_score
            + self.conflict_adjustment
        )


@dataclass
class ScoredCandidate:
    """
    Output of Stage 2 for one (resume, JD) pair. For a Failed parse, every
    field from score_breakdown down stays at its default — reporting.py
    checks `resume.is_failed` FIRST and prints "Failed Parse — recommend
    human review" instead of ever reading total_score or confidence.
    """

    resume: ParsedResume
    job_id: str

    score_breakdown: Optional[ScoreBreakdown] = None
    confidence: Optional[ConfidenceTier] = None

    matched_required: List[MatchedSkill] = field(default_factory=list)
    matched_preferred: List[MatchedSkill] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)

    explanation: List[str] = field(default_factory=list)  # exactly 3 bullets
    allocation: AllocationStatus = AllocationStatus.UNSCORED

    @property
    def total_score(self) -> Optional[float]:
        if self.score_breakdown is None:
            return None
        return self.score_breakdown.total
