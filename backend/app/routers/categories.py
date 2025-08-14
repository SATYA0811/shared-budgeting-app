"""
Category Routes - Step 3: Categorization System

This module handles:
- Category management (CRUD operations)
- Hierarchical category structure with parent-child relationships
- Budget assignment and management for categories
- Default category seeding for new users
- Category-based transaction filtering

Features:
- Hierarchical category organization (parent-child)
- Budget tracking per category
- Default categories for common expenses
- Category deletion with transaction handling
- Input validation and error handling
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..auth import get_current_user
from ..schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from ..models import User, Category, Transaction

# Create router
router = APIRouter(prefix="/categories", tags=["Categories"])

def get_default_categories():
    """Return default categories for new users."""
    return [
        {"name": "Food & Dining", "default_budget": 500.00},
        {"name": "Groceries", "default_budget": 300.00},
        {"name": "Transportation", "default_budget": 200.00},
        {"name": "Shopping", "default_budget": 150.00},
        {"name": "Entertainment", "default_budget": 100.00},
        {"name": "Bills & Utilities", "default_budget": 400.00},
        {"name": "Healthcare", "default_budget": 200.00},
        {"name": "Education", "default_budget": 100.00},
        {"name": "Travel", "default_budget": 300.00},
        {"name": "Personal Care", "default_budget": 75.00},
    ]

@router.get("", response_model=List[CategoryResponse])
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all categories. Creates default categories if none exist."""
    categories = db.query(Category).all()
    
    # If no categories exist, create default ones
    if not categories:
        default_categories = get_default_categories()
        for cat_data in default_categories:
            category = Category(**cat_data)
            db.add(category)
        
        db.commit()
        categories = db.query(Category).all()
    
    return [{
        "id": cat.id,
        "name": cat.name,
        "parent_id": cat.parent_id,
        "default_budget": float(cat.default_budget) if cat.default_budget else None
    } for cat in categories]

@router.post("", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category."""
    # Validate parent category exists if provided
    if category.parent_id:
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
    
    # Check if category name already exists
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    db_category = Category(
        name=category.name,
        parent_id=category.parent_id,
        default_budget=category.default_budget
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return {
        "id": db_category.id,
        "name": db_category.name,
        "parent_id": db_category.parent_id,
        "default_budget": float(db_category.default_budget) if db_category.default_budget else None
    }

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return {
        "id": category.id,
        "name": category.name,
        "parent_id": category.parent_id,
        "default_budget": float(category.default_budget) if category.default_budget else None
    }

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Validate parent category if being updated
    if category_update.parent_id:
        # Prevent self-referencing
        if category_update.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")
        
        parent = db.query(Category).filter(Category.id == category_update.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
    
    # Check name uniqueness if being updated
    if category_update.name and category_update.name != category.name:
        existing = db.query(Category).filter(
            Category.name == category_update.name,
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
    
    # Update fields
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return {
        "id": category.id,
        "name": category.name,
        "parent_id": category.parent_id,
        "default_budget": float(category.default_budget) if category.default_budget else None
    }

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a category."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has transactions
    transaction_count = db.query(Transaction).filter(
        Transaction.category_id == category_id
    ).count()
    
    if transaction_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete category. It has {transaction_count} associated transactions. "
                   "Please reassign these transactions to another category first."
        )
    
    # Check if category has child categories
    child_count = db.query(Category).filter(Category.parent_id == category_id).count()
    if child_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category. It has child categories. "
                   "Please delete child categories first or reassign them."
        )
    
    db.delete(category)
    db.commit()
    
    return {"message": "Category deleted successfully"}