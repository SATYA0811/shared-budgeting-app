"""
Category Routes - Step 3: Categorization System

This module handles:
- Category management (CRUD operations)
- Budget assignment and management for categories
- Default category seeding for new users
- Category-based transaction filtering

Features:
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
    categories = [
        {"name": "Income", "description": "Salary, freelance, and other income sources", "default_budget": 0.00},
        {"name": "Food & Drinks", "description": "Eating out, booze, snacks etc.", "default_budget": 600.00},
        {"name": "Transport", "description": "Uber, Ola and other modes of transport", "default_budget": 300.00},
        {"name": "Shopping", "description": "Clothes, shoes, furniture etc.", "default_budget": 400.00},
        {"name": "Groceries", "description": "Kitchen and other household supplies", "default_budget": 500.00},
        {"name": "Entertainment", "description": "Movies, Concerts and other recreations", "default_budget": 200.00},
        {"name": "Events", "description": "Being social while putting a dent in your bank account", "default_budget": 150.00},
        {"name": "Travel", "description": "Exploration, fun and vacations!", "default_budget": 500.00},
        {"name": "Medical", "description": "Medicines, Doctor consultation etc.", "default_budget": 200.00},
        {"name": "Personal", "description": "Money spent on & for yourself", "default_budget": 150.00},
        {"name": "Fitness", "description": "Things to keep your biological machinery in tune", "default_budget": 100.00},
        {"name": "Services", "description": "Professional tasks provided for a fee", "default_budget": 300.00},
        {"name": "Bills", "description": "Rent, Wi-fi, electricity and other bills", "default_budget": 800.00},
        {"name": "Subscriptions", "description": "Recurring payment to online services", "default_budget": 100.00},
        {"name": "EMI", "description": "Repayment of Loan", "default_budget": 500.00},
        {"name": "Credit Bill", "description": "Credit Card & BNPL services settlement", "default_budget": 300.00},
        {"name": "Investment", "description": "Money put towards investment", "default_budget": 1000.00},
        {"name": "Support", "description": "Financial support for loved ones", "default_budget": 200.00},
        {"name": "Insurance", "description": "Payment towards insurance premiums", "default_budget": 150.00},
        {"name": "Tax", "description": "Income tax, property tax, etc.", "default_budget": 300.00},
        {"name": "Top-up", "description": "Money added to online wallets", "default_budget": 50.00},
        {"name": "Children", "description": "It takes a village to raise a child, & a ton of cash", "default_budget": 400.00},
        {"name": "Miscellaneous", "description": "Everything else", "default_budget": 100.00},
        {"name": "Self Transfer", "description": "Transfer between personal Bank accounts", "default_budget": 0.00},
        {"name": "Savings", "description": "For goals and dreams", "default_budget": 800.00},
        {"name": "Gifts", "description": "Money gifted or spent buying gifts :)", "default_budget": 100.00},
    ]
    
    return categories

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
        "description": cat.description,
        "default_budget": float(cat.default_budget) if cat.default_budget else None
    } for cat in categories]

@router.post("", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category."""
    # Check if category name already exists
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category name already exists")
    
    db_category = Category(
        name=category.name,
        description=category.description,
        default_budget=category.default_budget
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return {
        "id": db_category.id,
        "name": db_category.name,
        "description": db_category.description,
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
        "description": category.description,
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
        "description": category.description,
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
    
    db.delete(category)
    db.commit()
    
    return {"message": "Category deleted successfully"}