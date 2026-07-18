from __future__ import annotations

import argparse
from pathlib import Path

from engine.field_extractor import extract_fields
from engine.grade_normalizer import normalize_grade
from engine.jd_loader import JDValidationError, load_jd
from engine.matcher import match_candidate
from engine.ocr_fallback import apply_ocr_fallback
from engine.parse_quality import classify_parse_quality
from engine.pdf_parser import needs_ocr, parse_pdf
from engine.reporting import report_to_json
from engine.score_engine import score_candidate
from engine.confidence_engine import assign_confidence
from engine.skill_extractor import extract_skills


def run_pipeline(resume_path: str | Path, jd_path: str | Path):
    jd = load_jd(jd_path)
    resume = parse_pdf(str(resume_path))
    if needs_ocr(resume.word_count):
        resume = apply_ocr_fallback(resume)
    resume = classify_parse_quality(resume)
    resume = extract_fields(resume)
    resume = normalize_grade(resume)
    resume = extract_skills(resume)
    candidate = match_candidate(resume, jd)
    candidate = score_candidate(candidate, jd)
    candidate = assign_confidence(candidate)
    return candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic resume shortlisting engine")
    parser.add_argument("--resume", required=True, help="Path to a resume PDF")
    parser.add_argument("--jd", required=True, help="Path to structured JD JSON")
    args = parser.parse_args(argv)

    try:
        candidate = run_pipeline(args.resume, args.jd)
    except JDValidationError as exc:
        parser.error(str(exc))

    print(report_to_json(candidate))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
