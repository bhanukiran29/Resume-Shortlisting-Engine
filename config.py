"""
config.py

Every tunable knob for the pipeline lives here: paths, weights, thresholds.
No business logic — this file is read by engine/*, never the reverse, and
it never imports from engine/ (keeps model shapes and tunable values fully
decoupled).

Every constant below is tagged:
  CERTAIN — taken directly from the graded spec, don't change without
            re-checking the rubric.
  DEFAULT — the spec gives a principle but not a number. These are starting
            points, not requirements. Override them once you've looked at
            the real 5-JD dataset instead of the practice set.
"""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
JD_DIR = DATA_DIR / "jds"
SKILLS_VOCAB_PATH = DATA_DIR / "skills_vocab.json"

# Fallback defaults so every module has something valid to import during
# standalone testing — cli.py should let both be overridden with real
# arguments (e.g. --resumes-dir, --output-dir) rather than relying on these.
DEFAULT_RESUME_DIR = BASE_DIR / "resumes"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"

PARSE_QUALITY_REPORT_FILENAME = "parse_quality_report.json"
SHORTLIST_FILENAME_TEMPLATE = "{job_id}_shortlist.json"

# Side effect, deliberately: reporting.py should never crash on a fresh
# clone just because output/ doesn't exist yet. Pull this out if you'd
# rather fail loudly on a missing directory than auto-create one.
DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Stage 1 — extraction thresholds
# ---------------------------------------------------------------------------

# CERTAIN — this is Bonus B's own stated trigger point.
OCR_WORD_COUNT_THRESHOLD = 50

# DEFAULT — "good yield" vs "low yield" isn't given a number. The practice
# set probe put real single-column resumes at 207-459 words; 150 is a
# floor comfortably under that, not a tight one. Re-check against the real
# 5-JD resumes, not the practice set — that set is explicitly a different,
# easier population (see the reply for why).
CLEAN_MIN_WORD_COUNT = 150

# DEFAULT — fields that must ALL be present for a Clean rating. Anything
# else missing drops a resume to Partial; it only drops to Failed when
# there's no usable text at all, even post-OCR.
CORE_FIELDS_FOR_CLEAN = ("name", "email", "college", "grad_year")

# DEFAULT -- first non-empty resume lines treated as the contact/header
# region by field_extractor.py. Kept in config so the region boundary is
# fixed and visible, not scattered through extraction logic.
HEADER_WINDOW_LINES = 12

# DEFAULT -- deterministic accepted graduation-year range for
# field_extractor.py. Years outside this range are ignored rather than
# guessed.
GRAD_YEAR_MIN = 1990
GRAD_YEAR_MAX = 2035


# ---------------------------------------------------------------------------
# Stage 1 -- parse quality classification
# ---------------------------------------------------------------------------

# DEFAULT -- length of a run of one repeated non-whitespace character before
# it counts as garbage text.
GARBAGE_RUN_MIN_LENGTH = 6

# DEFAULT -- at or above this ratio, repeated/garbage characters downgrade
# otherwise usable text to Partial.
GARBAGE_RATIO_PARTIAL_CEILING = 0.05

# DEFAULT -- at or above this ratio, repeated/garbage characters dominate
# the text enough to mark extraction Failed.
GARBAGE_RATIO_FAILED_CEILING = 0.20


# ---------------------------------------------------------------------------
# Stage 2 — scoring weights
# ---------------------------------------------------------------------------

# DEFAULT — proposed formula, explicitly flagged as "yours to override," not
# a confirmed rubric number. Sums to 90 + up to +/-10 adjustment = 80-100.
REQUIRED_SKILL_WEIGHT = 40
PREFERRED_SKILL_WEIGHT = 15
CGPA_WEIGHT = 15
PRACTICAL_SIGNAL_WEIGHT = 20
CONFLICT_ADJUSTMENT_MAX = 10

# DEFAULT — "soft penalty scaled to the gap" is the only constraint given.
# This is one linear way to satisfy it: lose this many CGPA points of
# score per 1.0 CGPA the candidate sits below the JD minimum, floored at 0.
# CGPA_WEIGHT / 3 means a 3.0-point gap zeroes the whole component.
CGPA_PENALTY_PER_POINT_GAP = CGPA_WEIGHT / 3


# ---------------------------------------------------------------------------
# Confidence tiers
# ---------------------------------------------------------------------------

# DEFAULT — confidence_engine caps by parse quality first. Failed parses
# never reach this table; they never get scored at all.
PARSE_QUALITY_CONFIDENCE_CAP = {
    "Clean": "High",
    "Partial": "Medium",
}

# DEFAULT — share of a candidate's matched skills that must be exact/synonym
# (as opposed to implicit/embedding) to keep the High tier; below this it
# gets capped down a level regardless of what parse quality allowed.
SKILL_CERTAINTY_HIGH_EXACT_RATIO = 0.7
SKILL_CERTAINTY_MEDIUM_EXACT_RATIO = 0.4


# ---------------------------------------------------------------------------
# Slot allocation
# ---------------------------------------------------------------------------

# DEFAULT — "remainder above a floor -> Reserve" per the spec; the floor
# itself isn't given. 50 keeps Reserve a genuine near-miss list rather than
# a dumping ground for everyone who didn't make the cut.
RESERVE_SCORE_FLOOR = 50
