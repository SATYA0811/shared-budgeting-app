"""
Goals Routes - Step 5: Goals & Investment Tracking

This module handles:
- Goal creation, tracking, and management (CRUD operations)
- Goal progress calculations and visualization
- Goal contribution logging and tracking
- Achievement detection and notifications
- Goals summary dashboard and reporting

Features:
- Target amount and date tracking
- Progress percentage calculations
- Contribution history
- Achievement status monitoring
- Recurring goal support (monthly, yearly)
- User-based goal isolation
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from decimal import Decimal

from ..database import get_db
from ..auth import get_current_user
from ..schemas import (
    GoalCreate, GoalUpdate, GoalResponse, 
    GoalContribution, GoalProgressUpdate
)
from ..models import User, Goal

# Create router
router = APIRouter(prefix="/goals", tags=["Goals"])

def calculate_goal_progress(goal: Goal):
    """Calculate progress statistics for a goal."""
    now = datetime.now()
    
    # Calculate progress percentage
    progress_percentage = float((goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0.0
    
    # Calculate amount remaining
    amount_remaining = goal.target_amount - goal.current_amount
    
    # Calculate days remaining
    days_remaining = (goal.target_date - now).days if goal.target_date > now else 0
    
    # Check if achieved
    is_achieved = goal.current_amount >= goal.target_amount
    
    return {
        "id": goal.id,
        "name": goal.name,
        "target_amount": float(goal.target_amount),
        "current_amount": float(goal.current_amount),
        "target_date": goal.target_date.isoformat(),
        "recurrence": goal.recurrence,
        "user_id": goal.user_id,
        "progress_percentage": progress_percentage,
        "amount_remaining": float(amount_remaining),
        "days_remaining": days_remaining,
        "is_achieved": is_achieved
    }

@router.post("", response_model=GoalResponse)
def create_goal(
    goal: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new financial goal."""
    # Validate target amount is positive
    if goal.target_amount <= 0:
        raise HTTPException(status_code=400, detail="Target amount must be positive")
    
    # Validate target date is in the future
    if goal.target_date <= datetime.now():
        raise HTTPException(status_code=400, detail="Target date must be in the future")
    
    # Validate current amount is not negative
    if goal.current_amount and goal.current_amount < 0:
        raise HTTPException(status_code=400, detail="Current amount cannot be negative")
    
    db_goal = Goal(
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount or Decimal(0),
        target_date=goal.target_date,
        recurrence=goal.recurrence,
        user_id=current_user.id
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return calculate_goal_progress(db_goal)

@router.get("", response_model=List[GoalResponse])
def get_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user's goals with progress calculations."""
    goals = db.query(Goal).filter(Goal.user_id == current_user.id).all()
    
    return [calculate_goal_progress(goal) for goal in goals]

@router.get("/{goal_id}", response_model=GoalResponse)
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
    
    return calculate_goal_progress(goal)

@router.put("/{goal_id}", response_model=dict)
def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
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
    if goal_update.target_amount is not None and goal_update.target_amount <= 0:
        raise HTTPException(status_code=400, detail="Target amount must be positive")
    
    if goal_update.current_amount is not None and goal_update.current_amount < 0:
        raise HTTPException(status_code=400, detail="Current amount cannot be negative")
    
    if goal_update.target_date is not None and goal_update.target_date <= datetime.now():
        raise HTTPException(status_code=400, detail="Target date must be in the future")
    
    # Update fields
    update_data = goal_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(goal, field, value)
    
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
    contribution: GoalContribution,
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
    if contribution.amount <= 0:
        raise HTTPException(status_code=400, detail="Contribution amount must be positive")
    
    # Update goal current amount
    goal.current_amount += contribution.amount
    db.commit()
    
    # Calculate new progress
    progress_percentage = float((goal.current_amount / goal.target_amount) * 100)
    amount_remaining = goal.target_amount - goal.current_amount
    is_achieved = goal.current_amount >= goal.target_amount
    
    return {
        "message": f"Added ${contribution.amount} to goal '{goal.name}'",
        "new_balance": float(goal.current_amount),
        "remaining": float(amount_remaining),
        "is_achieved": is_achieved,
        "progress_percentage": progress_percentage
    }

@router.put("/{goal_id}/progress")
def update_goal_progress(
    goal_id: int,
    progress_update: GoalProgressUpdate,
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
    if progress_update.current_amount < 0:
        raise HTTPException(status_code=400, detail="Current amount cannot be negative")
    
    old_amount = goal.current_amount
    goal.current_amount = progress_update.current_amount
    db.commit()
    
    # Calculate new progress
    progress_percentage = float((goal.current_amount / goal.target_amount) * 100)
    
    return {
        "message": "Goal progress updated successfully",
        "old_amount": float(old_amount),
        "new_amount": float(goal.current_amount),
        "progress_percentage": progress_percentage
    }

@router.get("-summary", response_model=dict)
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
        "goals_by_status": {
            "active": active_goals,
            "achieved": achieved_goal_count,
            "overdue": overdue_goals
        }
    }