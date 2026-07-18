"""
engine/pdf_parser.py

Stage 1, step 1: PDF file -> raw text + layout metadata. This module ONLY
extracts. It does not:
  - run OCR (that's ocr_fallback.py)
  - decide Clean/Partial/Failed (that's parse_quality.py)
  - pull name/email/college/etc (that's field_extractor.py)
  - touch skills or JDs at all

It returns a ParsedResume, because that's the shared contract every stage
passes forward. Two consequences worth being explicit about:

1. parse_quality is a REQUIRED field on ParsedResume with no default, but
   this module is not allowed to classify Clean vs Partial (that needs
   field-completeness data this module never sees). So:
     - if there is truly no extractable text, we set FAILED. That's a
       fact ("is there text or not"), not a judgment call, even though
       it's provisional -- ocr_fallback.py may still recover it, at which
       point parse_quality.py makes the real call.
     - otherwise we set PARTIAL as an explicit placeholder and say so in
       parse_quality_reason. parse_quality.py MUST overwrite this before
       the value is trusted anywhere downstream.

2. "page count" was requested as metadata but ParsedResume has no field
   for it. It's used internally below for the column heuristic and then
   dropped. If you want it persisted, that's a models.py change, not one
   this module can smuggle in.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

# PyMuPDF >=1.24 exposes both `import pymupdf` (canonical) and the legacy
# `import fitz` (same package). Try the canonical name first; fall back so
# this doesn't hard-fail on an older pinned version.
try:
    import pymupdf as fitz  # type: ignore
except ImportError:  # pragma: no cover
    import fitz  # type: ignore

from config import OCR_WORD_COUNT_THRESHOLD
from engine.models import ParsedResume, ParseQuality

# Blocks wider than this fraction of the page are treated as full-width
# elements (headers, horizontal rules, footer lines) and excluded from the
# column heuristic -- a wide block isn't evidence of a column layout.
_FULL_WIDTH_BLOCK_RATIO = 0.6

# Minimum number of narrow blocks required on EACH side of the page
# midline before we call a page multi-column. Guards against a single
# stray sidebar date or bullet producing a false positive.
_MIN_BLOCKS_PER_SIDE = 3


def needs_ocr(word_count: int) -> bool:
    """
    Pure signal, not an action: True when extracted word yield is below
    Bonus B's own trigger point (config.OCR_WORD_COUNT_THRESHOLD). This
    module does not act on it -- pipeline.py reads this to decide whether
    to hand the file to ocr_fallback.py.
    """
    return word_count < OCR_WORD_COUNT_THRESHOLD


def _extract_page_text_and_blocks(page) -> tuple[str, Sequence]:
    text = page.get_text("text")
    # (x0, y0, x1, y1, text, block_no, block_type)
    blocks = page.get_text("blocks")
    return text, blocks


def _is_multi_column_page(blocks: Sequence, page_width: float) -> bool:
    if page_width <= 0 or not blocks:
        return False

    midline = page_width / 2
    left_count = 0
    right_count = 0

    for block in blocks:
        x0, y0, x1, y1 = block[0], block[1], block[2], block[3]
        text = block[4] if len(block) > 4 else ""
        if not text or not text.strip():
            continue

        block_width = x1 - x0
        if block_width > page_width * _FULL_WIDTH_BLOCK_RATIO:
            continue  # full-width element, not column evidence

        center_x = (x0 + x1) / 2
        if center_x < midline:
            left_count += 1
        else:
            right_count += 1

    return left_count >= _MIN_BLOCKS_PER_SIDE and right_count >= _MIN_BLOCKS_PER_SIDE


def parse_pdf(file_path: str) -> ParsedResume:
    """
    Extract text + layout metadata from a single PDF. Always returns a
    ParsedResume -- never raises for a bad/corrupt file, since one bad PDF
    must not kill a batch run (per pipeline.py's per-file try/except
    contract). used_ocr is always False here; that flag belongs to
    ocr_fallback.py.
    """
    path = Path(file_path)

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        # Couldn't even open the file. There is no text to have an opinion
        # about -- this is a genuine FAILED, not a placeholder.
        return ParsedResume(
            file_path=str(path),
            parse_quality=ParseQuality.FAILED,
            parse_quality_reason=f"Could not open file: {exc}",
        )

    page_texts: List[str] = []
    multi_column_pages = 0
    extraction_error: Exception | None = None

    try:
        for page in doc:
            text, blocks = _extract_page_text_and_blocks(page)
            page_texts.append(text)
            if _is_multi_column_page(blocks, page.rect.width):
                multi_column_pages += 1
    except Exception as exc:  # noqa: BLE001 - deliberately broad, see below
        # Covers encrypted/truncated/malformed PDFs that fitz.open() didn't
        # reject up front but choke on when a page is actually read. Without
        # this, one bad file mid-batch raises out of parse_pdf and breaks
        # the "never crashes the batch" contract from the module docstring.
        extraction_error = exc
    finally:
        doc.close()

    if extraction_error is not None:
        return ParsedResume(
            file_path=str(path),
            parse_quality=ParseQuality.FAILED,
            parse_quality_reason=f"Extraction failed mid-document: {extraction_error}",
        )

    raw_text = "\n".join(page_texts).strip()
    word_count = len(raw_text.split()) if raw_text else 0
    is_multi_column = multi_column_pages > 0

    if not raw_text:
        parse_quality = ParseQuality.FAILED
        parse_quality_reason = "No extractable text found (pre-OCR)."
    else:
        # TODO(parse_quality.py): this PARTIAL is a provisional placeholder,
        # not a real classification -- pdf_parser.py has no field-completeness
        # data to base Clean/Partial on. parse_quality.py MUST overwrite this
        # value (and parse_quality_reason) before any downstream module
        # (scoring, reporting) is allowed to trust it. If you're reading a
        # parse_quality_reason that still says "Provisional" at report time,
        # that's a pipeline wiring bug, not a valid Partial resume.
        parse_quality = ParseQuality.PARTIAL
        parse_quality_reason = (
            "Provisional value from pdf_parser.py -- awaiting "
            "field-completeness check from parse_quality.py."
        )

    return ParsedResume(
        file_path=str(path),
        parse_quality=parse_quality,
        parse_quality_reason=parse_quality_reason,
        raw_text=raw_text if raw_text else None,
        word_count=word_count,
        used_ocr=False,
        is_multi_column=is_multi_column,
    )
