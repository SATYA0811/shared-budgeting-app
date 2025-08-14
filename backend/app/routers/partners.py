"""
Partners Routes - Shared Analytics & Household Management

This module handles:
- Shared household analytics and insights
- Partner collaboration and expense sharing
- Combined spending analysis across household members
- Shared goals and savings tracking
- Household member management
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    User, Transaction, Category, Goal, Income, 
    Household, HouseholdUser, SharedExpense, SharedExpenseSplit,
    BankAccount, GoalContribution
)

# Create router
router = APIRouter(prefix="/partners", tags=["Partners"])

@router.get("/household-overview")
def get_household_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get household overview with all members' financial data."""
    # Get user's household
    household_membership = db.query(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).first()
    
    if not household_membership:
        raise HTTPException(status_code=404, detail="User not part of any household")
    
    household = household_membership.household
    
    # Get all household members
    members = db.query(HouseholdUser).join(User).filter(
        HouseholdUser.household_id == household.id
    ).all()
    
    # Calculate totals for each member
    member_data = []
    total_household_spending = 0
    total_household_income = 0
    
    for member in members:
        user = member.user
        
        # Get member's spending (last 30 days)
        member_spending = db.query(
            func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
        ).filter(
            Transaction.user_id == user.id,
            Transaction.date >= datetime.now() - timedelta(days=30)
        ).scalar() or 0
        
        # Get member's income (last 30 days)
        member_income = db.query(
            func.sum(Income.amount)
        ).filter(
            Income.user_id == user.id,
            Income.date >= datetime.now() - timedelta(days=30)
        ).scalar() or 0
        
        member_data.append({
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "role": member.role.value,
            "total_spent": float(member_spending),
            "total_income": float(member_income),
            "is_current_user": user.id == current_user.id
        })
        
        total_household_spending += float(member_spending)
        total_household_income += float(member_income)
    
    # Get shared expenses
    shared_expenses = db.query(SharedExpense).filter(
        SharedExpense.household_id == household.id
    ).count()
    
    return {
        "household": {
            "id": household.id,
            "name": household.name,
            "created_at": household.created_at
        },
        "members": member_data,
        "totals": {
            "household_spending": total_household_spending,
            "household_income": total_household_income,
            "net_savings": total_household_income - total_household_spending,
            "shared_expenses_count": shared_expenses
        }
    }

@router.get("/spending-comparison")
def get_spending_comparison(
    months: int = Query(6, description="Number of months to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending comparison between household members over time."""
    # Get household members
    household_membership = db.query(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).first()
    
    if not household_membership:
        raise HTTPException(status_code=404, detail="User not part of any household")
    
    members = db.query(HouseholdUser).join(User).filter(
        HouseholdUser.household_id == household_membership.household_id
    ).all()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    
    # Get monthly spending for each member
    comparison_data = []
    
    for i in range(months):
        month_start = (end_date - timedelta(days=30 * (i + 1))).replace(day=1)
        month_end = (month_start.replace(month=month_start.month + 1) - timedelta(days=1)) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
        
        month_data = {
            "month": month_start.strftime("%Y-%m"),
            "members": []
        }
        
        total_shared = 0
        
        for member in members:
            user = member.user
            
            # Get individual spending
            individual_spending = db.query(
                func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
            ).filter(
                Transaction.user_id == user.id,
                Transaction.date >= month_start,
                Transaction.date <= month_end
            ).scalar() or 0
            
            month_data["members"].append({
                "user_id": user.id,
                "name": user.name,
                "individual_spending": float(individual_spending),
                "is_current_user": user.id == current_user.id
            })
        
        # Get shared expenses for the month
        shared_expenses = db.query(
            func.sum(SharedExpense.total_amount)
        ).filter(
            SharedExpense.household_id == household_membership.household_id,
            SharedExpense.created_at >= month_start,
            SharedExpense.created_at <= month_end
        ).scalar() or 0
        
        month_data["shared_expenses"] = float(shared_expenses)
        comparison_data.append(month_data)
    
    return {"comparison": list(reversed(comparison_data))}

@router.get("/category-breakdown")
def get_category_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed category breakdown for household members."""
    # Get household
    household_membership = db.query(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).first()
    
    if not household_membership:
        raise HTTPException(status_code=404, detail="User not part of any household")
    
    members = db.query(HouseholdUser).join(User).filter(
        HouseholdUser.household_id == household_membership.household_id
    ).all()
    
    # Get last 30 days
    start_date = datetime.now() - timedelta(days=30)
    
    # Get all categories with spending
    categories = db.query(Category).all()
    
    breakdown_data = []
    
    for category in categories:
        category_data = {
            "name": category.name,
            "category_id": category.id,
            "members": [],
            "total": 0
        }
        
        for member in members:
            user = member.user
            
            # Get member's spending in this category
            member_spending = db.query(
                func.sum(case((Transaction.amount < 0, Transaction.amount * -1), else_=0))
            ).filter(
                Transaction.user_id == user.id,
                Transaction.category_id == category.id,
                Transaction.date >= start_date
            ).scalar() or 0
            
            if member_spending > 0:
                category_data["members"].append({
                    "user_id": user.id,
                    "name": user.name,
                    "amount": float(member_spending),
                    "is_current_user": user.id == current_user.id
                })
                category_data["total"] += float(member_spending)
        
        # Only include categories with spending
        if category_data["total"] > 0:
            breakdown_data.append(category_data)
    
    # Sort by total spending
    breakdown_data.sort(key=lambda x: x["total"], reverse=True)
    
    return {"categories": breakdown_data}

@router.get("/shared-expenses")
def get_shared_expenses(
    limit: int = Query(50, description="Number of expenses to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get shared expenses for the household."""
    # Get household
    household_membership = db.query(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).first()
    
    if not household_membership:
        raise HTTPException(status_code=404, detail="User not part of any household")
    
    # Get shared expenses with details
    shared_expenses = db.query(SharedExpense).join(Transaction).join(User).filter(
        SharedExpense.household_id == household_membership.household_id
    ).order_by(SharedExpense.created_at.desc()).limit(limit).all()
    
    result = []
    for expense in shared_expenses:
        # Get splits
        splits = db.query(SharedExpenseSplit).join(User).filter(
            SharedExpenseSplit.shared_expense_id == expense.id
        ).all()
        
        # Get category name if available
        category_name = None
        if expense.transaction.category_id:
            category = db.query(Category).filter(
                Category.id == expense.transaction.category_id
            ).first()
            if category:
                category_name = category.name
        
        result.append({
            "id": expense.id,
            "description": expense.transaction.description,
            "amount": float(expense.total_amount),
            "date": expense.transaction.date,
            "paid_by": {
                "user_id": expense.paid_by.id,
                "name": expense.paid_by.name
            },
            "category": category_name or "Uncategorized",
            "split_method": expense.split_method,
            "splits": [
                {
                    "user_id": split.user.id,
                    "user_name": split.user.name,
                    "amount": float(split.amount),
                    "is_paid": split.is_paid
                }
                for split in splits
            ]
        })
    
    return {"shared_expenses": result}

@router.get("/joint-goals")
def get_joint_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get joint savings goals for household members."""
    # Get household
    household_membership = db.query(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).first()
    
    if not household_membership:
        raise HTTPException(status_code=404, detail="User not part of any household")
    
    members = db.query(HouseholdUser).join(User).filter(
        HouseholdUser.household_id == household_membership.household_id
    ).all()
    
    member_ids = [member.user_id for member in members]
    
    # Get goals from all household members (could be joint goals or individual goals we want to show)
    goals = db.query(Goal).filter(
        Goal.user_id.in_(member_ids),
        Goal.status == 'active'
    ).all()
    
    joint_goals = []
    for goal in goals:
        # Get contributions from all household members
        contributions = db.query(GoalContribution).join(User).filter(
            GoalContribution.goal_id == goal.id,
            GoalContribution.user_id.in_(member_ids)
        ).all()
        
        # Group contributions by user
        contributors = {}
        for contrib in contributions:
            if contrib.user_id not in contributors:
                contributors[contrib.user_id] = {
                    "user_name": contrib.user.name,
                    "total_contributed": 0
                }
            contributors[contrib.user_id]["total_contributed"] += float(contrib.amount)
        
        joint_goals.append({
            "id": goal.id,
            "name": goal.name,
            "description": goal.description,
            "target_amount": float(goal.target_amount),
            "current_amount": float(goal.current_amount),
            "target_date": goal.target_date,
            "category": goal.category.value if goal.category else None,
            "priority": goal.priority.value if goal.priority else None,
            "owner": {
                "user_id": goal.user_id,
                "name": goal.user.name
            },
            "contributors": list(contributors.values())
        })
    
    return {"joint_goals": joint_goals}

@router.post("/shared-expenses")
def create_shared_expense(
    transaction_id: int,
    split_method: str = "equal",
    splits: Optional[List[dict]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a shared expense from an existing transaction."""
    # Get household
    household_membership = db.query(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).first()
    
    if not household_membership:
        raise HTTPException(status_code=404, detail="User not part of any household")
    
    # Get transaction
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Create shared expense
    shared_expense = SharedExpense(
        household_id=household_membership.household_id,
        transaction_id=transaction_id,
        paid_by_user_id=current_user.id,
        total_amount=abs(transaction.amount),
        split_method=split_method
    )
    
    db.add(shared_expense)
    db.commit()
    db.refresh(shared_expense)
    
    # Create splits
    if split_method == "equal" and not splits:
        # Equal split among all household members
        members = db.query(HouseholdUser).filter(
            HouseholdUser.household_id == household_membership.household_id
        ).all()
        
        amount_per_person = abs(transaction.amount) / len(members)
        
        for member in members:
            split = SharedExpenseSplit(
                shared_expense_id=shared_expense.id,
                user_id=member.user_id,
                amount=amount_per_person,
                percentage=100 / len(members)
            )
            db.add(split)
    
    elif splits:
        # Custom splits
        for split_data in splits:
            split = SharedExpenseSplit(
                shared_expense_id=shared_expense.id,
                user_id=split_data["user_id"],
                amount=split_data["amount"],
                percentage=split_data.get("percentage")
            )
            db.add(split)
    
    db.commit()
    
    return {"message": "Shared expense created successfully", "shared_expense_id": shared_expense.id}

@router.post("/invite-partner")
def invite_partner(
    email: str,
    role: str = "member",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a partner to join the household."""
    # Get household
    household_membership = db.query(HouseholdUser).filter(
        HouseholdUser.user_id == current_user.id
    ).first()
    
    if not household_membership:
        raise HTTPException(status_code=404, detail="User not part of any household")
    
    # Check if user is admin or owner
    if household_membership.role.value not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Only household admins can invite members")
    
    # Check if user exists
    invited_user = db.query(User).filter(User.email == email).first()
    if not invited_user:
        raise HTTPException(status_code=404, detail="User not found. They need to register first.")
    
    # Check if already a member
    existing_membership = db.query(HouseholdUser).filter(
        HouseholdUser.household_id == household_membership.household_id,
        HouseholdUser.user_id == invited_user.id
    ).first()
    
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a household member")
    
    # Create membership
    new_membership = HouseholdUser(
        household_id=household_membership.household_id,
        user_id=invited_user.id,
        role=role
    )
    
    db.add(new_membership)
    db.commit()
    
    # TODO: Send invitation email notification
    
    return {
        "message": f"Successfully invited {invited_user.name} to the household",
        "invited_user": {
            "id": invited_user.id,
            "name": invited_user.name,
            "email": invited_user.email,
            "role": role
        }
    }