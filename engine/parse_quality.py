"""
engine/parse_quality.py

Stage 1, final step: the ONLY module that sets ParsedResume.parse_quality
and ParsedResume.parse_quality_reason. Runs after pdf_parser.py and
optional ocr_fallback.py have already populated raw_text, word_count, and
used_ocr -- and, per the current pipeline contract, BEFORE field_extractor.py
runs. That ordering matters: this module has no name/email/college/grad_year
to look at, so config.CORE_FIELDS_FOR_HIGH_CONFIDENCE is NOT consulted here (see
config.py's Stage 1 classification section for why, and for who should
consume it instead -- flagged, not silently dropped).

This module:
  - never runs OCR (ocr_fallback.py's job, already done by the time this runs)
  - never extracts fields (field_extractor.py's job, hasn't run yet)
  - never scores or matches candidates (Stage 2's job entirely)
  - unconditionally OVERWRITES parse_quality and parse_quality_reason on
    every resume it sees, including ones pdf_parser.py already marked
    FAILED. "Only owner" means this module's judgment is authoritative even
    when it happens to agree with what came before -- nothing downstream
    should ever need to trust pdf_parser.py's or ocr_fallback.py's reason
    string directly.
  - is otherwise READ-ONLY on the resume: raw_text, word_count, used_ocr,
    and every other field are inspected, never modified.

Classification signals and why each is here
---------------------------------------------
1. Text presence (raw_text falsy after Stage 1) -> FAILED. This is the
   FINAL failed determination, not pdf_parser.py's provisional one -- OCR
   has already had its shot by the time this module runs.

2. Garbage-character ratio (config.GARBAGE_RUN_MIN_LENGTH /
   GARBAGE_RATIO_PARTIAL_CEILING / GARBAGE_RATIO_FAILED_CEILING). Catches
   the failure mode word_count alone misses: a scanned page that OCRs into
   long runs of misread identical characters. If those runs are
   space-separated ("x x x x..."), word_count looks fine while the text is
   worthless -- garbage ratio is checked independently of word_count for
   exactly this reason, and can downgrade a resume word_count alone would
   have called Clean.

3. word_count vs the EXISTING thresholds -- no new numbers invented here.
   OCR_WORD_COUNT_THRESHOLD (50) is reused as the final usability floor:
   if a resume is still below it after OCR had its chance, "usable" isn't
   coming. CLEAN_MIN_WORD_COUNT (150) is reused as the Clean floor, exactly
   as config.py already documented its purpose.

4. used_ocr as a hard cap, not a scored signal. OCR-derived text is
   structurally less trustworthy than native extraction regardless of
   volume -- misreads are frequent and undetectable at this layer. A
   resume that only cleared word_count because OCR filled it in is capped
   at PARTIAL even if every other signal says Clean.

Deliberately NOT implemented: a dictionary/vocabulary check for "real
words" (needs a wordlist dependency and stops being a cheap deterministic
rule) and multi-character repeated-pattern detection beyond single-char
runs (covers the actual bad-OCR failure mode; chasing something like
"ababab" repeats is diminishing returns for real resume text and adds
another number to tune blind).

Decision order (first match wins)
----------------------------------
1. raw_text empty/None                                    -> FAILED
2. garbage_ratio >= GARBAGE_RATIO_FAILED_CEILING            -> FAILED
3. word_count < OCR_WORD_COUNT_THRESHOLD                    -> FAILED
4. word_count < CLEAN_MIN_WORD_COUNT
   OR garbage_ratio >= GARBAGE_RATIO_PARTIAL_CEILING
   OR used_ocr is True                                       -> PARTIAL
5. otherwise                                                -> CLEAN

Reason-string handling
-----------------------
parse_quality_reason is fully owned and rewritten here, but the upstream
reason string (pdf_parser.py's "Could not open file: ..." or "Extraction
failed mid-document: ...") is the only place that distinguishes *why*
raw_text ended up empty -- this module can't tell "file wouldn't open"
apart from "opened fine, zero usable text" by looking at raw_text alone.
Rather than destroy that diagnostic on overwrite, the final reason APPENDS
the prior stage's note (if any) as a bracketed origin tag.

Edge cases considered
-----------------------
- A legitimately short but real resume (a new grad with a sparse two-line
  resume landing at, say, 60 words) reads identically to "thin/garbage OCR
  output" under this module -- both trip the same FAILED-if-below-
  usability-floor rule. That's a real false-positive risk inherent to a
  threshold-only design; it's the same risk config.py already flagged for
  OCR_WORD_COUNT_THRESHOLD and CLEAN_MIN_WORD_COUNT, not a new one
  introduced here.
- A resume where OCR recovered word_count comfortably above
  CLEAN_MIN_WORD_COUNT still caps at PARTIAL -- by design, not a bug.
- A resume already FAILED at the pdf_parser.py stage (open failure,
  mid-document exception) has raw_text=None either way, so it falls
  through the same rule-1 FAILED path here -- re-affirmed, not
  re-diagnosed, with the original diagnostic preserved via the origin tag.
- word_count is read as-is from the resume (computed identically by
  pdf_parser.py and ocr_fallback.py via whitespace-split) rather than
  recomputed here, to avoid two different "word count" definitions
  disagreeing with each other on the same object.
"""

from __future__ import annotations

import re

from config import (
    CLEAN_MIN_WORD_COUNT,
    GARBAGE_RATIO_FAILED_CEILING,
    GARBAGE_RATIO_PARTIAL_CEILING,
    GARBAGE_RUN_MIN_LENGTH,
    OCR_WORD_COUNT_THRESHOLD,
)
from engine.models import ParsedResume, ParseQuality

# Matches any single non-whitespace character repeated at least
# GARBAGE_RUN_MIN_LENGTH times in a row.
_GARBAGE_RUN_PATTERN = re.compile(r"(\S)\1{%d,}" % (GARBAGE_RUN_MIN_LENGTH - 1))


def _garbage_char_ratio(text: str) -> float:
    """
    Fraction of `text`'s characters that fall inside a run of one repeated
    non-whitespace character at least GARBAGE_RUN_MIN_LENGTH long. Checked
    independently of word_count -- see module docstring for why.
    """
    if not text:
        return 0.0
    garbage_chars = sum(
        len(match.group(0)) for match in _GARBAGE_RUN_PATTERN.finditer(text)
    )
    return garbage_chars / len(text)


def _origin_tag(resume: ParsedResume) -> str:
    """
    Preserve whatever diagnostic pdf_parser.py / ocr_fallback.py already
    left behind -- it's the only record of *why* raw_text ended up the way
    it did (open failure vs. mid-doc exception vs. genuinely empty).
    """
    prior = resume.parse_quality_reason
    return f" [prior stage: {prior}]" if prior else ""


def _capitalize_first(text: str) -> str:
    """
    Capitalize only the first character, unlike str.capitalize() which also
    lowercases everything else -- would mangle things like "OCR-derived".
    """
    if not text:
        return text
    return text[0].upper() + text[1:]


def classify_parse_quality(resume: ParsedResume) -> ParsedResume:
    """
    Overwrites resume.parse_quality and resume.parse_quality_reason in
    place and returns the same object. Unconditional: runs this logic for
    every resume, including ones already marked FAILED upstream.
    """
    origin = _origin_tag(resume)
    text = resume.raw_text
    word_count = resume.word_count

    if not text:
        resume.parse_quality = ParseQuality.FAILED
        resume.parse_quality_reason = (
            "No usable text present after extraction and OCR." + origin
        )
        return resume

    garbage_ratio = _garbage_char_ratio(text)

    if garbage_ratio >= GARBAGE_RATIO_FAILED_CEILING:
        resume.parse_quality = ParseQuality.FAILED
        resume.parse_quality_reason = (
            f"Text is dominated by repeated/garbage characters "
            f"(ratio {garbage_ratio:.2f} >= {GARBAGE_RATIO_FAILED_CEILING}), "
            f"not usable despite {word_count} words." + origin
        )
        return resume

    if word_count < OCR_WORD_COUNT_THRESHOLD:
        resume.parse_quality = ParseQuality.FAILED
        resume.parse_quality_reason = (
            f"Word yield ({word_count}) remained below the usable-text "
            f"floor ({OCR_WORD_COUNT_THRESHOLD}) even after OCR." + origin
        )
        return resume

    partial_reasons = []
    if word_count < CLEAN_MIN_WORD_COUNT:
        partial_reasons.append(
            f"word yield ({word_count}) is below the Clean floor ({CLEAN_MIN_WORD_COUNT})"
        )
    if garbage_ratio >= GARBAGE_RATIO_PARTIAL_CEILING:
        partial_reasons.append(f"garbage-character ratio ({garbage_ratio:.2f}) is elevated")
    if resume.used_ocr:
        partial_reasons.append("text is OCR-derived, not natively extracted")

    if partial_reasons:
        resume.parse_quality = ParseQuality.PARTIAL
        resume.parse_quality_reason = (
            _capitalize_first("; ".join(partial_reasons)) + "." + origin
        )
        return resume

    resume.parse_quality = ParseQuality.CLEAN
    resume.parse_quality_reason = (
        f"Word yield ({word_count}) meets the Clean floor, text is "
        f"natively extracted, garbage-character ratio ({garbage_ratio:.2f}) "
        f"is within tolerance." + origin
    )
    return resume
