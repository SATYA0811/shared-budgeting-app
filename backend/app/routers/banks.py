"""
Banks Routes - Bank Account & File Management

This module handles:
- Bank account management and connections
- File upload and processing for bank statements
- Bank integration status and sync
- Account balance tracking
- Statement parsing and transaction extraction
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    User, BankAccount, Account, File, FileStatus, FileType,
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
    import logging
    logging.info(f"Getting bank accounts for user {current_user.id}")
    
    accounts = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id
    ).all()
    
    logging.info(f"Found {len(accounts)} bank accounts")
    
    result = []
    for account in accounts:
        logging.info(f"Processing BankAccount: {account.id}, {account.bank_name}, {account.account_type}, {account.account_number}")
        
        # Find the matching Account record for transaction counting
        # BankAccount stores bank details, but transactions reference Account table
        account_last_4 = account.account_number[-4:] if account.account_number and len(account.account_number) >= 4 else "0000"
        account_name = f"{account.bank_name} {account.account_type.title()}".strip()
        
        logging.info(f"Looking for Account with name='{account_name}', last4='{account_last_4}', household_id={current_user.id}")
        
        matching_account = db.query(Account).filter(
            Account.household_id == current_user.id,
            Account.name == account_name,
            Account.last4 == account_last_4
        ).first()
        
        logging.info(f"Matching Account found: {matching_account}")
        
        # Get recent transaction count from the matching Account
        transaction_count = 0
        if matching_account:
            transaction_count = db.query(Transaction).filter(
                Transaction.account_id == matching_account.id,
                Transaction.date >= datetime.now() - timedelta(days=30)
            ).count()
            logging.info(f"Transaction count: {transaction_count}")
        
        # Get last 4 digits of account number if available
        account_display = "****" + (account.account_number[-4:] if account.account_number and len(account.account_number) >= 4 else "0000")
        
        result.append({
            "id": account.id,
            "bank_name": account.bank_name,
            "account_type": account.account_type or "bank",
            "account_number": account_display,
            "balance": float(account.balance) if account.balance else 0.0,  # Use stored balance from PDF
            "currency": "CAD",  # Default currency
            "status": "active",  # Default status
            "last_sync": datetime.now().isoformat(),
            "recent_transactions": transaction_count,
            "created_at": datetime.now().isoformat()
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
        household_id=current_user.id,  # Set household_id to user_id
        bank_name=bank_name,
        account_type=account_type,
        account_number=account_number_last4,  # Store in account_number field
        balance=balance or 0
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
            "account_number": account.account_number or "****0000",
            "balance": float(account.balance),
            "status": "active"  # Default to active since we don't have is_active field
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
        # Cannot delete account with transactions - return error message
        return {"message": "Cannot delete account with transactions", "transaction_count": transaction_count}
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
    
    # Note: No last_sync field in current model, skipping update
    # db.commit()  # No changes to commit
    
    # TODO: Implement actual Plaid sync logic here
    
    return {
        "message": "Account sync initiated",
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

@router.get("/discovered")
def get_discovered_banks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get banks discovered from uploaded files."""
    # For now, return empty since we'll get banks when files are processed by the files router
    # This endpoint will be populated when the file processing system detects banks
    
    # Get existing bank accounts for this user
    discovered_banks = db.query(BankAccount).filter(
        BankAccount.user_id == current_user.id
    ).all()
    
    result = []
    for bank in discovered_banks:
        # Get file count for this user (can't filter by bank_name since File model doesn't have it)
        file_count = db.query(File).filter(
            File.user_id == current_user.id
        ).count()
        
        # Get recent transaction count
        transaction_count = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= datetime.now() - timedelta(days=30)
        ).count()
        
        # Calculate total balance from transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id
        ).all()
        
        balance = sum(float(t.amount) for t in transactions if t.amount)
        
        result.append({
            "id": bank.id,
            "bank_name": bank.bank_name,
            "account_type": bank.account_type or "Checking",
            "account_number": f"****{bank.account_number[-4:] if bank.account_number and len(bank.account_number) >= 4 else '0000'}",
            "balance": balance,
            "currency": "CAD",
            "status": "active",
            "last_sync": bank.last_sync.isoformat() if bank.last_sync else datetime.now().isoformat(),
            "files_uploaded": file_count,
            "recent_transactions": transaction_count,
            "logo": get_bank_logo(bank.bank_name),
            "discovered_from_uploads": True
        })
    
    return {"accounts": result}

def get_bank_logo(bank_name: str) -> str:
    """Get emoji logo for bank."""
    bank_logos = {
        "CIBC": "🏦",
        "Royal Bank of Canada (RBC)": "🏛️", 
        "American Express": "💳",
        "TD Canada Trust": "🏦",
        "Bank of Montreal (BMO)": "🏦",
        "Scotiabank": "🏦",
        "Tangerine": "🍊"
    }
    return bank_logos.get(bank_name, "🏦")

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
        status = "connected"  # Default to connected since we don't have is_active field
        
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