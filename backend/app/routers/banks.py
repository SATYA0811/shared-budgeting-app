"""
Banks Routes - Bank Account & File Management

This module handles:
- Bank account management and connections
- File upload and processing for bank statements
- Bank integration status and sync
- Account balance tracking
- Statement parsing and transaction extraction
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File as FastAPIFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
import os
import io
import json
import uuid
from pathlib import Path

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    User, BankAccount, File, FileStatus, FileType,
    Transaction, Category
)

# Create router
router = APIRouter(prefix="/banks", tags=["Banks"])

@router.get("/accounts")
def get_bank_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's bank accounts."""
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id
    ).order_by(BankAccount.created_at.desc()).all()
    
    result = []
    for account in accounts:
        # Get recent transaction count
        transaction_count = db.query(Transaction).filter(
            Transaction.bank_account_id == account.id,
            Transaction.date >= datetime.now() - timedelta(days=30)
        ).count()
        
        result.append({
            "id": account.id,
            "bank_name": account.bank_name,
            "account_type": account.account_type,
            "account_number": f"****{account.account_number_last4}",
            "balance": float(account.balance),
            "currency": account.currency,
            "status": account.is_active,
            "last_sync": account.last_sync,
            "recent_transactions": transaction_count,
            "created_at": account.created_at
        })
    
    return {"accounts": result}

@router.post("/accounts")
def create_bank_account(
    bank_name: str,
    account_type: str,
    account_number_last4: str,
    balance: Optional[float] = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new bank account."""
    # Validate account type
    valid_types = ["Checking", "Savings", "Credit Card", "Investment", "Loan"]
    if account_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid account type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create account
    account = BankAccount(
        user_id=current_user.id,
        bank_name=bank_name,
        account_type=account_type,
        account_number_last4=account_number_last4,
        balance=balance or 0,
        is_active="active",
        last_sync=datetime.now()
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    return {
        "message": "Bank account created successfully",
        "account": {
            "id": account.id,
            "bank_name": account.bank_name,
            "account_type": account.account_type,
            "account_number": f"****{account.account_number_last4}",
            "balance": float(account.balance),
            "status": account.is_active
        }
    }

@router.put("/accounts/{account_id}")
def update_bank_account(
    account_id: int,
    bank_name: Optional[str] = None,
    account_type: Optional[str] = None,
    balance: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a bank account."""
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Update fields
    if bank_name:
        account.bank_name = bank_name
    if account_type:
        valid_types = ["Checking", "Savings", "Credit Card", "Investment", "Loan"]
        if account_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid account type. Must be one of: {', '.join(valid_types)}"
            )
        account.account_type = account_type
    if balance is not None:
        account.balance = balance
    
    account.updated_at = datetime.now()
    db.commit()
    
    return {"message": "Bank account updated successfully"}

@router.delete("/accounts/{account_id}")
def delete_bank_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bank account."""
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Check if account has transactions
    transaction_count = db.query(Transaction).filter(
        Transaction.bank_account_id == account.id
    ).count()
    
    if transaction_count > 0:
        # Soft delete - mark as inactive instead of deleting
        account.is_active = "inactive"
        db.commit()
        return {"message": "Bank account deactivated (has transactions)"}
    else:
        # Hard delete if no transactions
        db.delete(account)
        db.commit()
        return {"message": "Bank account deleted successfully"}

@router.post("/accounts/{account_id}/sync")
def sync_bank_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually sync a bank account (placeholder for Plaid integration)."""
    account = db.query(BankAccount).filter(
        BankAccount.id == account_id,
        BankAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    # Update last sync time
    account.last_sync = datetime.now()
    account.is_active = "active"
    db.commit()
    
    # TODO: Implement actual Plaid sync logic here
    
    return {
        "message": "Account sync initiated",
        "last_sync": account.last_sync,
        "status": "Sync completed"
    }

# File Management Endpoints

@router.get("/files")
def get_uploaded_files(
    limit: int = Query(50, description="Number of files to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's uploaded files."""
    query = db.query(File).filter(File.user_id == current_user.id)
    
    if status_filter:
        try:
            status_enum = FileStatus(status_filter)
            query = query.filter(File.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status filter")
    
    files = query.order_by(File.uploaded_at.desc()).limit(limit).all()
    
    result = []
    for file in files:
        result.append({
            "id": file.id,
            "filename": file.original_filename or file.filename,
            "file_size": f"{file.file_size / 1024:.1f} KB" if file.file_size < 1024*1024 else f"{file.file_size / (1024*1024):.1f} MB",
            "file_type": file.file_type.value if file.file_type else "unknown",
            "bank_name": file.bank_name or "Manual Upload",
            "status": file.status.value,
            "transactions_found": file.transactions_found or 0,
            "uploaded_at": file.uploaded_at,
            "processed_at": file.processed_at,
            "error_message": file.error_message
        })
    
    return {"files": result}

@router.post("/files/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    bank_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a bank statement file."""
    # Validate file type
    allowed_extensions = {".pdf", ".csv", ".xlsx", ".xls"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Determine file type
    file_type = FileType.csv
    if file_ext == ".pdf":
        file_type = FileType.bank_statement
    elif file_ext in [".xlsx", ".xls"]:
        file_type = FileType.excel
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Create unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    # TODO: Save to actual file storage (S3, local filesystem, etc.)
    # For now, we'll just store metadata
    
    # Create file record
    db_file = File(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_size=file_size,
        file_type=file_type,
        bank_name=bank_name,
        status=FileStatus.uploaded,
        transactions_found=0
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # TODO: Queue for processing
    # For demonstration, we'll simulate processing
    await simulate_file_processing(db_file, db, content)
    
    return {
        "message": "File uploaded successfully",
        "file_id": db_file.id,
        "filename": file.filename,
        "status": "uploaded"
    }

async def simulate_file_processing(db_file: File, db: Session, content: bytes):
    """Simulate file processing (replace with actual implementation)."""
    try:
        # Update status to processing
        db_file.status = FileStatus.parsing
        db.commit()
        
        # Simulate parsing delay
        import asyncio
        await asyncio.sleep(1)
        
        # Mock transaction extraction
        if db_file.file_type == FileType.csv:
            # Simulate CSV parsing
            transactions_found = simulate_csv_parsing(content, db_file, db)
        elif db_file.file_type == FileType.bank_statement:
            # Simulate PDF parsing
            transactions_found = simulate_pdf_parsing(content, db_file, db)
        else:
            transactions_found = 0
        
        # Update file status
        db_file.status = FileStatus.parsed
        db_file.transactions_found = transactions_found
        db_file.processed_at = datetime.now()
        db.commit()
        
    except Exception as e:
        # Handle processing errors
        db_file.status = FileStatus.error
        db_file.error_message = str(e)
        db.commit()

def simulate_csv_parsing(content: bytes, db_file: File, db: Session) -> int:
    """Simulate CSV file parsing and transaction creation."""
    try:
        # Decode CSV content
        csv_content = content.decode('utf-8')
        lines = csv_content.strip().split('\n')
        
        if len(lines) < 2:  # Need header + at least one data row
            return 0
        
        # Skip header and process data rows
        transactions_created = 0
        for line in lines[1:6]:  # Limit to first 5 transactions for demo
            try:
                parts = line.split(',')
                if len(parts) >= 3:
                    # Assume format: Date, Description, Amount
                    date_str = parts[0].strip('"')
                    description = parts[1].strip('"')
                    amount_str = parts[2].strip('"')
                    
                    # Parse date
                    try:
                        transaction_date = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        transaction_date = datetime.strptime(date_str, '%m/%d/%Y')
                    
                    # Parse amount
                    amount = float(amount_str.replace('$', '').replace(',', ''))
                    
                    # Create transaction
                    transaction = Transaction(
                        user_id=db_file.user_id,
                        date=transaction_date,
                        description=description,
                        amount=amount,
                        source_file_id=db_file.id
                    )
                    
                    db.add(transaction)
                    transactions_created += 1
                    
            except Exception as e:
                continue  # Skip invalid rows
        
        db.commit()
        return transactions_created
        
    except Exception:
        return 0

def simulate_pdf_parsing(content: bytes, db_file: File, db: Session) -> int:
    """Simulate PDF file parsing and transaction creation."""
    # For demo purposes, create some mock transactions
    try:
        mock_transactions = [
            {"date": "2025-08-01", "description": "Grocery Store", "amount": -125.50},
            {"date": "2025-08-02", "description": "Gas Station", "amount": -45.00},
            {"date": "2025-08-03", "description": "Salary Deposit", "amount": 3200.00},
            {"date": "2025-08-04", "description": "Electric Bill", "amount": -89.99},
        ]
        
        transactions_created = 0
        for mock_txn in mock_transactions:
            transaction = Transaction(
                user_id=db_file.user_id,
                date=datetime.strptime(mock_txn["date"], '%Y-%m-%d'),
                description=mock_txn["description"],
                amount=mock_txn["amount"],
                source_file_id=db_file.id
            )
            
            db.add(transaction)
            transactions_created += 1
        
        db.commit()
        return transactions_created
        
    except Exception:
        return 0

@router.delete("/files/{file_id}")
def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an uploaded file."""
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if file has associated transactions
    transaction_count = db.query(Transaction).filter(
        Transaction.source_file_id == file.id
    ).count()
    
    if transaction_count > 0:
        return {
            "message": "Cannot delete file with associated transactions",
            "transaction_count": transaction_count
        }
    
    # TODO: Delete actual file from storage
    
    db.delete(file)
    db.commit()
    
    return {"message": "File deleted successfully"}

@router.get("/files/{file_id}/transactions")
def get_file_transactions(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions extracted from a file."""
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get transactions from this file
    transactions = db.query(Transaction).filter(
        Transaction.source_file_id == file.id
    ).order_by(Transaction.date.desc()).all()
    
    result = []
    for txn in transactions:
        category_name = None
        if txn.category_id:
            category = db.query(Category).filter(Category.id == txn.category_id).first()
            if category:
                category_name = category.name
        
        result.append({
            "id": txn.id,
            "date": txn.date,
            "description": txn.description,
            "amount": float(txn.amount),
            "category_name": category_name,
            "category_id": txn.category_id
        })
    
    return {
        "file": {
            "id": file.id,
            "filename": file.original_filename,
            "status": file.status.value,
            "bank_name": file.bank_name
        },
        "transactions": result
    }

@router.get("/integration-status")
def get_integration_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get bank integration status."""
    # Get user's accounts and their status
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id
    ).all()
    
    integrations = []
    for account in accounts:
        status = "connected" if account.is_active == "active" else "error"
        
        integrations.append({
            "bank_name": account.bank_name,
            "account_type": account.account_type,
            "status": status,
            "last_sync": account.last_sync,
            "account_id": account.id
        })
    
    # Only show available integrations if user has connected accounts
    # This avoids showing "predefined data" to new users
    available_integrations = []
    if integrations:  # User has connected accounts, show additional options
        available_banks = [
            {"name": "Bank of America", "status": "available"},
            {"name": "Citi Bank", "status": "available"},
            {"name": "American Express", "status": "available"},
            {"name": "Discover", "status": "available"}
        ]
        
        # Filter out banks that are already connected
        connected_banks = [acc["bank_name"] for acc in integrations]
        available_integrations = [
            bank for bank in available_banks 
            if bank["name"] not in connected_banks
        ]
    
    return {
        "connected_accounts": integrations,
        "available_integrations": available_integrations,
        "plaid_enabled": False,  # TODO: Check actual Plaid configuration
        "open_banking_enabled": False  # TODO: Check Open Banking configuration
    }