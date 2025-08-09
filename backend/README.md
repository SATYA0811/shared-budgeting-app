# Backend (FastAPI) - Starter

## Run locally (free)

1. Install Python 3.11+ and Tesseract OCR (required for pytesseract).
   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - Mac (Homebrew): `brew install tesseract`

2. Create a virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Visit http://localhost:8000/docs for the OpenAPI UI.

Notes:
- This starter uses SQLite (dev.db) for zero-config development.
- The `/upload-statement` endpoint accepts PDF and returns extracted text lines (naive).
- Next steps: implement CSV parsing, table extraction, normalization, and categorization.
