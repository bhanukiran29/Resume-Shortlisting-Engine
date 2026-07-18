# Architecture Overview

This document describes the high-level architecture of the **Resume Shortlisting Engine**.

## System Architecture

```text
               +--------------------------------------+
               |               Frontend               |
               |            (React + Vite)            |
               +------------------+-------------------+
                                  |
                                  | API Requests
                                  v
               +------------------+-------------------+
               |               Backend                |
               |          (Python FastAPI)            |
               +------------------+-------------------+
                                  |
               +------------------+-------------------+
               | Services                             |
               | - Parser (pdfplumber, PyMuPDF, OCR)  |
               | - Matcher (rapidfuzz, text analysis) |
               | - Scorer (matching matrices)         |
               +--------------------------------------+
```

## Directory Structure

```text
Resume-Shortlisting-Engine/
├── frontend/             # React + Vite application
├── backend/
│   └── app/              # FastAPI application
│       ├── routes/       # API route handlers (e.g., upload.py)
│       ├── services/     # Core business logic (parser, matcher, scorer)
│       ├── models/       # Pydantic data schemas/objects
│       ├── schemas/      # Request/Response validation schemas
│       └── utils/        # General utilities
├── uploads/              # Saved raw resumes (PDFs, DOCXs)
├── outputs/              # Generated reports/output data
├── docs/                 # Documentation (Design decisions, logs, etc.)
└── requirements.txt      # Python dependencies
```
