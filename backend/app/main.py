from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import os, tempfile, re
import pdfplumber

from .database import get_db, create_tables
from .auth import authenticate_user, create_access_token, get_current_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from .schemas import UserRegistration, UserLogin, Token, UserResponse, HouseholdCreate, HouseholdResponse
from .models import User, Household, HouseholdUser, Role, File, FileStatus, Transaction

# Create tables on startup
create_tables()

app = FastAPI(title="Shared Budgeting API")

# Debug endpoint
@app.get("/debug")
def debug_endpoint():
    """Debug endpoint to check server status."""
    return {"status": "ok", "message": "Server is running"}

@app.get("/debug-auth")
def debug_auth(current_user: User = Depends(get_current_user)):
    """Debug endpoint to test authentication."""
    try:
        return {"status": "ok", "user_id": current_user.id, "message": "Auth working"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Authentication endpoints
@app.post("/register", response_model=UserResponse)
def register(user_data: UserRegistration, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

# Household management
@app.post("/households", response_model=HouseholdResponse)
def create_household(
    household_data: HouseholdCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new household."""
    # Create household
    new_household = Household(name=household_data.name)
    db.add(new_household)
    db.commit()
    db.refresh(new_household)
    
    # Add creator as owner
    household_user = HouseholdUser(
        household_id=new_household.id,
        user_id=current_user.id,
        role=Role.owner
    )
    db.add(household_user)
    db.commit()
    
    return {
        "id": new_household.id,
        "name": new_household.name,
        "created_at": new_household.created_at
    }

@app.get("/households")
def get_user_households(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get households the user belongs to."""
    households = db.query(Household).join(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": h.id,
            "name": h.name,
            "created_at": h.created_at
        }
        for h in households
    ]

@app.post("/upload-statement")
async def upload_statement(
    file: UploadFile = File(...),
    household_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse bank statement file."""
    # Basic validation
    if not file.filename.lower().endswith(('.pdf', '.csv', '.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Validate household access if provided
    if household_id:
        household_user = db.query(HouseholdUser).filter(
            HouseholdUser.household_id == household_id,
            HouseholdUser.user_id == current_user.id
        ).first()
        if not household_user:
            raise HTTPException(status_code=403, detail="No access to this household")
    
    # Create file record
    file_record = File(
        household_id=household_id,
        user_id=current_user.id,
        s3_key=file.filename,  # For now, just store filename
        status=FileStatus.uploaded
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    
    # Save to temp and parse (MVP: inline parsing)
    ext = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
    
    # Update status to parsing
    file_record.status = FileStatus.parsing
    db.commit()
    
    try:
        parsed_data = await parse_file(tmp_path, ext, file_record.id, db)
        
        # Update status to parsed
        file_record.status = FileStatus.parsed
        db.commit()
        
        return {
            "file_id": file_record.id,
            "filename": file.filename,
            "status": "parsed",
            "transactions_found": len(parsed_data.get("transactions", []))
        }
        
    except Exception as e:
        # Update status to error
        file_record.status = FileStatus.error
        db.commit()
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
    
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


# File and transaction viewing endpoints
@app.get("/files")
def get_uploaded_files(
    household_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get uploaded files for user or household."""
    query = db.query(File).filter(File.user_id == current_user.id)
    
    if household_id:
        # Verify access to household
        household_user = db.query(HouseholdUser).filter(
            HouseholdUser.household_id == household_id,
            HouseholdUser.user_id == current_user.id
        ).first()
        if not household_user:
            raise HTTPException(status_code=403, detail="No access to this household")
        
        query = query.filter(File.household_id == household_id)
    
    files = query.order_by(File.id.desc()).all()
    
    return [
        {
            "id": f.id,
            "filename": f.s3_key,
            "status": f.status.value,
            "household_id": f.household_id,
            "created_at": f.id  # Using id as proxy for creation time
        }
        for f in files
    ]


@app.get("/files/{file_id}/transactions")
def get_file_transactions(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions from a specific uploaded file."""
    # Verify file access
    file_record = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id
    ).first()
    
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    transactions = db.query(Transaction).filter(
        Transaction.source_file_id == file_id
    ).order_by(Transaction.date.desc()).all()
    
    return [
        {
            "id": t.id,
            "date": t.date.isoformat(),
            "description": t.description,
            "amount": float(t.amount),
            "category_id": t.category_id
        }
        for t in transactions
    ]


# Enhanced file parsing functions
async def parse_file(file_path: str, ext: str, file_id: int, db: Session):
    """Enhanced file parsing with better extraction."""
    if ext == '.pdf':
        return await parse_pdf_file(file_path, file_id, db)
    elif ext in ['.csv', '.xls', '.xlsx']:
        return await parse_spreadsheet_file(file_path, ext, file_id, db)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


async def parse_pdf_file(file_path: str, file_id: int, db: Session):
    """Enhanced PDF parsing with table extraction."""
    import re
    from decimal import Decimal
    
    transactions = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Try table extraction first
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        transactions.extend(parse_table_rows(table, file_id))
                
                # Fallback to text extraction
                text = page.extract_text() or ""
                if text and not tables:
                    transactions.extend(parse_text_lines(text, file_id))
    
    except Exception as e:
        # OCR fallback if PDF parsing fails
        try:
            import pytesseract
            from PIL import Image
            
            # Convert PDF to image and OCR
            transactions = await ocr_fallback(file_path, file_id)
        except Exception as ocr_error:
            raise Exception(f"PDF parsing failed: {e}, OCR fallback failed: {ocr_error}")
    
    # Store parsed transactions in database
    await store_transactions(transactions, file_id, db)
    
    return {"transactions": transactions}


def parse_table_rows(table, file_id: int):
    """Parse table rows to extract transaction data."""
    transactions = []
    
    for row in table:
        if not row or len(row) < 3:
            continue
            
        try:
            # Common bank statement formats
            # [Date, Description, Amount] or [Date, Description, Debit, Credit]
            transaction = parse_transaction_row(row, file_id)
            if transaction:
                transactions.append(transaction)
        except Exception:
            continue
    
    return transactions


def parse_text_lines(text: str, file_id: int):
    """Parse text lines for transaction patterns."""
    import re
    from datetime import datetime
    
    transactions = []
    lines = text.split('\n')
    
    # Common patterns for dates and amounts
    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
    amount_pattern = r'\$?([+-]?\d{1,3}(?:,\d{3})*\.?\d{0,2})'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for date patterns
        date_matches = re.findall(date_pattern, line)
        amount_matches = re.findall(amount_pattern, line)
        
        if date_matches and amount_matches:
            try:
                transaction = {
                    "date": date_matches[0],
                    "description": clean_description(line, date_matches[0], amount_matches[0]),
                    "amount": amount_matches[-1],  # Usually last amount is the transaction amount
                    "source_file_id": file_id
                }
                transactions.append(transaction)
            except Exception:
                continue
    
    return transactions


def parse_transaction_row(row, file_id: int):
    """Parse a single table row into transaction data."""
    from datetime import datetime
    import re
    
    if len(row) < 3:
        return None
    
    try:
        # Assume format: [Date, Description, Amount] or [Date, Description, Debit, Credit]
        date_str = str(row[0]).strip() if row[0] else ""
        description = str(row[1]).strip() if row[1] else ""
        
        # Handle debit/credit columns
        if len(row) >= 4:
            debit = str(row[2]).strip() if row[2] else ""
            credit = str(row[3]).strip() if row[3] else ""
            amount = credit if credit and credit != "" else f"-{debit}" if debit else ""
        else:
            amount = str(row[2]).strip() if row[2] else ""
        
        # Validate date format
        if not re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', date_str):
            return None
        
        # Clean amount
        amount_clean = re.sub(r'[^\d.-]', '', amount)
        if not amount_clean:
            return None
        
        return {
            "date": date_str,
            "description": description,
            "amount": amount_clean,
            "source_file_id": file_id
        }
    
    except Exception:
        return None


def clean_description(line: str, date: str, amount: str) -> str:
    """Clean transaction description by removing date and amount."""
    # Remove date and amount from the line to get clean description
    clean_line = line.replace(date, "").replace(amount, "")
    clean_line = re.sub(r'\s+', ' ', clean_line).strip()
    return clean_line[:200]  # Limit description length


async def parse_spreadsheet_file(file_path: str, ext: str, file_id: int, db: Session):
    """Parse CSV/Excel files."""
    transactions = []
    
    try:
        if ext == '.csv':
            import csv
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, None)
                for row in reader:
                    transaction = parse_csv_row(row, headers, file_id)
                    if transaction:
                        transactions.append(transaction)
        
        else:  # .xls, .xlsx
            import pandas as pd
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                transaction = parse_excel_row(row, file_id)
                if transaction:
                    transactions.append(transaction)
    
    except Exception as e:
        raise Exception(f"Spreadsheet parsing failed: {e}")
    
    # Store parsed transactions in database
    await store_transactions(transactions, file_id, db)
    
    return {"transactions": transactions}


def parse_csv_row(row, headers, file_id: int):
    """Parse CSV row into transaction."""
    if len(row) < 3:
        return None
    
    # Try to identify date, description, amount columns
    # This is a simplified version - in production, you'd want more sophisticated column detection
    return {
        "date": row[0] if len(row) > 0 else "",
        "description": row[1] if len(row) > 1 else "",
        "amount": row[2] if len(row) > 2 else "",
        "source_file_id": file_id
    }


def parse_excel_row(row, file_id: int):
    """Parse Excel row into transaction."""
    try:
        return {
            "date": str(row.iloc[0]) if len(row) > 0 else "",
            "description": str(row.iloc[1]) if len(row) > 1 else "",
            "amount": str(row.iloc[2]) if len(row) > 2 else "",
            "source_file_id": file_id
        }
    except Exception:
        return None


async def ocr_fallback(file_path: str, file_id: int):
    """OCR fallback for difficult PDFs."""
    # This is a placeholder - implementing full OCR is complex
    # For now, return empty transactions
    return []


async def store_transactions(transactions, file_id: int, db: Session):
    """Store parsed transactions in the database."""
    from .models import Transaction
    from datetime import datetime
    from decimal import Decimal
    import re
    
    for trans_data in transactions:
        try:
            # Parse date
            date_str = trans_data.get("date", "")
            try:
                # Try different date formats
                for date_format in ["%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%Y-%m-%d"]:
                    try:
                        date_obj = datetime.strptime(date_str, date_format)
                        break
                    except ValueError:
                        continue
                else:
                    date_obj = datetime.now()  # Fallback to current date
            except Exception:
                date_obj = datetime.now()
            
            # Parse amount
            amount_str = str(trans_data.get("amount", "0"))
            amount_clean = re.sub(r'[^\d.-]', '', amount_str)
            try:
                amount = Decimal(amount_clean) if amount_clean else Decimal('0')
            except Exception:
                amount = Decimal('0')
            
            # Create transaction record
            transaction = Transaction(
                date=date_obj,
                description=trans_data.get("description", "")[:200],
                amount=amount,
                source_file_id=file_id
            )
            
            db.add(transaction)
        
        except Exception as e:
            # Skip invalid transactions but continue processing
            continue
    
    db.commit()
