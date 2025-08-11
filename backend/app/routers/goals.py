"""
Goals Routes - Enhanced Investment & Savings Tracking

This module handles:
- Goal creation, tracking, and management with categories and priorities
- Comprehensive goal analytics and insights
- Goal contribution logging and tracking
- Achievement detection and celebration
- Goal recommendations and optimization
- Monthly contribution analysis

Features:
- Target amount and date tracking with categories
- Progress percentage calculations and projections
- Contribution history and analytics
- Achievement status monitoring with notifications
- Goal recommendations and optimization tips
- Category-based goal organization
- Priority management and tracking
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

from ..database import get_db
from ..auth import get_current_user
from ..models import (
    User, Goal, GoalContribution, GoalCategory, GoalStatus, GoalPriority,
    Transaction, Income
)

# Create router
router = APIRouter(prefix="/goals", tags=["Goals"])

def calculate_goal_progress(goal: Goal, db: Session):
    """Calculate comprehensive progress statistics for a goal."""
    now = datetime.now()
    
    # Calculate progress percentage
    progress_percentage = float((goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0.0
    
    # Calculate amount remaining
    amount_remaining = goal.target_amount - goal.current_amount
    
    # Calculate days remaining
    days_remaining = (goal.target_date - now).days if goal.target_date > now else 0
    months_remaining = max(1, round(days_remaining / 30))
    
    # Check if achieved
    is_achieved = goal.current_amount >= goal.target_amount
    
    # Calculate required monthly contribution to reach goal
    monthly_target = float(amount_remaining / months_remaining) if months_remaining > 0 and amount_remaining > 0 else 0
    
    # Get actual contribution history
    total_contributions = db.query(
        func.sum(GoalContribution.amount)
    ).filter(GoalContribution.goal_id == goal.id).scalar() or 0
    
    # Calculate monthly contributions (last 6 months)
    six_months_ago = now - timedelta(days=180)
    recent_contributions = db.query(
        func.sum(GoalContribution.amount)
    ).filter(
        GoalContribution.goal_id == goal.id,
        GoalContribution.date >= six_months_ago
    ).scalar() or 0
    
    avg_monthly_contribution = float(recent_contributions / 6)
    
    # Determine goal status
    status = "active"
    if is_achieved:
        status = "completed"
    elif goal.target_date < now and not is_achieved:
        status = "overdue"
    elif days_remaining < 30 and progress_percentage < 80:
        status = "at_risk"
    
    return {
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "target_amount": float(goal.target_amount),
        "current_amount": float(goal.current_amount),
        "monthly_contribution": float(goal.monthly_contribution),
        "target_date": goal.target_date.isoformat(),
        "category": goal.category.value if goal.category else None,
        "status": status,
        "priority": goal.priority.value if goal.priority else "medium",
        "recurrence": goal.recurrence,
        "created_at": goal.created_at.isoformat(),
        "user_id": goal.user_id,
        "progress_percentage": progress_percentage,
        "amount_remaining": float(amount_remaining),
        "days_remaining": days_remaining,
        "months_remaining": months_remaining,
        "monthly_target": monthly_target,
        "avg_monthly_contribution": avg_monthly_contribution,
        "total_contributions": float(total_contributions),
        "is_achieved": is_achieved,
        "is_on_track": avg_monthly_contribution >= monthly_target if monthly_target > 0 else True
    }

@router.post("")
def create_goal(
    name: str,
    target_amount: float,
    target_date: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = "medium",
    monthly_contribution: Optional[float] = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new financial goal with enhanced features."""
    # Validate target amount is positive
    if target_amount <= 0:
        raise HTTPException(status_code=400, detail="Target amount must be positive")
    
    # Parse and validate target date
    try:
        target_date_obj = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid target date format")
    
    if target_date_obj <= datetime.now():
        raise HTTPException(status_code=400, detail="Target date must be in the future")
    
    # Validate category
    goal_category = None
    if category:
        try:
            goal_category = GoalCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid goal category")
    
    # Validate priority
    goal_priority = GoalPriority.medium
    if priority:
        try:
            goal_priority = GoalPriority(priority)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid goal priority")
    
    db_goal = Goal(
        name=name,
        description=description,
        target_amount=target_amount,
        current_amount=0,
        monthly_contribution=monthly_contribution or 0,
        target_date=target_date_obj,
        category=goal_category,
        priority=goal_priority,
        status=GoalStatus.active,
        user_id=current_user.id
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return calculate_goal_progress(db_goal, db)

@router.get("")
def get_goals(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, paused"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's goals with filtering and progress calculations."""
    query = db.query(Goal).filter(Goal.user_id == current_user.id)
    
    if status:
        try:
            status_enum = GoalStatus(status)
            query = query.filter(Goal.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status filter")
    
    if category:
        try:
            category_enum = GoalCategory(category)
            query = query.filter(Goal.category == category_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category filter")
    
    if priority:
        try:
            priority_enum = GoalPriority(priority)
            query = query.filter(Goal.priority == priority_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid priority filter")
    
    goals = query.order_by(Goal.priority.desc(), Goal.created_at.desc()).all()
    
    return {"goals": [calculate_goal_progress(goal, db) for goal in goals]}

@router.get("/summary")
def get_goals_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary statistics for all user's goals."""
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    
    if not goals:
        return {
            "total_goals": 0,
            "achieved_goals": 0,
            "total_target_amount": 0.0,
            "total_current_amount": 0.0,
            "overall_progress_percentage": 0.0,
            "goals_by_status": {"active": 0, "achieved": 0, "overdue": 0}
        }
    
    total_goals = len(goals)
    achieved_goals = len([g for g in goals if g.current_amount >= g.target_amount])
    
    total_target = sum(goal.target_amount for goal in goals)
    total_current = sum(goal.current_amount for goal in goals)
    
    # Count goals by status
    now = datetime.now()
    active_goals = 0
    achieved_goal_count = 0
    overdue_goals = 0
    
    for goal in goals:
        if goal.current_amount >= goal.target_amount:
            achieved_goal_count += 1
        elif goal.target_date < now:
            overdue_goals += 1
        else:
            active_goals += 1
    
    return {
        "total_goals": total_goals,
        "achieved_goals": achieved_goals,
        "total_target_amount": float(total_target),
        "total_current_amount": float(total_current),
        "overall_progress_percentage": float((total_current / total_target) * 100) if total_target > 0 else 0.0,
        "monthly_commitment": float(sum(goal.monthly_contribution for goal in goals)),
        "goals_by_status": {
            "active": active_goals,
            "achieved": achieved_goal_count,
            "overdue": overdue_goals
        }
    }

@router.get("/{goal_id}")
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific goal with progress calculations."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return calculate_goal_progress(goal, db)

@router.put("/{goal_id}")
def update_goal(
    goal_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    target_amount: Optional[float] = None,
    monthly_contribution: Optional[float] = None,
    target_date: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a goal."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Validate updates
    if target_amount is not None and target_amount <= 0:
        raise HTTPException(status_code=400, detail="Target amount must be positive")
    
    if target_date:
        try:
            target_date_obj = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
            if target_date_obj <= datetime.now():
                raise HTTPException(status_code=400, detail="Target date must be in the future")
            goal.target_date = target_date_obj
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid target date format")
    
    # Update fields
    if name:
        goal.name = name
    if description:
        goal.description = description
    if target_amount:
        goal.target_amount = target_amount
    if monthly_contribution is not None:
        goal.monthly_contribution = monthly_contribution
    if category:
        try:
            goal.category = GoalCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category")
    if priority:
        try:
            goal.priority = GoalPriority(priority)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid priority")
    
    db.commit()
    
    return {"message": "Goal updated successfully"}

@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a goal."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    db.delete(goal)
    db.commit()
    
    return {"message": "Goal deleted successfully"}

@router.post("/{goal_id}/contribute")
def contribute_to_goal(
    goal_id: int,
    amount: float,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a contribution to a goal."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Validate contribution amount
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Contribution amount must be positive")
    
    # Update goal current amount
    goal.current_amount += amount
    db.commit()
    
    # Calculate new progress
    progress_percentage = float((goal.current_amount / goal.target_amount) * 100)
    amount_remaining = goal.target_amount - goal.current_amount
    is_achieved = goal.current_amount >= goal.target_amount
    
    return {
        "message": f"Added ${amount} to goal '{goal.name}'",
        "new_balance": float(goal.current_amount),
        "remaining": float(amount_remaining),
        "is_achieved": is_achieved,
        "progress_percentage": progress_percentage
    }

@router.put("/{goal_id}/progress")
def update_goal_progress(
    goal_id: int,
    current_amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update goal progress manually."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Validate amount
    if current_amount < 0:
        raise HTTPException(status_code=400, detail="Current amount cannot be negative")
    
    old_amount = goal.current_amount
    goal.current_amount = current_amount
    db.commit()
    
    # Calculate new progress
    progress_percentage = float((goal.current_amount / goal.target_amount) * 100)
    
    return {
        "message": "Goal progress updated successfully",
        "old_amount": float(old_amount),
        "new_amount": float(goal.current_amount),
        "progress_percentage": progress_percentage
    }

# Enhanced Analytics Endpoints

@router.get("/analytics/category-breakdown")
def get_goals_by_category(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goals breakdown by category with analytics."""
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == GoalStatus.active
    ).all()
    
    category_data = {}
    
    for goal in goals:
        category = goal.category.value if goal.category else "uncategorized"
        
        if category not in category_data:
            category_data[category] = {
                "category": category,
                "goals_count": 0,
                "total_target": 0,
                "total_current": 0,
                "monthly_commitment": 0,
                "goals": []
            }
        
        goal_progress = calculate_goal_progress(goal, db)
        
        category_data[category]["goals_count"] += 1
        category_data[category]["total_target"] += float(goal.target_amount)
        category_data[category]["total_current"] += float(goal.current_amount)
        category_data[category]["monthly_commitment"] += float(goal.monthly_contribution)
        category_data[category]["goals"].append(goal_progress)
    
    # Calculate percentages and progress for each category
    for category_info in category_data.values():
        total_target = category_info["total_target"]
        total_current = category_info["total_current"]
        category_info["progress_percentage"] = (total_current / total_target * 100) if total_target > 0 else 0
    
    return {"categories": list(category_data.values())}

@router.get("/analytics/monthly-projections")
def get_monthly_projections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly projections for goal completion."""
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == GoalStatus.active
    ).all()
    
    projections = []
    
    for goal in goals:
        progress = calculate_goal_progress(goal, db)
        
        # Calculate months to completion based on current contribution rate
        if progress["avg_monthly_contribution"] > 0:
            months_to_completion = progress["amount_remaining"] / progress["avg_monthly_contribution"]
        else:
            months_to_completion = float('inf')
        
        # Calculate if on track to meet target date
        months_until_target = progress["months_remaining"]
        is_on_track = months_to_completion <= months_until_target
        
        projections.append({
            "goal_id": goal.id,
            "goal_name": goal.name,
            "category": progress["category"],
            "target_date": progress["target_date"],
            "months_to_completion": round(months_to_completion, 1) if months_to_completion != float('inf') else None,
            "months_until_target": months_until_target,
            "is_on_track": is_on_track,
            "projected_completion": datetime.now() + timedelta(days=months_to_completion * 30) if months_to_completion != float('inf') else None,
            "recommended_monthly": progress["monthly_target"]
        })
    
    return {"projections": projections}

@router.get("/analytics/contribution-history")
def get_contribution_history(
    months: int = Query(12, description="Number of months to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contribution history analytics."""
    # Get user's goals
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    goal_ids = [goal.id for goal in goals]
    
    if not goal_ids:
        return {"monthly_contributions": [], "total_contributed": 0}
    
    # Get contributions for the specified period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    
    contributions = db.query(GoalContribution).join(Goal).filter(
        GoalContribution.goal_id.in_(goal_ids),
        GoalContribution.date >= start_date,
        Goal.user_id == current_user.id
    ).order_by(GoalContribution.date).all()
    
    # Group by month
    monthly_data = {}
    total_contributed = 0
    
    for contrib in contributions:
        month_key = contrib.date.strftime("%Y-%m")
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "month": month_key,
                "total_amount": 0,
                "contribution_count": 0,
                "goals_contributed": set()
            }
        
        monthly_data[month_key]["total_amount"] += float(contrib.amount)
        monthly_data[month_key]["contribution_count"] += 1
        monthly_data[month_key]["goals_contributed"].add(contrib.goal.name)
        total_contributed += float(contrib.amount)
    
    # Convert to list and format
    monthly_contributions = []
    for month_data in monthly_data.values():
        month_data["goals_contributed"] = list(month_data["goals_contributed"])
        monthly_contributions.append(month_data)
    
    # Sort by month
    monthly_contributions.sort(key=lambda x: x["month"])
    
    return {
        "monthly_contributions": monthly_contributions,
        "total_contributed": total_contributed,
        "average_monthly": total_contributed / min(months, len(monthly_contributions)) if monthly_contributions else 0
    }

@router.get("/recommendations")
def get_goal_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized goal recommendations and optimization tips."""
    goals = db.query(Goal).filter(
        Goal.user_id == current_user.id,
        Goal.status == GoalStatus.active
    ).all()
    
    recommendations = []
    
    # Analyze each goal for recommendations
    for goal in goals:
        progress = calculate_goal_progress(goal, db)
        
        # Check if goal needs attention
        if not progress["is_on_track"] and progress["days_remaining"] > 0:
            difference = progress["monthly_target"] - progress["avg_monthly_contribution"]
            recommendations.append({
                "type": "optimization",
                "goal_id": goal.id,
                "goal_name": goal.name,
                "title": f"Increase {goal.name} Contribution",
                "description": f"Consider increasing monthly contribution by ${difference:.0f} to reach your goal on time",
                "action": f"Increase by ${difference:.0f}",
                "priority": "high" if progress["days_remaining"] < 90 else "medium"
            })
        
        # Check for overdue goals
        if progress["days_remaining"] < 0:
            recommendations.append({
                "type": "urgent",
                "goal_id": goal.id,
                "goal_name": goal.name,
                "title": f"Goal Overdue: {goal.name}",
                "description": f"This goal was due {abs(progress['days_remaining'])} days ago. Consider adjusting the target date or increasing contributions.",
                "action": "Review goal settings",
                "priority": "urgent"
            })
        
        # Check for low-priority goals that might be deprioritized
        if goal.priority == GoalPriority.low and progress["avg_monthly_contribution"] > progress["monthly_target"]:
            recommendations.append({
                "type": "suggestion",
                "goal_id": goal.id,
                "goal_name": goal.name,
                "title": f"Consider Reallocating from {goal.name}",
                "description": f"You're ahead of schedule on this low-priority goal. Consider redirecting some funds to higher-priority goals.",
                "action": "Reallocate funds",
                "priority": "low"
            })
    
    # General recommendations based on overall portfolio
    total_monthly_commitment = sum(float(goal.monthly_contribution) for goal in goals)
    
    # Get user's average monthly income
    monthly_income = db.query(
        func.avg(Income.amount)
    ).filter(
        Income.user_id == current_user.id,
        Income.date >= datetime.now() - timedelta(days=180)
    ).scalar() or 0
    
    if monthly_income > 0 and total_monthly_commitment / monthly_income < 0.20:
        recommendations.append({
            "type": "growth",
            "title": "Consider Increasing Savings Rate",
            "description": f"You're saving {(total_monthly_commitment/monthly_income*100):.1f}% of your income. Consider increasing to 20% or more for better financial health.",
            "action": "Increase monthly contributions",
            "priority": "medium"
        })
    
    # Sort by priority
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
    
    return {"recommendations": recommendations}

@router.post("/{goal_id}/contributions")
def add_goal_contribution(
    goal_id: int,
    amount: float,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a contribution to a goal with proper tracking."""
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Contribution amount must be positive")
    
    # Create contribution record
    contribution = GoalContribution(
        goal_id=goal.id,
        user_id=current_user.id,
        amount=amount,
        notes=notes
    )
    
    # Update goal current amount
    goal.current_amount += amount
    
    # Check if goal is now completed
    if goal.current_amount >= goal.target_amount and goal.status == GoalStatus.active:
        goal.status = GoalStatus.completed
    
    db.add(contribution)
    db.commit()
    
    # Return updated progress
    progress = calculate_goal_progress(goal, db)
    
    return {
        "message": f"Added ${amount} contribution to {goal.name}",
        "contribution_id": contribution.id,
        "goal_progress": progress
    }