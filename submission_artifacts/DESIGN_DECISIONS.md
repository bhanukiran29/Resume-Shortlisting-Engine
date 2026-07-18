# Design Decisions

## 1. Raw PDF handling and OCR fallback

The engine accepts raw resume files and starts with deterministic text extraction in `engine/pdf_parser.py`. If the native text yield is too low, `engine/ocr_fallback.py` attempts OCR and marks the resume as OCR-derived. This keeps the pipeline usable for scanned resumes while preserving transparency: OCR is treated as less reliable and later capped by parse-quality and confidence logic rather than silently mixed with clean native text.

## 2. Parse quality transparency

Every resume is assigned `Clean`, `Partial`, or `Failed` by `engine/parse_quality.py`, and the reason is carried into the final report. Failed parses are not dropped; they still appear in output with an explicit human-review warning. This decision directly avoids silent failure and makes judge evaluation reproducible because the report records whether the parser trusted the extracted text.

## 3. CGPA normalization

Grades are normalized in `engine/grade_normalizer.py` onto a 10-point scale while preserving the raw value exactly as written on the resume. Ambiguous formats are not guessed aggressively; when scale assumptions are needed, they are recorded. This prevents a candidate from being over-scored because of unclear grade formatting and keeps scoring tied to auditable extracted evidence.

## 4. Deterministic matching and scoring

The matcher and scorer use structured job-description inputs, vocabulary-driven skill extraction, and fixed score weights from configuration. The implementation avoids LLM calls, embeddings, random sampling, and time-dependent behavior, so identical inputs produce identical output. Required skills, preferred skills, CGPA, practical signals, missing requirements, confidence, and allocation are reported separately so the final score is explainable instead of opaque.
