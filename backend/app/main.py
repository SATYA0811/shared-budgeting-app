from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, tempfile
import pdfplumber

from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create tables (dev only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shared Budgeting API")

@app.post("/upload-statement")
async def upload_statement(file: UploadFile = File(...)):
    # Basic validation
    if not file.filename.lower().endswith(('.pdf', '.csv', '.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Save to temp and parse (MVP: inline parsing)
    ext = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    extracted = []
    try:
        if ext == '.pdf':
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    # naive line-by-line extraction — later we'll parse tables & amounts
                    for line in text.splitlines():
                        if line and line.strip():
                            extracted.append(line.strip())
        else:
            extracted.append("CSV/XLS parsing not implemented in this stub")
    except Exception as e:
        return JSONResponse({"error": str(e)})
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return {"filename": file.filename, "lines": extracted[:500]}
