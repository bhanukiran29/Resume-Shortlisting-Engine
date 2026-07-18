from pathlib import Path

from docx import Document

from config import BASE_DIR
from engine.confidence_engine import assign_confidence
from engine.field_extractor import extract_fields
from engine.grade_normalizer import normalize_grade
from engine.jd_loader import JDValidationError, load_jd
from engine.matcher import match_candidate
from engine.models import ParsedResume, ParseQuality
from engine.ocr_fallback import apply_ocr_fallback
from engine.parse_quality import classify_parse_quality
from engine.pdf_parser import needs_ocr, parse_pdf
from engine.score_engine import score_candidate
from engine.skill_extractor import extract_skills


DEFAULT_UPLOAD_JD_PATH = BASE_DIR / "data" / "jds" / "default.json"

class ParserService:
    def __init__(self):
        pass

    def parse_resume(self, file_path: str) -> dict:
        """
        Parses resume file and extracts deterministic profile fields.
        """
        resume = self._extract_resume(file_path)
        if needs_ocr(resume.word_count) and Path(file_path).suffix.lower() == ".pdf":
            resume = apply_ocr_fallback(resume)
        resume = classify_parse_quality(resume)
        resume = extract_fields(resume)
        resume = normalize_grade(resume)
        resume = extract_skills(resume)
        scoring_data = self._score_resume(resume)

        parsed_data = {
            "filename": resume.file_name,
            "extracted_text": resume.raw_text or "",
            "parse_quality": resume.parse_quality.value,
            "parse_quality_reason": resume.parse_quality_reason,
            "word_count": resume.word_count,
            "used_ocr": resume.used_ocr,
            "is_multi_column": resume.is_multi_column,
            "name": resume.name,
            "email": resume.email,
            "phone": resume.phone,
            "college": resume.college,
            "degree": resume.degree,
            "grad_year": resume.grad_year,
            "raw_cgpa": resume.raw_cgpa,
            "normalized_cgpa": resume.normalized_cgpa,
            "skills": [skill.name for skill in resume.skills],
            "skill_details": [
                {"name": skill.name, "match_type": skill.match_type.value}
                for skill in resume.skills
            ],
            "experience_years": 0.0,
            "education": [
                value for value in (resume.college, resume.degree)
                if value is not None
            ],
        }
        parsed_data.update(scoring_data)
        return parsed_data

    def parse_job_description(self, text: str) -> dict:
        """
        Parses job description text.
        Currently a stub.
        """
        return {
            "skills_required": ["Stub Skill A"],
            "minimum_experience": 0.0,
            "parsed_title": "Software Engineer"
        }

    def _extract_resume(self, file_path: str) -> ParsedResume:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return parse_pdf(str(path))

        if suffix == ".docx":
            return self._parse_docx(path)

        if suffix == ".txt":
            return self._parse_txt(path)

        return ParsedResume(
            file_path=str(path),
            parse_quality=ParseQuality.FAILED,
            parse_quality_reason=f"Unsupported resume format for parser service: {suffix}",
        )

    def _parse_docx(self, path: Path) -> ParsedResume:
        try:
            document = Document(str(path))
            raw_text = "\n".join(
                paragraph.text for paragraph in document.paragraphs
                if paragraph.text.strip()
            ).strip()
        except Exception as exc:  # noqa: BLE001 - one bad resume must not kill a batch
            return ParsedResume(
                file_path=str(path),
                parse_quality=ParseQuality.FAILED,
                parse_quality_reason=f"Could not open DOCX file: {exc}",
            )

        return self._resume_from_text(path, raw_text, "DOCX text extracted successfully.")

    def _parse_txt(self, path: Path) -> ParsedResume:
        try:
            raw_text = path.read_text(encoding="utf-8", errors="replace").strip()
        except Exception as exc:  # noqa: BLE001 - one bad resume must not kill a batch
            return ParsedResume(
                file_path=str(path),
                parse_quality=ParseQuality.FAILED,
                parse_quality_reason=f"Could not open TXT file: {exc}",
            )

        return self._resume_from_text(path, raw_text, "TXT text extracted successfully.")

    def _resume_from_text(self, path: Path, raw_text: str, reason: str) -> ParsedResume:
        if not raw_text:
            return ParsedResume(
                file_path=str(path),
                parse_quality=ParseQuality.FAILED,
                parse_quality_reason="No extractable text found.",
            )

        return ParsedResume(
            file_path=str(path),
            parse_quality=ParseQuality.PARTIAL,
            parse_quality_reason=reason,
            raw_text=raw_text,
            word_count=len(raw_text.split()),
            used_ocr=False,
            is_multi_column=False,
        )

    def _score_resume(self, resume: ParsedResume) -> dict:
        if not DEFAULT_UPLOAD_JD_PATH.exists():
            return {
                "scoring_available": False,
                "scoring_reason": f"Default JD not found: {DEFAULT_UPLOAD_JD_PATH}",
            }

        try:
            jd = load_jd(DEFAULT_UPLOAD_JD_PATH)
        except JDValidationError as exc:
            return {
                "scoring_available": False,
                "scoring_reason": str(exc),
            }

        candidate = match_candidate(resume, jd)
        candidate = score_candidate(candidate, jd)
        candidate = assign_confidence(candidate)
        breakdown = candidate.score_breakdown

        return {
            "scoring_available": True,
            "job_id": candidate.job_id,
            "job_title": jd.title,
            "score": candidate.total_score,
            "overall_score": candidate.total_score,
            "confidence": candidate.confidence.value if candidate.confidence else None,
            "allocation": candidate.allocation.value,
            "score_breakdown": {
                "required_skill_score": breakdown.required_skill_score,
                "preferred_skill_score": breakdown.preferred_skill_score,
                "cgpa_score": breakdown.cgpa_score,
                "practical_signal_score": breakdown.practical_signal_score,
                "conflict_adjustment": breakdown.conflict_adjustment,
            } if breakdown else None,
            "matched_required": [
                {"name": skill.name, "match_type": skill.match_type.value}
                for skill in candidate.matched_required
            ],
            "matched_preferred": [
                {"name": skill.name, "match_type": skill.match_type.value}
                for skill in candidate.matched_preferred
            ],
            "missing_required": list(candidate.missing_required),
        }
