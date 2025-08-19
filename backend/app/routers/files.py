"""
File Upload Routes - Step 2: File Upload & Parsing

This module handles:
- Bank statement file upload and processing
- PDF, CSV, and Excel file parsing
- Transaction extraction and normalization
- File validation and security checks
- Upload history and status tracking

Features:
- Multi-format file support (PDF, CSV, XLSX, XLS)
- Automatic transaction parsing and extraction
- File size and type validation
- Rate limiting to prevent abuse
- User-based file isolation
- Comprehensive error handling
"""

import os
import tempfile
import re
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, UploadFile, File as FastAPIFile, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..database import get_db
from ..auth import get_current_user
from ..models import User, File, FileStatus, Transaction, Category, Account, AccountType
from ..config import settings
from ..parsers import parse_canadian_bank_transactions
from ..parsers.canadian_banks import detect_canadian_bank, extract_account_info

# Import parsing libraries
import pdfplumber
try:
    import pandas as pd
except (ImportError, ValueError) as e:
    # Handle both ImportError and numpy compatibility issues
    pd = None
    print(f"Pandas import failed: {e}. CSV/Excel parsing will be disabled.")

# Create router
router = APIRouter(prefix="", tags=["File Upload"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename."""
    # Remove path separators and dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename

def validate_file_type(filename: str) -> bool:
    """Validate file type based on extension."""
    allowed_extensions = {'.pdf', '.csv', '.xlsx', '.xls'}
    file_ext = os.path.splitext(filename.lower())[1]
    return file_ext in allowed_extensions

def parse_pdf_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Parse transactions from PDF file with Canadian bank support."""
    transactions = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                
                # Also try table extraction
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row and len(row) >= 3:  # Basic validation
                            text += " ".join(str(cell) for cell in row if cell) + "\n"
    
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")
    
    # First try Canadian bank parsing
    canadian_transactions = parse_canadian_bank_transactions(text)
    if canadian_transactions:
        return canadian_transactions
    
    # Fallback to generic parsing
    lines = text.split('\n')
    date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
    amount_pattern = r'[-+]?\$?[\d,]+\.?\d*'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for date patterns
        date_matches = re.findall(date_pattern, line)
        if date_matches:
            try:
                # Parse date
                date_str = date_matches[0]
                # Handle different date formats including Canadian formats
                for fmt in ['%d/%m/%Y', '%Y/%m/%d', '%m/%d/%Y', '%m/%d/%y', '%m-%d-%Y', '%m-%d-%y', '%d-%m-%Y']:
                    try:
                        transaction_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    continue  # Skip if date parsing fails
                
                # Look for amounts
                amounts = re.findall(amount_pattern, line)
                if amounts:
                    # Take the last amount as it's usually the transaction amount
                    amount_str = amounts[-1].replace('$', '').replace(',', '')
                    try:
                        amount = float(amount_str)
                        # Determine if it's a debit or credit based on context
                        if 'debit' in line.lower() or 'withdrawal' in line.lower() or 'purchase' in line.lower():
                            amount = -abs(amount)
                        elif 'credit' in line.lower() or 'deposit' in line.lower():
                            amount = abs(amount)
                        elif amount > 0:
                            # Assume expenses are negative
                            amount = -amount
                        
                        # Extract description (everything except date and amount)
                        description = line
                        for date_match in date_matches:
                            description = description.replace(date_match, '').strip()
                        for amount_match in amounts:
                            description = description.replace(amount_match, '').strip()
                        
                        description = re.sub(r'\s+', ' ', description)  # Clean up whitespace
                        
                        if description and len(description) > 3:  # Basic description validation
                            transactions.append({
                                'date': transaction_date,
                                'description': description[:200],  # Limit description length
                                'amount': Decimal(str(amount))
                            })
                    
                    except (ValueError, TypeError):
                        continue  # Skip invalid amounts
            
            except Exception:
                continue  # Skip problematic lines
    
    return transactions

def parse_csv_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Parse transactions from CSV file."""
    if not pd:
        raise ValueError("Pandas not installed. Cannot parse CSV files.")
    
    transactions = []
    
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not read CSV file with any supported encoding")
        
        # Common column name mappings including Canadian bank formats
        column_mappings = {
            'date': ['date', 'Date', 'DATE', 'transaction_date', 'Transaction Date', 'Transaction_Date', 'Posting Date', 'posting_date'],
            'description': ['description', 'Description', 'DESC', 'memo', 'Memo', 'details', 'Details', 'Transaction Details', 'Payee', 'Reference'],
            'amount': ['amount', 'Amount', 'AMOUNT', 'value', 'Value', 'transaction_amount', 'debit', 'credit', 'Debit', 'Credit', 'CAD$', 'CAD']
        }
        
        # Find actual column names
        actual_columns = {}
        for field, possible_names in column_mappings.items():
            for col_name in df.columns:
                if col_name in possible_names:
                    actual_columns[field] = col_name
                    break
        
        if 'date' not in actual_columns or 'amount' not in actual_columns:
            raise ValueError("Required columns (date, amount) not found in CSV")
        
        # Process each row
        for _, row in df.iterrows():
            try:
                # Parse date with Canadian formats
                date_str = str(row[actual_columns['date']])
                try:
                    transaction_date = pd.to_datetime(date_str, dayfirst=True).to_pydatetime()
                except:
                    # Try different Canadian date formats
                    for fmt in ['%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%Y-%m-%d']:
                        try:
                            transaction_date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        transaction_date = pd.to_datetime(date_str).to_pydatetime()
                
                # Parse amount
                amount_value = row[actual_columns['amount']]
                if pd.isna(amount_value):
                    continue
                
                # Handle string amounts
                if isinstance(amount_value, str):
                    amount_value = amount_value.replace('$', '').replace(',', '').strip()
                    if amount_value.startswith('(') and amount_value.endswith(')'):
                        amount_value = '-' + amount_value[1:-1]
                
                amount = float(amount_value)
                
                # Get description
                description = ""
                if 'description' in actual_columns:
                    desc_value = row[actual_columns['description']]
                    if not pd.isna(desc_value):
                        description = str(desc_value)[:200]
                
                if not description:
                    description = "CSV Transaction"
                
                transactions.append({
                    'date': transaction_date,
                    'description': description,
                    'amount': Decimal(str(amount))
                })
            
            except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
                continue  # Skip invalid rows
    
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")
    
    return transactions

def parse_excel_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Parse transactions from Excel file."""
    if not pd:
        raise ValueError("Pandas not installed. Cannot parse Excel files.")
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Use similar logic as CSV parsing
        return parse_csv_transactions_from_dataframe(df)
    
    except Exception as e:
        raise ValueError(f"Error parsing Excel: {str(e)}")

def parse_csv_transactions_from_dataframe(df) -> List[Dict[str, Any]]:
    """Helper function to parse transactions from a pandas DataFrame."""
    transactions = []
    
    # Common column name mappings
    column_mappings = {
        'date': ['date', 'Date', 'DATE', 'transaction_date', 'Transaction Date'],
        'description': ['description', 'Description', 'DESC', 'memo', 'Memo', 'details', 'Details'],
        'amount': ['amount', 'Amount', 'AMOUNT', 'value', 'Value', 'transaction_amount', 'debit', 'credit']
    }
    
    # Find actual column names
    actual_columns = {}
    for field, possible_names in column_mappings.items():
        for col_name in df.columns:
            if col_name in possible_names:
                actual_columns[field] = col_name
                break
    
    if 'date' not in actual_columns or 'amount' not in actual_columns:
        raise ValueError("Required columns (date, amount) not found")
    
    # Process each row
    for _, row in df.iterrows():
        try:
            # Parse date
            date_str = str(row[actual_columns['date']])
            transaction_date = pd.to_datetime(date_str).to_pydatetime()
            
            # Parse amount
            amount_value = row[actual_columns['amount']]
            if pd.isna(amount_value):
                continue
            
            # Handle string amounts
            if isinstance(amount_value, str):
                amount_value = amount_value.replace('$', '').replace(',', '').strip()
                if amount_value.startswith('(') and amount_value.endswith(')'):
                    amount_value = '-' + amount_value[1:-1]
            
            amount = float(amount_value)
            
            # Get description
            description = ""
            if 'description' in actual_columns:
                desc_value = row[actual_columns['description']]
                if not pd.isna(desc_value):
                    description = str(desc_value)[:200]
            
            if not description:
                description = "Transaction"
            
            transactions.append({
                'date': transaction_date,
                'description': description,
                'amount': Decimal(str(amount))
            })
        
        except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
            continue  # Skip invalid rows
    
    return transactions

def auto_categorize_transaction(description: str, amount: float, db: Session) -> int:
    """Auto-categorize transaction based on description and amount."""
    description_lower = description.lower()
    
    # Define categorization rules
    category_rules = {
        'groceries': ['grocery', 'supermarket', 'food', 'loblaws', 'metro', 'sobeys', 'walmart'],
        'food & dining': ['restaurant', 'coffee', 'tim hortons', 'starbucks', 'mcdonald', 'pizza', 'cafe'],
        'transportation': ['gas station', 'petro', 'shell', 'esso', 'transit', 'uber', 'taxi', 'parking'],
        'shopping': ['purchase', 'amazon', 'store', 'mall', 'shop'],
        'bills & utilities': ['bank fee', 'service charge', 'utility', 'hydro', 'rogers', 'bell', 'telus'],
        'entertainment': ['movie', 'entertainment', 'spotify', 'netflix', 'game'],
        'healthcare': ['pharmacy', 'medical', 'hospital', 'dental', 'doctor'],
        'travel': ['hotel', 'airline', 'flight', 'booking'],
        'personal care': ['salon', 'spa', 'cosmetic'],
        'education': ['school', 'university', 'course', 'tuition']
    }
    
    # Check for income patterns (positive amounts)
    if amount > 0:
        income_keywords = ['salary', 'deposit', 'payment', 'refund', 'transfer', 'income']
        if any(keyword in description_lower for keyword in income_keywords):
            # For income, we don't categorize or create an "Income" category
            return None
    
    # Find matching category
    for category_name, keywords in category_rules.items():
        if any(keyword in description_lower for keyword in keywords):
            category = db.query(Category).filter(Category.name.ilike(f'%{category_name}%')).first()
            if category:
                return category.id
    
    # Default to uncategorized
    return None

def create_or_find_account(text: str, bank_type: str, household_id: int, db: Session) -> int:
    """Create or find account based on parsed bank statement."""
    # Extract account information from the statement text
    account_info = extract_account_info(text, bank_type)
    
    # Map account type to AccountType enum
    account_type_map = {
        'CHECKING': AccountType.bank,
        'SAVINGS': AccountType.bank, 
        'CREDIT': AccountType.card
    }
    account_type = account_type_map.get(account_info['account_type'], AccountType.bank)
    
    # Create account name with bank and type info
    account_name = f"{bank_type} {account_info['account_type'].title()}".strip()
    
    # Look for existing account by name and last 4 digits
    existing_account = db.query(Account).filter(
        Account.household_id == household_id,
        Account.name == account_name,
        Account.last4 == account_info['last_4_digits']
    ).first()
    
    if existing_account:
        return existing_account.id
    
    # Create new account
    new_account = Account(
        household_id=household_id,
        name=account_name,
        type=account_type,
        last4=account_info['last_4_digits'],
        currency='CAD'  # Canadian banks default to CAD
    )
    
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return new_account.id

def store_transactions(transactions: List[Dict[str, Any]], user_id: int, file_id: int, account_id: int, db: Session):
    """Store parsed transactions in database with auto-categorization."""
    for transaction_data in transactions:
        try:
            # Auto-categorize the transaction
            category_id = auto_categorize_transaction(
                transaction_data['description'], 
                float(transaction_data['amount']), 
                db
            )
            
            transaction = Transaction(
                date=transaction_data['date'],
                description=transaction_data['description'],
                amount=transaction_data['amount'],
                category_id=category_id,
                user_id=user_id,
                source_file_id=file_id,
                account_id=account_id  # Associate with the bank account
            )
            
            db.add(transaction)
        
        except Exception:
            # Skip invalid transactions but continue processing
            continue
    
    db.commit()

@router.post("/upload-statement")
@limiter.limit("20/hour")  # Limit file uploads to prevent abuse
async def upload_statement(
    request: Request,
    file: UploadFile = FastAPIFile(...),
    household_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse bank statement file."""
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Validate file type
    if not validate_file_type(safe_filename):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload PDF, CSV, or Excel files."
        )
    
    # Check file size
    max_size = settings.max_file_size  # 10MB default
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {max_size // (1024*1024)}MB"
        )
    
    # Create file record
    db_file = File(
        filename=safe_filename,
        file_size=len(content),
        user_id=current_user.id,
        household_id=household_id,
        status=FileStatus.parsing
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(safe_filename)[1]) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Parse file based on type
        file_ext = os.path.splitext(safe_filename.lower())[1]
        transactions = []
        text = ""
        
        if file_ext == '.pdf':
            transactions = parse_pdf_transactions(temp_file_path)
            # Also extract text for account creation
            try:
                import pdfplumber
                with pdfplumber.open(temp_file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception:
                text = ""
        elif file_ext == '.csv':
            transactions = parse_csv_transactions(temp_file_path)
        elif file_ext in ['.xlsx', '.xls']:
            transactions = parse_excel_transactions(temp_file_path)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if not transactions:
            db_file.status = FileStatus.error
            db.commit()
            raise HTTPException(status_code=400, detail="No valid transactions found in file")
        
        # Create or find account for PDF files
        account_id = None
        if file_ext == '.pdf' and text:
            bank_type = detect_canadian_bank(text)
            if bank_type and bank_type != 'UNKNOWN':
                account_id = create_or_find_account(text, bank_type, household_id, db)
        
        # Store transactions
        store_transactions(transactions, current_user.id, db_file.id, account_id, db)
        
        # Update file status
        db_file.status = FileStatus.parsed
        db.commit()
        
        return {
            "message": f"Successfully processed {len(transactions)} transactions",
            "file_id": db_file.id,
            "filename": safe_filename,
            "transactions_count": len(transactions)
        }
    
    except Exception as e:
        # Clean up temp file if it exists
        try:
            if 'temp_file_path' in locals():
                os.unlink(temp_file_path)
        except:
            pass
        
        # Update file status
        db_file.status = FileStatus.error
        db.commit()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing file: {str(e)}"
        )

@router.get("/files")
def get_uploaded_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's uploaded files."""
    files = db.query(File).filter(File.user_id == current_user.id).all()
    
    result = []
    for file in files:
        result.append({
            "id": file.id,
            "filename": file.filename,
            "file_size": file.file_size,
            "status": file.status.value,
            "uploaded_at": file.uploaded_at,
            "transactions_count": len(file.transactions) if file.transactions else 0
        })
    
    return result

@router.post("/categorize-transactions")
def categorize_existing_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Categorize existing uncategorized transactions."""
    # Get all uncategorized transactions for the user
    uncategorized_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.category_id.is_(None)
    ).all()
    
    categorized_count = 0
    for transaction in uncategorized_transactions:
        category_id = auto_categorize_transaction(
            transaction.description,
            float(transaction.amount),
            db
        )
        
        if category_id:
            transaction.category_id = category_id
            categorized_count += 1
    
    db.commit()
    
    return {
        "message": f"Categorized {categorized_count} out of {len(uncategorized_transactions)} transactions",
        "categorized": categorized_count,
        "total": len(uncategorized_transactions)
    }