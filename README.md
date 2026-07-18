# Resume Shortlisting Engine

## Overview
An AI-powered document parsing, matching, and scoring system designed to help recruiters filter and shortlist resumes against job descriptions. This project features a modular React + Vite frontend and a Python FastAPI backend.

---

## Features

- **✅ File Upload**: Upload multiple resume formats (PDF, DOCX, TXT).
- **✅ Document Parser (Python)**: Extract text and parse candidates using powerful Python libraries.
- **✅ Match & Scorer**: Match extracted candidate profiles with target job requirements using text-matching matrices.
- **✅ FastAPI Backend**: Modern, high-performance API featuring automatic OpenAPI docs.
- **✅ React Frontend**: Decoupled component architecture for real-time visualization of candidate scores and ranks.
- **✅ Environment Variable Support**: Scoped configuration files for frontend and backend.

---

## Architecture

```text
React (Vite Frontend)
         │
    HTTP Requests
         │
         ▼
FastAPI (Python Backend)
         ├── Routes (e.g., upload.py)
         ├── Models (Pydantic models)
         ├── Schemas (Request/response shapes)
         └── Services (Business Logic)
                 ├── Parser (pdfplumber, PyMuPDF, OCR)
                 ├── Matcher (Text similarity)
                 └── Scorer (Scoring matrix)
```

---

## Folder Structure

```text
Resume-Shortlisting-Engine/
├── frontend/             # React + Vite frontend application
├── backend/
│   └── app/              # FastAPI backend application
│       ├── routes/       # API router endpoints
│       ├── services/     # Business logic layer (parser, matcher, scorer)
│       ├── models/       # Pydantic data schemas/objects
│       ├── schemas/      # Validation schemas
│       └── utils/        # General utilities
├── uploads/              # Saved raw resumes (PDFs, DOCXs, TXTs)
├── outputs/              # Saved comparison reports
├── logs/                 # System logs
├── docs/                 # Documentation and logs
├── README.md             # Main repository documentation
└── requirements.txt      # Python dependencies
```

---

## Installation & Setup

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- Pip (Python Package Installer)

### Clone the Repository
```bash
git clone <repo-url>
cd Resume-Shortlisting-Engine
```

### Backend Dependency Setup
1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template:
   ```bash
   cp .env.example .env
   ```

### Frontend Dependency Setup
1. Install node dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Copy environment template:
   ```bash
   cp .env.example .env  # Configure VITE_API_URL to point to http://localhost:8000
   ```

---

## Running the Applications

### Start the Backend Server
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```
Interactive API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Start the Frontend Dev Server
```bash
cd frontend
npm run dev
```
The React frontend will be running on [http://localhost:5173](http://localhost:5173).

---

## License
MIT License.