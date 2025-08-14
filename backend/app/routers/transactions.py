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
from sqlalchemy import and_, or_, String, func, case
from typing import Optional, List
from datetime import datetime, timedelta

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

@router.get("/export")
def export_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None,
    format: str = Query("csv", description="Export format: csv or json"),
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