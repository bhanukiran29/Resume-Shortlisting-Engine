# Design Decisions

This document outlines key technical and architectural design decisions made during development.

## 1. Replacing Express with FastAPI (Python)
- **Context**: The hackathon template came with an Express (Node.js) backend.
- **Decision**: Fully replaced Express with FastAPI.
- **Rationale**: Python is the industry-standard language for text processing, NLP, and document parsing. It provides native, robust libraries (such as `pdfplumber`, `PyMuPDF`, and `pytesseract`) that are much easier to integrate directly into a Python API than spawning subprocesses from a Node server. FastAPI also generates automatic interactive Swagger/OpenAPI documentation.

## 2. Decoupling the Pipeline (Parser, Matcher, Scorer)
- **Context**: Resume shortlisting involves multiple distinct operations.
- **Decision**: Separated the backend business logic into three distinct services:
  1. **Parser**: Responsible for raw text extraction and metadata identification.
  2. **Matcher**: Compares parsed data against a specified job description structure.
  3. **Scorer**: Assigns scores and priorities based on match quality.
- **Rationale**: This division enables easier unit testing, modular extensions (e.g. changing parsing engines without touching matching logic), and scaling.
