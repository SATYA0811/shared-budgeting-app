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

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    TransactionCreate, TransactionUpdate, TransactionResponse, 
    CategorizeTransactionRequest
)
from ..models import User, Transaction, Category

# Create router
router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transactions with optional filtering."""
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
    
    # Get transactions with category names
    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()
    
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