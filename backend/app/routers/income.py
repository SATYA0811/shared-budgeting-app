"""
Income Routes - Step 4: Income & Expense Tracking

This module handles:
- Income tracking and management (CRUD operations)
- Income source categorization and notes
- Financial summary calculations (income vs expenses)
- Monthly/yearly income reporting
- Budget vs actual analysis with income data

Features:
- Multiple income sources support
- Date-based income filtering
- Income vs expense comparisons
- Financial health metrics
- User-based data isolation
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    IncomeCreate, IncomeUpdate, IncomeResponse,
    FinancialSummary, ExpenseSummary, MonthlyTrend
)
from ..models import User, Income, Transaction, Category

# Create router
router = APIRouter(prefix="/income", tags=["Income"])

@router.get("", response_model=List[IncomeResponse])
def get_income(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's income records with optional filtering."""
    query = db.query(Income).filter(Income.user_id == current_user.id)
    
    # Apply filters
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Income.date >= start_dt)
    
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        query = query.filter(Income.date <= end_dt)
    
    if source:
        query = query.filter(Income.source.contains(source))
    
    income_records = query.order_by(Income.date.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": record.id,
        "date": record.date,
        "amount": float(record.amount),
        "source": record.source,
        "notes": record.notes,
        "user_id": record.user_id
    } for record in income_records]

@router.post("", response_model=IncomeResponse)
def create_income(
    income: IncomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new income record."""
    # Validate amount is positive
    if income.amount <= 0:
        raise HTTPException(status_code=400, detail="Income amount must be positive")
    
    db_income = Income(
        date=income.date,
        amount=income.amount,
        source=income.source,
        notes=income.notes,
        user_id=current_user.id
    )
    
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    
    return {
        "id": db_income.id,
        "date": db_income.date,
        "amount": float(db_income.amount),
        "source": db_income.source,
        "notes": db_income.notes,
        "user_id": db_income.user_id
    }

@router.get("/{income_id}", response_model=IncomeResponse)
def get_income_record(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific income record."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id
    ).first()
    
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    
    return {
        "id": income.id,
        "date": income.date,
        "amount": float(income.amount),
        "source": income.source,
        "notes": income.notes,
        "user_id": income.user_id
    }

@router.put("/{income_id}", response_model=IncomeResponse)
def update_income(
    income_id: int,
    income_update: IncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an income record."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id
    ).first()
    
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    
    # Validate amount if being updated
    if income_update.amount is not None and income_update.amount <= 0:
        raise HTTPException(status_code=400, detail="Income amount must be positive")
    
    # Update fields
    update_data = income_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(income, field, value)
    
    db.commit()
    db.refresh(income)
    
    return {
        "id": income.id,
        "date": income.date,
        "amount": float(income.amount),
        "source": income.source,
        "notes": income.notes,
        "user_id": income.user_id
    }

@router.delete("/{income_id}")
def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an income record."""
    income = db.query(Income).filter(
        Income.id == income_id,
        Income.user_id == current_user.id
    ).first()
    
    if not income:
        raise HTTPException(status_code=404, detail="Income record not found")
    
    db.delete(income)
    db.commit()
    
    return {"message": "Income record deleted successfully"}

@router.get("/summary/financial", response_model=FinancialSummary)
def get_financial_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get financial summary for a date range."""
    # Default to current month if no dates provided
    if not start_date or not end_date:
        now = datetime.now()
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get total income
    total_income = db.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        Income.date >= start_dt,
        Income.date <= end_dt
    ).scalar() or Decimal(0)
    
    # Get total expenses (negative transactions)
    total_expenses = db.query(
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_dt,
        Transaction.date <= end_dt
    ).scalar() or Decimal(0)
    
    net_balance = total_income - total_expenses
    
    return {
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_balance": float(net_balance),
        "period_start": start_dt,
        "period_end": end_dt
    }

@router.get("/summary/expenses", response_model=List[ExpenseSummary])
def get_expense_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get expense summary by category."""
    # Default to current month if no dates provided
    if not start_date or not end_date:
        now = datetime.now()
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Get expense summary by category
    expense_summary = db.query(
        Category.name.label('category_name'),
        Category.id.label('category_id'),
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).label('total_amount'),
        func.count(case((Transaction.amount < 0, Transaction.id), else_=None)).label('transaction_count'),
        Category.default_budget.label('budget_amount')
    ).join(
        Transaction, Category.id == Transaction.category_id, isouter=True
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_dt,
        Transaction.date <= end_dt,
        Transaction.amount < 0
    ).group_by(
        Category.id, Category.name, Category.default_budget
    ).order_by(
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).desc()
    ).all()
    
    result = []
    for summary in expense_summary:
        budget_remaining = None
        if summary.budget_amount:
            budget_remaining = float(summary.budget_amount - summary.total_amount)
        
        result.append({
            "category_name": summary.category_name or "Uncategorized",
            "category_id": summary.category_id or 0,
            "total_amount": float(summary.total_amount),
            "transaction_count": summary.transaction_count,
            "budget_amount": float(summary.budget_amount) if summary.budget_amount else None,
            "budget_remaining": budget_remaining
        })
    
    return result

@router.get("/trends/monthly", response_model=List[MonthlyTrend])
def get_monthly_trends(
    months: int = Query(12, description="Number of months to include"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly income and expense trends."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    
    # Get monthly income and expenses
    monthly_data = db.query(
        func.strftime('%Y-%m', Income.date).label('month_year'),
        func.sum(Income.amount).label('income')
    ).filter(
        Income.user_id == current_user.id,
        Income.date >= start_date
    ).group_by(
        func.strftime('%Y-%m', Income.date)
    ).subquery()
    
    # Get monthly expenses
    monthly_expenses = db.query(
        func.strftime('%Y-%m', Transaction.date).label('month_year'),
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).label('expenses')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date
    ).group_by(
        func.strftime('%Y-%m', Transaction.date)
    ).subquery()
    
    # Combine income and expenses
    # This is a simplified version - in production you'd want a proper join
    result = []
    for i in range(months):
        month_date = end_date - timedelta(days=30 * i)
        month_str = month_date.strftime('%Y-%m')
        year = month_date.year
        
        # Get income for this month
        income = db.query(func.sum(Income.amount)).filter(
            Income.user_id == current_user.id,
            func.strftime('%Y-%m', Income.date) == month_str
        ).scalar() or Decimal(0)
        
        # Get expenses for this month
        expenses = db.query(
            func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
        ).filter(
            Transaction.user_id == current_user.id,
            func.strftime('%Y-%m', Transaction.date) == month_str
        ).scalar() or Decimal(0)
        
        net = income - expenses
        
        result.append({
            "month": month_str,
            "year": year,
            "income": float(income),
            "expenses": float(expenses),
            "net": float(net)
        })
    
    return sorted(result, key=lambda x: x["month"])