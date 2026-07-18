"""
engine/ocr_fallback.py

Stage 1, step 2: recover text for resumes that pdf_parser.py couldn't get
enough out of. This module:
  - only runs when pdf_parser.needs_ocr(word_count) says the file qualifies
  - never decides Clean/Partial/Failed (parse_quality.py's job, untouched
    here -- parse_quality and parse_quality_reason are never written)
  - never touches field extraction, skills, or JDs

Mutates and returns the SAME ParsedResume instance it's given (not a copy)
so identity holds for any caller still holding a reference mid-pipeline.
"""

from __future__ import annotations

from typing import List

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised in environments without optional OCR deps
    Image = None
try:
    import pytesseract
except ImportError:  # pragma: no cover - exercised in environments without optional OCR deps
    pytesseract = None

# PyMuPDF >=1.24 exposes both `import pymupdf` (canonical) and the legacy
# `import fitz` (same package) -- mirrors pdf_parser.py's import guard.
try:
    import pymupdf as fitz  # type: ignore
except ImportError:  # pragma: no cover
    import fitz  # type: ignore

from engine.models import ParsedResume
from engine.pdf_parser import needs_ocr

# DEFAULT -- fixed on purpose. Varying DPI between runs would change the
# rasterized image tesseract sees, which can change its output and break
# determinism (Bonus D). Do not make this configurable per-call.
OCR_RENDER_DPI = 300

# DEFAULT -- resumes are assumed English. Revisit if the real dataset
# contains non-English resumes; nothing here auto-detects language.
OCR_LANGUAGE = "eng"


def _rasterize_and_ocr_page(page) -> str:
    # colorspace=fitz.csRGB is PyMuPDF's own default and changes nothing
    # about the output today -- it's made explicit here so the RGB
    # assumption baked into Image.frombytes("RGB", ...) below is an
    # asserted contract, not an inherited default that could silently
    # change on a future PyMuPDF version bump.
    pix = page.get_pixmap(dpi=OCR_RENDER_DPI, colorspace=fitz.csRGB)
    image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return pytesseract.image_to_string(image, lang=OCR_LANGUAGE)


def apply_ocr_fallback(resume: ParsedResume) -> ParsedResume:
    """
    Attempt OCR recovery for a single ParsedResume already produced by
    pdf_parser.py. No-op (returns resume unchanged) if:
      - the word count doesn't clear needs_ocr()'s threshold
      - the file can't be reopened
      - tesseract itself isn't installed
      - OCR runs but doesn't produce more words than were already there

    raw_text / word_count / used_ocr are updated ONLY when OCR output is
    strictly better than what's already on the resume. used_ocr=True means
    "this resume's current text came from OCR," not "OCR was attempted."
    """
    if not needs_ocr(resume.word_count):
        return resume

    if pytesseract is None or Image is None:
        return resume

    try:
        doc = fitz.open(resume.file_path)
    except Exception:
        # Can't reopen the file (e.g. it never opened in pdf_parser.py
        # either). Nothing to recover from; leave resume as-is.
        return resume

    page_texts: List[str] = []
    tesseract_missing = False

    try:
        for page in doc:
            try:
                page_texts.append(_rasterize_and_ocr_page(page))
            except pytesseract.TesseractNotFoundError:
                # Binary isn't installed. Every subsequent page will fail
                # identically -- stop immediately rather than retrying.
                tesseract_missing = True
                break
            except Exception:
                # This page failed OCR for some other reason (corrupt
                # image data, etc.). Don't let one page sink the file --
                # record it as empty and keep going.
                page_texts.append("")
    finally:
        doc.close()

    if tesseract_missing:
        return resume

    ocr_text = "\n".join(page_texts).strip()
    ocr_word_count = len(ocr_text.split()) if ocr_text else 0

    if ocr_word_count > resume.word_count:
        resume.raw_text = ocr_text if ocr_text else None
        resume.word_count = ocr_word_count
        resume.used_ocr = True

    return resume
