"""
Transaction Routes - Step 2: File Upload & Parsing + Step 3: Categorization

This module handles:
- Transaction CRUD operations (Create, Read, Update, Delete)
- Transaction filtering and searching
- Bulk transaction operations
- Transaction categorization (manual and automatic)
- Rule-based auto-categorization system

Features:
- User-based transaction isolation
- Date-based filtering and sorting
- Category assignment and management
- Comprehensive input validation
- Error handling and logging
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, String, func, case
from typing import Optional, List
from datetime import datetime, timedelta
import pdfplumber
import io
import logging

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    TransactionCreate, TransactionUpdate, TransactionResponse, 
    CategorizeTransactionRequest
)
from ..models import User, Transaction, Category, BankAccount, Account, AccountType
from ..parsers.canadian_banks import parse_canadian_bank_transactions, detect_canadian_bank, extract_account_info, extract_account_balance, map_pdf_category_to_system_id

# Create router
router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 50,
    category_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    month: Optional[str] = None,
    year: Optional[int] = None,
    sort_by: str = Query("date", description="Sort by: date, amount, description"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    bank_filter: Optional[str] = Query(None, description="Filter by bank type: CIBC, RBC, AMEX"),
    has_category: Optional[bool] = Query(None, description="Filter by categorized/uncategorized"),
    merchant_filter: Optional[str] = Query(None, description="Filter by merchant name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transactions with optional filtering and monthly grouping."""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    # Apply filters
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    # Monthly filtering (preferred over date range)
    if month and year:
        # Parse month (e.g., "january" or "01")
        try:
            if month.isdigit():
                month_num = int(month)
            else:
                month_num = datetime.strptime(month.capitalize(), '%B').month
            
            start_dt = datetime(year, month_num, 1)
            if month_num == 12:
                end_dt = datetime(year + 1, 1, 1)
            else:
                end_dt = datetime(year, month_num + 1, 1)
            
            query = query.filter(Transaction.date >= start_dt, Transaction.date < end_dt)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid month or year format")
    
    # Date range filtering (fallback)
    elif start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Transaction.date >= start_dt)
    
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Transaction.date <= end_dt)
    
    if search:
        query = query.filter(or_(
            Transaction.description.ilike(f"%{search}%"),
            func.cast(Transaction.amount, String).like(f"%{search}%")
        ))
    
    # Bank filter (if transaction has source info)
    if bank_filter:
        query = query.filter(Transaction.description.contains(bank_filter.upper()))
    
    # Category filter (tagged/untagged)
    if has_category is not None:
        if has_category:
            query = query.filter(Transaction.category_id.isnot(None))
        else:
            query = query.filter(Transaction.category_id.is_(None))
    
    # Merchant filter
    if merchant_filter:
        query = query.filter(Transaction.description.ilike(f"%{merchant_filter}%"))
    
    # Dynamic sorting
    sort_column = Transaction.date  # default
    if sort_by == "amount":
        sort_column = Transaction.amount
    elif sort_by == "description":
        sort_column = Transaction.description
    
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Get transactions with category names
    transactions = query.offset(skip).limit(limit).all()
    
    # Convert to response format with category names
    result = []
    for transaction in transactions:
        category_name = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
            if category:
                category_name = category.name
        
        result.append({
            "id": transaction.id,
            "date": transaction.date,
            "description": transaction.description,
            "amount": float(transaction.amount),
            "category_id": transaction.category_id,
            "account_id": transaction.account_id,
            "user_id": transaction.user_id,
            "source_file_id": transaction.source_file_id,
            "category_name": category_name
        })
    
    return result

@router.get("/grouped-by-month")
def get_transactions_grouped_by_month(
    year: Optional[int] = Query(None, description="Year to filter (default: current year)"),
    search: Optional[str] = Query(None, description="Search in descriptions"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    bank_filter: Optional[str] = Query(None, description="Filter by bank"),
    has_category: Optional[bool] = Query(None, description="Filter tagged/untagged"),
    time_filter: Optional[str] = Query(None, description="Time filter: 7days, 30days, 90days, 6months, 1year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions grouped by month with counts and totals (like the frontend image)."""
    
    if not year:
        year = datetime.now().year
    
    # Base query with filters
    base_query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    # Apply time filter (overrides year filter if specified)
    if time_filter:
        now = datetime.now()
        if time_filter == '7days':
            start_date = now - timedelta(days=7)
        elif time_filter == '30days':
            start_date = now - timedelta(days=30)
        elif time_filter == '90days':
            start_date = now - timedelta(days=90)
        elif time_filter == '6months':
            start_date = now - timedelta(days=180)
        elif time_filter == '1year':
            start_date = now - timedelta(days=365)
        else:
            start_date = None
            
        if start_date:
            print(f"🔍 Time filter applied: {time_filter} -> filtering from {start_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
            base_query = base_query.filter(Transaction.date >= start_date)
    else:
        # Apply year filter only if no time filter is specified
        start_of_year = datetime(year, 1, 1)
        end_of_year = datetime(year + 1, 1, 1)
        base_query = base_query.filter(
            Transaction.date >= start_of_year,
            Transaction.date < end_of_year
        )
    
    # Apply search filter
    if search:
        base_query = base_query.filter(or_(
            Transaction.description.ilike(f"%{search}%"),
            func.cast(Transaction.amount, String).like(f"%{search}%")
        ))
    
    # Apply other filters
    if category_id:
        base_query = base_query.filter(Transaction.category_id == category_id)
    
    if bank_filter:
        base_query = base_query.filter(Transaction.description.contains(bank_filter.upper()))
    
    if has_category is not None:
        if has_category:
            base_query = base_query.filter(Transaction.category_id.isnot(None))
        else:
            base_query = base_query.filter(Transaction.category_id.is_(None))
    
    # Get all matching transactions
    all_transactions = base_query.order_by(Transaction.date.desc()).all()
    
    # Group by month
    monthly_groups = {}
    
    for transaction in all_transactions:
        month_key = transaction.date.strftime('%Y-%m')
        month_name = transaction.date.strftime('%B %Y')
        
        if month_key not in monthly_groups:
            monthly_groups[month_key] = {
                "month_name": month_name,
                "month": transaction.date.month,
                "year": transaction.date.year,
                "transaction_count": 0,
                "total_income": 0.0,
                "total_expenses": 0.0,
                "net_amount": 0.0,
                "transactions": []
            }
        
        # Add transaction data
        monthly_groups[month_key]["transaction_count"] += 1
        amount = float(transaction.amount)
        
        if amount > 0:
            monthly_groups[month_key]["total_income"] += amount
        else:
            monthly_groups[month_key]["total_expenses"] += abs(amount)
        
        monthly_groups[month_key]["net_amount"] += amount
        
        # Get category info for transaction
        category_name = None
        category_color = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
            if category:
                category_name = category.name
        
        # Add transaction to group
        monthly_groups[month_key]["transactions"].append({
            "id": transaction.id,
            "date": transaction.date,
            "time": transaction.date.strftime('%I:%M %p'),
            "description": transaction.description,
            "merchant": transaction.description.split()[0] if transaction.description else "Unknown",
            "amount": amount,
            "formatted_amount": f"${abs(amount):,.2f}" if amount != 0 else "$0.00",
            "is_credit": amount > 0,
            "category_id": transaction.category_id,
            "category_name": category_name or "Untagged",
            "account_id": transaction.account_id,
            "user_id": transaction.user_id,
            "source_file_id": transaction.source_file_id
        })
    
    # Convert to list and sort by date (newest first)
    result = []
    for month_key in sorted(monthly_groups.keys(), reverse=True):
        group = monthly_groups[month_key]
        income_str = f"${group['total_income']:,.2f}" if group['total_income'] > 0 else "$0.00"
        expenses_str = f"${group['total_expenses']:,.2f}" if group['total_expenses'] > 0 else "$0.00"
        net_str = f"${group['net_amount']:+,.2f}"
        group["formatted_totals"] = f"Income: {income_str} • Expenses: {expenses_str} • Net: {net_str}"
        result.append(group)
    
    return {
        "year": year,
        "total_months": len(result),
        "monthly_groups": result,
        "filters_applied": {
            "search": search,
            "category_id": category_id,
            "bank_filter": bank_filter,
            "has_category": has_category
        }
    }

@router.get("/all", response_model=dict)
def get_all_transactions(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page (max 100)"),
    category_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user transactions with pagination (50 per page by default)."""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    # Apply filters
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Transaction.date >= start_dt)
    
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Transaction.date <= end_dt)
    
    if search:
        query = query.filter(Transaction.description.contains(search))
    
    # Order by date (newest first)
    query = query.order_by(Transaction.date.desc())
    
    # Get total count for pagination info
    total_count = query.count()
    
    # Calculate pagination
    skip = (page - 1) * per_page
    total_pages = (total_count + per_page - 1) // per_page
    
    # Get paginated results
    transactions = query.offset(skip).limit(per_page).all()
    
    # Convert to response format with category names
    result = []
    for transaction in transactions:
        category_name = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
            if category:
                category_name = category.name
        
        result.append({
            "id": transaction.id,
            "date": transaction.date,
            "description": transaction.description,
            "amount": float(transaction.amount),
            "category_id": transaction.category_id,
            "account_id": transaction.account_id,
            "user_id": transaction.user_id,
            "source_file_id": transaction.source_file_id,
            "category_name": category_name
        })
    
    return {
        "transactions": result,
        "pagination": {
            "current_page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_count": total_count,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }

@router.get("/monthly-summary")
def get_monthly_summary(
    year: Optional[int] = Query(None, description="Year (defaults to current year)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly transaction summary for a year."""
    if not year:
        year = datetime.now().year
    
    # Get all transactions for the year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year + 1, 1, 1)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_of_year,
        Transaction.date < end_of_year
    ).order_by(Transaction.date.desc()).all()
    
    # Group by month
    monthly_data = {}
    for month in range(1, 13):
        month_name = datetime(year, month, 1).strftime('%B')
        monthly_data[month_name] = {
            "month": month,
            "year": year,
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_amount": 0.0,
            "transaction_count": 0,
            "categories": {}
        }
    
    # Process transactions
    for transaction in transactions:
        month_name = transaction.date.strftime('%B')
        amount = float(transaction.amount)
        
        monthly_data[month_name]["transaction_count"] += 1
        
        if amount > 0:
            monthly_data[month_name]["total_income"] += amount
        else:
            monthly_data[month_name]["total_expenses"] += abs(amount)
        
        monthly_data[month_name]["net_amount"] += amount
        
        # Category breakdown
        category_name = "Uncategorized"
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
            if category:
                category_name = category.name
        
        if category_name not in monthly_data[month_name]["categories"]:
            monthly_data[month_name]["categories"][category_name] = 0.0
        
        monthly_data[month_name]["categories"][category_name] += abs(amount)
    
    return {
        "year": year,
        "monthly_summary": monthly_data,
        "yearly_totals": {
            "total_income": sum(data["total_income"] for data in monthly_data.values()),
            "total_expenses": sum(data["total_expenses"] for data in monthly_data.values()),
            "net_amount": sum(data["net_amount"] for data in monthly_data.values()),
            "total_transactions": sum(data["transaction_count"] for data in monthly_data.values())
        }
    }

@router.post("/upload-pdf")
async def upload_and_extract_transactions(
    file: UploadFile = File(...),
    account_id: Optional[int] = Query(None, description="Account ID for the transactions"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload PDF bank statement and extract transactions (CIBC, RBC, AMEX)."""
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Validate file size (10MB limit)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed.")
    
    try:
        # Read PDF content
        contents = await file.read()
        logging.info(f"Read PDF file: {file.filename}, size: {len(contents)} bytes")
        
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty PDF file")
        
        # Extract text using pdfplumber (better for bank statements)
        text_content = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            logging.info(f"PDF has {len(pdf.pages)} pages")
            
            for page_num, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
                        logging.info(f"Extracted text from page {page_num + 1}: {len(page_text)} characters")
                    else:
                        logging.warning(f"No text found on page {page_num + 1}")
                except Exception as page_error:
                    logging.warning(f"Error extracting text from page {page_num + 1}: {str(page_error)}")
                    continue
        
        if not text_content.strip():
            raise HTTPException(
                status_code=400, 
                detail="No text could be extracted from PDF. The file might be image-based or corrupted."
            )
        
        logging.info(f"Total extracted text length: {len(text_content)} characters")
        
        # Detect bank type and account type
        bank_type, account_type = detect_canadian_bank(text_content)
        logging.info(f"Detected bank type: {bank_type}, account type: {account_type}")
        
        if bank_type == 'UNKNOWN':
            # Provide more helpful error message with text sample
            text_sample = text_content[:500] if len(text_content) > 500 else text_content
            raise HTTPException(
                status_code=400, 
                detail=f"Bank statement format not recognized. Supported: CIBC, RBC, AMEX. Text sample: {text_sample}"
            )
        
        # Extract account information from statement
        account_info = extract_account_info(text_content, bank_type, account_type)
        logging.info(f"Extracted account info: {account_info}")
        
        # Extract account balance from statement
        account_balance = extract_account_balance(text_content, bank_type)
        logging.info(f"Extracted account balance: ${account_balance:.2f}")
        
        # Create or find account if not provided
        if account_id is None:
            # Look for existing account using name and last 4 digits
            account_name = f"{bank_type} {account_info['account_type'].title()}".strip()
            existing_account = db.query(Account).filter(
                Account.household_id == current_user.id,
                Account.name == account_name,
                Account.last4 == account_info['last_4_digits']
            ).first()
            
            if existing_account:
                account_id = existing_account.id
                logging.info(f"Found existing account {account_id} for {bank_type} ending in {account_info['last_4_digits']}")
            else:
                # Check for existing bank account first
                existing_bank_account = db.query(BankAccount).filter(
                    BankAccount.user_id == current_user.id,
                    BankAccount.bank_name == bank_type,
                    BankAccount.account_type == account_info['account_type'],
                    BankAccount.account_number == f"****{account_info['last_4_digits']}"
                ).first()
                
                if not existing_bank_account and account_info['last_4_digits'] != '0000':
                    # Only create new bank account if we have valid account digits (not fallback '0000')
                    new_bank_account = BankAccount(
                        user_id=current_user.id,
                        household_id=current_user.id,  # Set household_id to user_id
                        bank_name=bank_type,
                        account_type=account_info['account_type'],
                        account_number=f"****{account_info['last_4_digits']}",
                        balance=account_balance  # Use extracted balance from PDF
                    )
                    db.add(new_bank_account)
                    logging.info(f"Created new {account_info['account_type']} account {new_bank_account.id} for {bank_type} ending in {account_info['last_4_digits']}")
                elif account_info['last_4_digits'] == '0000':
                    logging.warning(f"Skipping BankAccount creation - failed to extract valid account number from PDF")
                else:
                    # Update existing bank account balance with latest from PDF
                    existing_bank_account.balance = account_balance
                    logging.info(f"Updated existing bank account balance to ${account_balance:.2f}")
                
                # Also create an Account record for transaction references
                account_type_map = {
                    'CHECKING': AccountType.bank,
                    'SAVINGS': AccountType.bank, 
                    'CREDIT': AccountType.card
                }
                account_type = account_type_map.get(account_info['account_type'], AccountType.bank)
                account_name = f"{bank_type} {account_info['account_type'].title()}".strip()
                
                new_account = Account(
                    household_id=current_user.id,  # Using user_id as household_id for now
                    name=account_name,
                    type=account_type,
                    last4=account_info['last_4_digits'],
                    currency='CAD'
                )
                db.add(new_account)
                db.commit()
                db.refresh(new_account)
                account_id = new_account.id  # Use Account.id for transactions
                logging.info(f"Created new {account_info['account_type']} account {account_id} for {bank_type} ending in {account_info['last_4_digits']}")
        
        # Parse transactions
        parsed_transactions = parse_canadian_bank_transactions(text_content)
        logging.info(f"Parsed {len(parsed_transactions)} transactions")
        
        if not parsed_transactions:
            # Provide text sample for debugging
            text_sample = text_content[:1000] if len(text_content) > 1000 else text_content
            raise HTTPException(
                status_code=400,
                detail=f"No transactions found in the PDF. Bank: {bank_type}. Text sample: {text_sample}"
            )
        
        # Save transactions to database
        saved_transactions = []
        duplicate_count = 0
        errors = []
        
        for i, trans_data in enumerate(parsed_transactions):
            try:
                # Check for duplicates (same date, amount, description)
                existing = db.query(Transaction).filter(
                    Transaction.user_id == current_user.id,
                    Transaction.date == trans_data['date'],
                    Transaction.amount == trans_data['amount'],
                    Transaction.description == trans_data['description']
                ).first()
                
                if existing:
                    duplicate_count += 1
                    continue
                
                # Map PDF category to system category
                category_id = None
                if 'pdf_category' in trans_data and trans_data['pdf_category']:
                    category_id = map_pdf_category_to_system_id(trans_data['pdf_category'])
                    if category_id:
                        logging.info(f"Auto-categorized transaction as category_id {category_id} from PDF category '{trans_data['pdf_category']}'")
                
                # Create new transaction with auto-assigned category
                new_transaction = Transaction(
                    account_id=account_id,
                    date=trans_data['date'],
                    description=trans_data['description'],
                    amount=trans_data['amount'],
                    category_id=category_id,  # Auto-assign category from PDF
                    user_id=current_user.id
                )
                
                db.add(new_transaction)
                saved_transactions.append(new_transaction)
                
            except Exception as trans_error:
                errors.append(f"Transaction {i+1}: {str(trans_error)}")
                logging.error(f"Error saving transaction {i+1}: {str(trans_error)}")
                continue
        
        if saved_transactions:
            db.commit()
            
            # Refresh to get IDs
            for transaction in saved_transactions:
                db.refresh(transaction)
        
        # Format response
        result_transactions = []
        for transaction in saved_transactions:
            result_transactions.append({
                "id": transaction.id,
                "date": transaction.date,
                "description": transaction.description,
                "amount": float(transaction.amount),
                "category_id": transaction.category_id,
                "account_id": transaction.account_id,
                "user_id": transaction.user_id,
                "source_file_id": transaction.source_file_id,
                "category_name": None
            })
        
        response_data = {
            "message": f"Successfully processed {file.filename}",
            "bank_type": bank_type,
            "account_info": {
                "account_id": account_id,
                "account_type": account_info['account_type'],
                "last_4_digits": account_info['last_4_digits'],
                "bank_name": bank_type
            },
            "total_transactions_found": len(parsed_transactions),
            "new_transactions_added": len(saved_transactions),
            "duplicates_skipped": duplicate_count,
            "transactions": result_transactions[:10]  # Show first 10 for preview
        }
        
        if errors:
            response_data["errors"] = errors
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error processing PDF {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.post("/test-pdf-text")
async def test_pdf_text_extraction(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Test endpoint to extract and return raw text from PDF for debugging."""
    
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read PDF content
        contents = await file.read()
        
        # Extract text using pdfplumber
        text_content = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content += f"=== PAGE {page_num + 1} ===\n{page_text}\n\n"
        
        # Detect bank type
        bank_type = detect_canadian_bank(text_content)
        
        return {
            "filename": file.filename,
            "total_pages": len(pdf.pages) if 'pdf' in locals() else 0,
            "text_length": len(text_content),
            "detected_bank": bank_type,
            "extracted_text": text_content[:2000] + "..." if len(text_content) > 2000 else text_content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

@router.get("/filter-stats")
def get_filter_statistics(
    year: Optional[int] = Query(None, description="Year to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for filters (untagged count, bank breakdown, etc.)."""
    
    if not year:
        year = datetime.now().year
    
    # Base query for the year
    start_of_year = datetime(year, 1, 1)
    end_of_year = datetime(year + 1, 1, 1)
    
    base_query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_of_year,
        Transaction.date < end_of_year
    )
    
    total_transactions = base_query.count()
    
    # Untagged transactions count
    untagged_count = base_query.filter(Transaction.category_id.is_(None)).count()
    tagged_count = total_transactions - untagged_count
    
    # Bank breakdown (approximate from descriptions)
    bank_stats = {}
    all_transactions = base_query.all()
    
    for transaction in all_transactions:
        desc = transaction.description.upper() if transaction.description else ""
        bank = "OTHER"
        
        if "CIBC" in desc or "IMPERIAL" in desc:
            bank = "CIBC"
        elif "RBC" in desc or "ROYAL" in desc:
            bank = "RBC"
        elif "AMEX" in desc or "AMERICAN EXPRESS" in desc:
            bank = "AMEX"
        elif "TD" in desc or "DOMINION" in desc:
            bank = "TD"
        elif "BMO" in desc or "MONTREAL" in desc:
            bank = "BMO"
        elif "SCOTIA" in desc:
            bank = "SCOTIA"
        
        if bank not in bank_stats:
            bank_stats[bank] = 0
        bank_stats[bank] += 1
    
    # Category breakdown
    category_stats = db.query(
        Category.name,
        func.count(Transaction.id).label('count')
    ).join(Transaction, Transaction.category_id == Category.id, isouter=False).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_of_year,
        Transaction.date < end_of_year
    ).group_by(Category.id, Category.name).order_by(
        func.count(Transaction.id).desc()
    ).all()
    
    # Merchant breakdown (top merchants)
    merchant_stats = {}
    for transaction in all_transactions:
        if transaction.description:
            # Extract first word as merchant
            merchant = transaction.description.split()[0] if transaction.description.split() else "Unknown"
            if merchant not in merchant_stats:
                merchant_stats[merchant] = 0
            merchant_stats[merchant] += 1
    
    # Sort merchants by frequency
    top_merchants = sorted(merchant_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "year": year,
        "total_transactions": total_transactions,
        "categorization": {
            "tagged": tagged_count,
            "untagged": untagged_count,
            "tagged_percentage": round((tagged_count / total_transactions * 100), 1) if total_transactions > 0 else 0
        },
        "banks": bank_stats,
        "top_categories": [
            {"name": cat.name, "count": cat.count}
            for cat in category_stats
        ],
        "top_merchants": [
            {"name": merchant, "count": count}
            for merchant, count in top_merchants
        ]
    }

@router.post("", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction."""
    # Validate category exists if provided
    if transaction.category_id:
        category = db.query(Category).filter(Category.id == transaction.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    db_transaction = Transaction(
        account_id=transaction.account_id,
        date=transaction.date,
        description=transaction.description,
        amount=transaction.amount,
        category_id=transaction.category_id,
        user_id=current_user.id
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Get category name for response
    category_name = None
    if db_transaction.category_id:
        category = db.query(Category).filter(Category.id == db_transaction.category_id).first()
        if category:
            category_name = category.name
    
    return {
        "id": db_transaction.id,
        "date": db_transaction.date,
        "description": db_transaction.description,
        "amount": float(db_transaction.amount),
        "category_id": db_transaction.category_id,
        "account_id": db_transaction.account_id,
        "user_id": db_transaction.user_id,
        "source_file_id": db_transaction.source_file_id,
        "category_name": category_name
    }

@router.get("/statistics")
def get_transaction_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive transaction statistics."""
    # Get basic counts
    total_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).count()
    
    # Get income vs expense counts and totals
    income_stats = db.query(
        func.count(Transaction.id).label('count'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.amount > 0
    ).first()
    
    expense_stats = db.query(
        func.count(Transaction.id).label('count'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.amount < 0
    ).first()
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= thirty_days_ago
    ).count()
    
    # Get most frequent categories
    top_categories = db.query(
        Category.name,
        func.count(Transaction.id).label('count'),
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).label('total_spent')
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id
    ).group_by(Category.id, Category.name).order_by(
        func.count(Transaction.id).desc()
    ).limit(5).all()
    
    # Get average transaction amounts
    avg_income = db.query(func.avg(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.amount > 0
    ).scalar() or 0
    
    avg_expense = db.query(func.avg(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.amount < 0
    ).scalar() or 0
    
    return {
        "total_transactions": total_transactions,
        "income": {
            "count": income_stats.count or 0,
            "total": float(income_stats.total or 0),
            "average": float(avg_income)
        },
        "expenses": {
            "count": expense_stats.count or 0,
            "total": float(abs(expense_stats.total or 0)),
            "average": float(abs(avg_expense))
        },
        "recent_activity": {
            "last_30_days": recent_transactions,
            "daily_average": round(recent_transactions / 30, 2)
        },
        "top_categories": [
            {
                "name": cat.name,
                "transaction_count": cat.count,
                "total_spent": float(cat.total_spent or 0)
            }
            for cat in top_categories
        ]
    }

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction."""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Get category name
    category_name = None
    if transaction.category_id:
        category = db.query(Category).filter(Category.id == transaction.category_id).first()
        if category:
            category_name = category.name
    
    return {
        "id": transaction.id,
        "date": transaction.date,
        "description": transaction.description,
        "amount": float(transaction.amount),
        "category_id": transaction.category_id,
        "account_id": transaction.account_id,
        "user_id": transaction.user_id,
        "source_file_id": transaction.source_file_id,
        "category_name": category_name
    }

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a transaction."""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Validate category if being updated
    if transaction_update.category_id:
        category = db.query(Category).filter(Category.id == transaction_update.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    # Update fields
    update_data = transaction_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    # Get category name
    category_name = None
    if transaction.category_id:
        category = db.query(Category).filter(Category.id == transaction.category_id).first()
        if category:
            category_name = category.name
    
    return {
        "id": transaction.id,
        "date": transaction.date,
        "description": transaction.description,
        "amount": float(transaction.amount),
        "category_id": transaction.category_id,
        "account_id": transaction.account_id,
        "user_id": transaction.user_id,
        "source_file_id": transaction.source_file_id,
        "category_name": category_name
    }

@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction."""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Transaction deleted successfully"}

@router.post("/{transaction_id}/categorize")
def categorize_single_transaction(
    transaction_id: int,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Categorize a single transaction."""
    # Find the transaction
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    category_id = request.get("category_id")
    
    # Verify category exists if provided
    if category_id:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        transaction.category_id = category_id
        category_name = category.name
    else:
        # Clear category
        transaction.category_id = None
        category_name = None
    
    db.commit()
    
    return {
        "message": "Transaction categorized successfully",
        "transaction_id": transaction_id,
        "category_id": category_id,
        "category_name": category_name
    }

@router.post("/categorize")
def categorize_transactions(
    request: CategorizeTransactionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually categorize multiple transactions."""
    # Verify category exists
    category = db.query(Category).filter(Category.id == request.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update transactions
    updated_count = 0
    for transaction_id in request.transaction_ids:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if transaction:
            transaction.category_id = request.category_id
            updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully categorized {updated_count} transactions",
        "category_name": category.name
    }

# Enhanced Bulk Operations

@router.post("/bulk-delete")
def bulk_delete_transactions(
    transaction_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple transactions at once."""
    if not transaction_ids:
        raise HTTPException(status_code=400, detail="No transaction IDs provided")
    
    # Verify all transactions belong to the user
    transactions = db.query(Transaction).filter(
        Transaction.id.in_(transaction_ids),
        Transaction.user_id == current_user.id
    ).all()
    
    if len(transactions) != len(transaction_ids):
        raise HTTPException(status_code=400, detail="Some transactions not found or not owned by user")
    
    # Delete transactions
    deleted_count = 0
    for transaction in transactions:
        db.delete(transaction)
        deleted_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} transactions",
        "deleted_count": deleted_count
    }

@router.post("/bulk-categorize")
def bulk_categorize_transactions(
    transaction_ids: List[int],
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk categorize multiple transactions (for frontend bulk selection)."""
    if not transaction_ids:
        raise HTTPException(status_code=400, detail="No transaction IDs provided")
    
    # Verify category exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update transactions
    updated_count = 0
    for transaction_id in transaction_ids:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if transaction:
            transaction.category_id = category_id
            updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully categorized {updated_count} transactions",
        "category_name": category.name,
        "updated_count": updated_count,
        "category_id": category_id
    }

@router.post("/bulk-update")
def bulk_update_transactions(
    updates: List[dict],  # List of {"id": int, "category_id": int, "description": str, etc.}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update multiple transactions at once."""
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    updated_count = 0
    errors = []
    
    for update in updates:
        transaction_id = update.get("id")
        if not transaction_id:
            errors.append({"error": "Missing transaction ID", "update": update})
            continue
        
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            errors.append({"error": f"Transaction {transaction_id} not found", "update": update})
            continue
        
        # Apply updates
        for field, value in update.items():
            if field != "id" and hasattr(transaction, field):
                setattr(transaction, field, value)
        
        updated_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully updated {updated_count} transactions",
        "updated_count": updated_count,
        "errors": errors
    }

@router.get("/search")
def search_transactions(
    query: str = Query(..., description="Search query"),
    limit: int = Query(50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search transactions by description, amount, or category."""
    if len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    # Search in description
    transactions = db.query(Transaction).join(Category, Transaction.category_id == Category.id, isouter=True).filter(
        Transaction.user_id == current_user.id,
        or_(
            Transaction.description.ilike(f"%{query}%"),
            Category.name.ilike(f"%{query}%"),
            func.cast(Transaction.amount, String).like(f"%{query}%")
        )
    ).order_by(Transaction.date.desc()).limit(limit).all()
    
    result = []
    for transaction in transactions:
        category_name = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
            if category:
                category_name = category.name
        
        result.append({
            "id": transaction.id,
            "date": transaction.date,
            "description": transaction.description,
            "amount": float(transaction.amount),
            "category_id": transaction.category_id,
            "account_id": transaction.account_id,
            "user_id": transaction.user_id,
            "source_file_id": transaction.source_file_id,
            "category_name": category_name
        })
    
    return {
        "query": query,
        "results_count": len(result),
        "transactions": result
    }

@router.post("/export-selected")
def export_selected_transactions(
    transaction_ids: List[int],
    format: str = Query("csv", description="Export format: csv, json, excel"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export selected transactions (for bulk selection export)."""
    if not transaction_ids:
        raise HTTPException(status_code=400, detail="No transaction IDs provided")
    
    # Get selected transactions
    transactions = db.query(Transaction).filter(
        Transaction.id.in_(transaction_ids),
        Transaction.user_id == current_user.id
    ).order_by(Transaction.date.desc()).all()
    
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    
    # Prepare export data
    export_data = []
    for transaction in transactions:
        category_name = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
            if category:
                category_name = category.name
        
        export_data.append({
            "id": transaction.id,
            "date": transaction.date.strftime('%Y-%m-%d'),
            "time": transaction.date.strftime('%H:%M:%S'),
            "description": transaction.description,
            "merchant": transaction.description.split()[0] if transaction.description else "Unknown",
            "amount": float(transaction.amount),
            "formatted_amount": f"${abs(float(transaction.amount)):,.2f}",
            "type": "Credit" if float(transaction.amount) > 0 else "Debit",
            "category": category_name or "Untagged",
            "account_id": transaction.account_id
        })
    
    filename_base = f"selected_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if format.lower() == "json":
        return {
            "format": "json",
            "data": export_data,
            "count": len(export_data),
            "filename": f"{filename_base}.json"
        }
    elif format.lower() == "excel":
        # For Excel export, return structured data that frontend can convert
        return {
            "format": "excel",
            "data": export_data,
            "count": len(export_data),
            "filename": f"{filename_base}.xlsx",
            "headers": ["Date", "Time", "Merchant", "Description", "Amount", "Type", "Category"]
        }
    else:  # CSV format
        import csv
        import io
        
        output = io.StringIO()
        fieldnames = ["date", "time", "merchant", "description", "amount", "type", "category"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in export_data:
            writer.writerow({
                "date": item["date"],
                "time": item["time"],
                "merchant": item["merchant"],
                "description": item["description"],
                "amount": item["amount"],
                "type": item["type"],
                "category": item["category"]
            })
        
        return {
            "format": "csv",
            "data": output.getvalue(),
            "count": len(export_data),
            "filename": f"{filename_base}.csv"
        }

@router.get("/export")
def export_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None,
    bank_filter: Optional[str] = None,
    has_category: Optional[bool] = None,
    format: str = Query("csv", description="Export format: csv, json, excel"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export transactions in various formats."""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    # Apply filters
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Transaction.date >= start_dt)
    
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Transaction.date <= end_dt)
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Prepare data
    export_data = []
    for transaction in transactions:
        category_name = None
        if transaction.category_id:
            category = db.query(Category).filter(Category.id == transaction.category_id).first()
            if category:
                category_name = category.name
        
        export_data.append({
            "date": transaction.date.strftime('%Y-%m-%d'),
            "description": transaction.description,
            "amount": float(transaction.amount),
            "category": category_name or "Uncategorized",
            "account_id": transaction.account_id
        })
    
    if format.lower() == "csv":
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["date", "description", "amount", "category", "account_id"])
        writer.writeheader()
        writer.writerows(export_data)
        
        return {
            "format": "csv",
            "data": output.getvalue(),
            "filename": f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    
    else:  # JSON format
        return {
            "format": "json",
            "data": export_data,
            "count": len(export_data),
            "filename": f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }