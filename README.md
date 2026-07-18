# Resume Shortlisting Engine

Deterministic resume parsing, matching, scoring, confidence, and reporting for shortlisting candidates against a structured job description.

The core engine is intentionally rule-based. It does not use LLMs, embeddings, random behavior, or time-dependent scoring.

## Architecture

```text
Resume PDF/DOCX
    |
    v
pdf_parser.py
    |
    v
ocr_fallback.py          # optional, only for low text yield
    |
    v
parse_quality.py
    |
    v
field_extractor.py
grade_normalizer.py
skill_extractor.py
    |
    v
jd_loader.py + matcher.py
    |
    v
score_engine.py
confidence_engine.py
    |
    v
reporting.py / cli.py
```

Shared data contracts live in `engine/models.py`. Tunable paths, thresholds, weights, and confidence caps live in `config.py`.

## Installation

Python 3.9+ is recommended.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

OCR fallback requires the Tesseract binary to be installed on the system. If `pytesseract` or `Pillow` are unavailable, non-OCR parsing still runs and OCR fallback becomes a no-op.

## Usage

Run one resume against one structured JD JSON:

```bash
python cli.py --resume path\to\resume.pdf --jd path\to\jd.json
```

Example JD shape:

```json
{
  "job_id": "backend",
  "title": "Backend Engineer",
  "slot_count": 1,
  "required_skills": ["Python", "SQL"],
  "preferred_skills": ["Docker", "Git"],
  "min_cgpa": 8.0
}
```

The CLI prints a JSON report containing parse quality, extracted fields, normalized CGPA, skills, matched/missing requirements, score breakdown, confidence, warnings, and explanation fields.

## Testing

```bash
python -m unittest discover
python -m py_compile cli.py config.py engine\models.py engine\pdf_parser.py engine\ocr_fallback.py engine\parse_quality.py engine\field_extractor.py engine\grade_normalizer.py engine\skill_extractor.py engine\jd_loader.py engine\matcher.py engine\score_engine.py engine\confidence_engine.py engine\reporting.py
python -m compileall cli.py config.py engine tests
```

## Requirements

Runtime dependencies are listed in `requirements.txt`, including:

- `PyMuPDF` for PDF/DOCX text extraction through the current parser path
- `pytesseract` and `Pillow` for optional OCR fallback
- `python-docx` for document tooling compatibility
- `fastapi`, `uvicorn`, and related backend dependencies

## Repository Notes

Generated outputs, validation artifacts, Python caches, virtual environments, frontend build outputs, and local environment files are ignored by git.

`outputs/e2e_check/` is currently treated as a local validation/example artifact because `outputs/` is ignored. Move it outside `outputs/` or add a `.gitignore` exception if it should be committed as a public fixture.

## License

MIT License.
