# Shared Budgeting App - Starter Repo

This repository contains a minimal starter for a shared budgeting app:
- Backend: FastAPI (SQLite dev DB) with a basic /upload-statement endpoint that extracts text from PDFs.
- Frontend: Vite + React + Tailwind with a static dashboard mockup.

## Quick start (local, free)
1. Backend:
   - cd backend
   - python -m venv .venv
   - source .venv/bin/activate
   - pip install -r requirements.txt
   - uvicorn app.main:app --reload
   - Visit http://localhost:8000/docs

2. Frontend:
   - cd frontend
   - npm install
   - npm run dev
   - Visit the Vite dev URL (usually http://localhost:5173)

## Next steps I can implement for you (pick one)
- Improve PDF parsing: table extraction (camelot/pdfplumber), OCR fallback, transaction normalization.
- Implement categorization: rule-based + ML classifier starter and labeling UI.
- Add income tracking & goals endpoints + frontend UI.
- Add transactions CRUD and link frontend to backend.
