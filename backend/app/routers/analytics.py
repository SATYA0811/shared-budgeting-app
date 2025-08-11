"""
Analytics Routes - Step 6: Analytics & Insights

This module handles:
- Spending trends and pattern analysis over time
- Category-wise spending analysis and breakdowns
- Budget vs actual performance tracking
- Monthly/yearly financial reports
- Personalized financial insights and recommendations

Features:
- Time-based spending trend analysis
- Category performance metrics
- Budget utilization tracking
- Comparative analysis (month-over-month)
- Automated financial insights generation
- Data visualization support
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from calendar import monthrange

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    SpendingTrend, CategoryAnalysis, MonthlyReport,
    BudgetPerformance, FinancialInsight
)
from ..models import User, Transaction, Category, Income, Goal

# Create router
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/spending-trends", response_model=List[SpendingTrend])
def get_spending_trends(
    months: int = Query(12, description="Number of months to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending trends over specified months."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    
    # Query spending by month
    trends = db.query(
        func.strftime('%Y-%m', Transaction.date).label('period'),
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).label('total_spending'),
        func.count(case((Transaction.amount < 0, Transaction.id), else_=None)).label('transaction_count')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(
        func.strftime('%Y-%m', Transaction.date)
    ).order_by('period').all()
    
    result = []
    for trend in trends:
        avg_transaction = float(trend.total_spending / trend.transaction_count) if trend.transaction_count > 0 else 0
        result.append({
            "period": trend.period,
            "total_spending": float(trend.total_spending),
            "transaction_count": trend.transaction_count,
            "average_transaction": avg_transaction
        })
    
    return result

@router.get("/category-analysis", response_model=List[CategoryAnalysis])
def get_category_analysis(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending analysis by category."""
    # Default to last 30 days if no dates provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Convert to datetime objects
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if start_dt > end_dt:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    # Get total spending for percentage calculation
    total_spending = db.query(
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_dt,
        Transaction.date <= end_dt
    ).scalar() or Decimal(0)
    
    # Query category spending
    category_stats = db.query(
        Transaction.category_id,
        Category.name.label('category_name'),
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).label('total_amount'),
        func.count(case((Transaction.amount < 0, Transaction.id), else_=None)).label('transaction_count'),
        Category.default_budget
    ).join(
        Category, Transaction.category_id == Category.id, isouter=True
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_dt,
        Transaction.date <= end_dt
    ).group_by(
        Transaction.category_id, Category.name, Category.default_budget
    ).order_by(func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).desc()).all()
    
    result = []
    for stat in category_stats:
        category_name = stat.category_name or "Uncategorized"
        percentage = float((stat.total_amount / total_spending) * 100) if total_spending > 0 else 0
        avg_per_transaction = float(stat.total_amount / stat.transaction_count) if stat.transaction_count > 0 else 0
        
        budget_utilization = None
        if stat.default_budget and stat.default_budget > 0:
            budget_utilization = float((stat.total_amount / stat.default_budget) * 100)
        
        result.append({
            "category_id": stat.category_id or 0,
            "category_name": category_name,
            "total_amount": float(stat.total_amount),
            "transaction_count": stat.transaction_count,
            "percentage_of_total": percentage,
            "average_per_transaction": avg_per_transaction,
            "budget_amount": float(stat.default_budget) if stat.default_budget else None,
            "budget_utilization": budget_utilization
        })
    
    return result

@router.get("/monthly-report/{year}/{month}", response_model=MonthlyReport)
def get_monthly_report(
    year: int,
    month: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed monthly financial report."""
    # Validate month and year
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 1900 or year > 2100:
        raise HTTPException(status_code=400, detail="Invalid year")
    
    # Get start and end dates for the month
    try:
        start_date = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end_date = datetime(year, month, last_day, 23, 59, 59)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date")
    
    # Get income and expenses for the month
    income_total = db.query(
        func.sum(Income.amount)
    ).filter(
        Income.user_id == current_user.id,
        Income.date >= start_date,
        Income.date <= end_date
    ).scalar() or Decimal(0)
    
    expense_total = db.query(
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or Decimal(0)
    
    net_savings = income_total - expense_total
    savings_rate = float((net_savings / income_total) * 100) if income_total > 0 else 0
    
    # Get top spending categories
    top_categories_query = db.query(
        Transaction.category_id,
        Category.name.label('category_name'),
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).label('total_amount'),
        func.count(case((Transaction.amount < 0, Transaction.id), else_=None)).label('transaction_count')
    ).join(
        Category, Transaction.category_id == Category.id, isouter=True
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.amount < 0
    ).group_by(
        Transaction.category_id, Category.name
    ).order_by(func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0)).desc()).limit(5).all()
    
    top_categories = []
    for cat in top_categories_query:
        category_name = cat.category_name or "Uncategorized"
        percentage = float((cat.total_amount / expense_total) * 100) if expense_total > 0 else 0
        avg_per_transaction = float(cat.total_amount / cat.transaction_count) if cat.transaction_count > 0 else 0
        
        top_categories.append({
            "category_id": cat.category_id or 0,
            "category_name": category_name,
            "total_amount": float(cat.total_amount),
            "transaction_count": cat.transaction_count,
            "percentage_of_total": percentage,
            "average_per_transaction": avg_per_transaction,
            "budget_amount": None,
            "budget_utilization": None
        })
    
    return {
        "month": f"{year}-{month:02d}",
        "year": year,
        "total_income": float(income_total),
        "total_expenses": float(expense_total),
        "net_savings": float(net_savings),
        "savings_rate": savings_rate,
        "top_categories": top_categories
    }

@router.get("/budget-performance", response_model=List[BudgetPerformance])
def get_budget_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget vs actual performance for categories where user has transactions."""
    # Get current month data
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    
    # Check if user has any transactions at all
    user_has_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).first() is not None
    
    # For new users with no transactions, return empty result to avoid showing "predefined data"
    if not user_has_transactions:
        return []
    
    # Get categories with budgets that the user has actually used
    categories_with_spending = db.query(
        Category.id, Category.name, Category.default_budget
    ).join(Transaction).filter(
        Transaction.user_id == current_user.id,
        Category.default_budget.isnot(None),
        Category.default_budget > 0
    ).distinct().all()
    
    result = []
    for category in categories_with_spending:
        # Get actual spending for this category this month
        actual_spending = db.query(
            func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == category.id,
            Transaction.date >= start_of_month
        ).scalar() or Decimal(0)
        
        budget_amount = category.default_budget
        variance = actual_spending - budget_amount
        utilization = float((actual_spending / budget_amount) * 100)
        
        # Determine status
        if utilization <= 80:
            status = "under_budget"
        elif utilization <= 100:
            status = "on_track" 
        else:
            status = "over_budget"
        
        result.append({
            "category_id": category.id,
            "category_name": category.name,
            "budget_amount": float(budget_amount),
            "actual_amount": float(actual_spending),
            "variance": float(variance),
            "utilization_percentage": utilization,
            "status": status
        })
    
    return sorted(result, key=lambda x: x["utilization_percentage"], reverse=True)

@router.get("/insights", response_model=List[FinancialInsight])
def get_financial_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized financial insights and recommendations."""
    insights = []
    now = datetime.now()
    
    # Check for budget overruns
    start_of_month = datetime(now.year, now.month, 1)
    categories_with_budgets = db.query(Category).filter(
        Category.default_budget.isnot(None),
        Category.default_budget > 0
    ).all()
    
    for category in categories_with_budgets:
        actual_spending = db.query(
            func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.category_id == category.id,
            Transaction.date >= start_of_month
        ).scalar() or Decimal(0)
        
        utilization = float((actual_spending / category.default_budget) * 100)
        
        if utilization > 100:
            insights.append({
                "type": "warning",
                "title": f"Budget Exceeded: {category.name}",
                "description": f"You've spent {utilization:.1f}% of your {category.name} budget this month.",
                "category": category.name,
                "amount": float(actual_spending - category.default_budget)
            })
        elif utilization > 80:
            insights.append({
                "type": "suggestion",
                "title": f"Approaching Budget Limit: {category.name}",
                "description": f"You've used {utilization:.1f}% of your {category.name} budget. Consider monitoring your spending.",
                "category": category.name,
                "amount": float(actual_spending)
            })
    
    # Check for goals achievements
    achieved_goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.current_amount >= Goal.target_amount
    ).all()
    
    for goal in achieved_goals:
        insights.append({
            "type": "achievement", 
            "title": f"Goal Achieved: {goal.name}",
            "description": f"Congratulations! You've reached your goal of ${goal.target_amount}.",
            "category": "Goals",
            "amount": float(goal.current_amount)
        })
    
    # Spending pattern insights
    last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
    last_month_end = start_of_month - timedelta(days=1)
    
    current_month_spending = db.query(
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_of_month
    ).scalar() or Decimal(0)
    
    last_month_spending = db.query(
        func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= last_month_start,
        Transaction.date <= last_month_end
    ).scalar() or Decimal(0)
    
    if last_month_spending > 0:
        spending_change = ((current_month_spending - last_month_spending) / last_month_spending) * 100
        
        if spending_change > 20:
            insights.append({
                "type": "warning",
                "title": "Increased Spending Detected",
                "description": f"Your spending has increased by {spending_change:.1f}% compared to last month.",
                "category": "Overall",
                "amount": float(current_month_spending - last_month_spending)
            })
        elif spending_change < -10:
            insights.append({
                "type": "achievement",
                "title": "Great Job Saving!",
                "description": f"You've reduced your spending by {abs(spending_change):.1f}% compared to last month.",
                "category": "Overall", 
                "amount": float(last_month_spending - current_month_spending)
            })
    
    return insights