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
    """Return default categories for new users with hierarchical structure."""
    categories = []
    
    # Create parent categories first, then children
    parent_categories = [
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
        {"name": "Bill", "description": "Rent, Wi-fi, electricity and other bills", "default_budget": 800.00},
        {"name": "Subscription", "description": "Recurring payment to online services", "default_budget": 100.00},
        {"name": "EMI", "description": "Repayment of Loan", "default_budget": 500.00},
        {"name": "Credit Bill", "description": "Credit Card & BNPL services settlement", "default_budget": 300.00},
        {"name": "Investment", "description": "Money put towards investment", "default_budget": 1000.00},
        {"name": "Support", "description": "Financial support for loved ones", "default_budget": 200.00},
        {"name": "Insurance", "description": "Payment towards insurance premiums", "default_budget": 150.00},
        {"name": "Tax", "description": "Income tax, property tax, e.t.c", "default_budget": 300.00},
        {"name": "Top-up", "description": "Money added to online wallets", "default_budget": 50.00},
        {"name": "Children", "description": "It takes a village to raise a child, & a ton of cash", "default_budget": 400.00},
        {"name": "Misc.", "description": "Everything else", "default_budget": 100.00},
        {"name": "Self Transfer", "description": "Transfer between personal Bank accounts", "default_budget": 0.00},
        {"name": "Savings", "description": "For goals and dreams", "default_budget": 800.00},
        {"name": "Gift", "description": "Money gifted or spent buying gifts :)", "default_budget": 100.00},
    ]
    
    # Child categories for each parent
    child_categories = {
        "Food & Drinks": [
            {"name": "Eating out", "default_budget": 200.00},
            {"name": "Take Away", "default_budget": 150.00},
            {"name": "Tea & Coffee", "default_budget": 50.00},
            {"name": "Fast Food", "default_budget": 100.00},
            {"name": "Sweets", "default_budget": 50.00},
            {"name": "Swiggy", "default_budget": 150.00},
            {"name": "Zomato", "default_budget": 150.00},
            {"name": "Liquor", "default_budget": 100.00},
            {"name": "Beverages", "default_budget": 50.00},
            {"name": "Data", "default_budget": 30.00},
            {"name": "Pizza", "default_budget": 80.00},
            {"name": "Tiffin", "default_budget": 120.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Transport": [
            {"name": "Uber", "default_budget": 100.00},
            {"name": "Rapido", "default_budget": 60.00},
            {"name": "Auto", "default_budget": 80.00},
            {"name": "Cab", "default_budget": 100.00},
            {"name": "Train", "default_budget": 50.00},
            {"name": "Metro", "default_budget": 60.00},
            {"name": "Bus", "default_budget": 40.00},
            {"name": "Bike", "default_budget": 30.00},
            {"name": "Fuel", "default_budget": 200.00},
            {"name": "EV Charge", "default_budget": 50.00},
            {"name": "Flights", "default_budget": 300.00},
            {"name": "Parking", "default_budget": 30.00},
            {"name": "FASTtag", "default_budget": 50.00},
            {"name": "Tolls", "default_budget": 40.00},
            {"name": "Lounge", "default_budget": 50.00},
            {"name": "Fine", "default_budget": 0.00},
            {"name": "Others", "default_budget": 30.00},
        ],
        "Shopping": [
            {"name": "Clothes", "default_budget": 150.00},
            {"name": "Footwear", "default_budget": 100.00},
            {"name": "Electronics", "default_budget": 200.00},
            {"name": "Festival", "default_budget": 100.00},
            {"name": "Video games", "default_budget": 60.00},
            {"name": "Books", "default_budget": 50.00},
            {"name": "Plants", "default_budget": 30.00},
            {"name": "Jewellery", "default_budget": 100.00},
            {"name": "Furniture", "default_budget": 200.00},
            {"name": "Appliances", "default_budget": 150.00},
            {"name": "Vehicle", "default_budget": 500.00},
            {"name": "Cosmetics", "default_budget": 80.00},
            {"name": "Toys", "default_budget": 50.00},
            {"name": "Stationery", "default_budget": 30.00},
            {"name": "Glasses", "default_budget": 100.00},
            {"name": "Devotional", "default_budget": 50.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Groceries": [
            {"name": "Staples", "default_budget": 150.00},
            {"name": "Vegetables", "default_budget": 100.00},
            {"name": "Fruits", "default_budget": 80.00},
            {"name": "Meat", "default_budget": 120.00},
            {"name": "Eggs", "default_budget": 40.00},
            {"name": "Bakery", "default_budget": 60.00},
            {"name": "Dairy", "default_budget": 80.00},
            {"name": "Zepto", "default_budget": 100.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Entertainment": [
            {"name": "Movies", "default_budget": 100.00},
            {"name": "Shows", "default_budget": 80.00},
            {"name": "Bowling", "default_budget": 60.00},
            {"name": "Others", "default_budget": 40.00},
        ],
        "Events": [
            {"name": "Party", "default_budget": 100.00},
            {"name": "Spiritual", "default_budget": 50.00},
            {"name": "Wedding", "default_budget": 200.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Travel": [
            {"name": "Activities", "default_budget": 150.00},
            {"name": "Camping", "default_budget": 100.00},
            {"name": "Hotel", "default_budget": 200.00},
            {"name": "Visa fees", "default_budget": 100.00},
            {"name": "Hostel", "default_budget": 80.00},
            {"name": "Airbnb", "default_budget": 150.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Medical": [
            {"name": "Medicines", "default_budget": 80.00},
            {"name": "Hospital", "default_budget": 200.00},
            {"name": "Clinic", "default_budget": 100.00},
            {"name": "Dentist", "default_budget": 150.00},
            {"name": "Lab test", "default_budget": 100.00},
            {"name": "Hygiene", "default_budget": 50.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Personal": [
            {"name": "Self-care", "default_budget": 80.00},
            {"name": "Grooming", "default_budget": 60.00},
            {"name": "Hobbies", "default_budget": 100.00},
            {"name": "Vices", "default_budget": 50.00},
            {"name": "Therapy", "default_budget": 200.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Fitness": [
            {"name": "Gym", "default_budget": 80.00},
            {"name": "Badminton", "default_budget": 50.00},
            {"name": "Football", "default_budget": 40.00},
            {"name": "Cricket", "default_budget": 40.00},
            {"name": "Classes", "default_budget": 60.00},
            {"name": "Equipment", "default_budget": 100.00},
            {"name": "Nutrition", "default_budget": 80.00},
            {"name": "Others", "default_budget": 30.00},
        ],
        "Services": [
            {"name": "Laundry", "default_budget": 50.00},
            {"name": "Tailor", "default_budget": 40.00},
            {"name": "Courier", "default_budget": 30.00},
            {"name": "Carpenter", "default_budget": 100.00},
            {"name": "Plumber", "default_budget": 80.00},
            {"name": "Mechanic", "default_budget": 150.00},
            {"name": "Photographer", "default_budget": 200.00},
            {"name": "Driver", "default_budget": 100.00},
            {"name": "Vehicle Wash", "default_budget": 40.00},
            {"name": "Electrician", "default_budget": 80.00},
            {"name": "Painting", "default_budget": 100.00},
            {"name": "Xerox", "default_budget": 20.00},
            {"name": "Legal", "default_budget": 200.00},
            {"name": "Advisor", "default_budget": 150.00},
            {"name": "Repair", "default_budget": 80.00},
            {"name": "Logistics", "default_budget": 60.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Bill": [
            {"name": "Phone", "default_budget": 80.00},
            {"name": "Rent", "default_budget": 1500.00},
            {"name": "Water", "default_budget": 60.00},
            {"name": "Electricity", "default_budget": 150.00},
            {"name": "Gas", "default_budget": 100.00},
            {"name": "Internet", "default_budget": 80.00},
            {"name": "House help", "default_budget": 100.00},
            {"name": "Education", "default_budget": 200.00},
            {"name": "DTH", "default_budget": 50.00},
            {"name": "Cook", "default_budget": 150.00},
            {"name": "Maintenance", "default_budget": 100.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Subscription": [
            {"name": "Software", "default_budget": 50.00},
            {"name": "News", "default_budget": 30.00},
            {"name": "Netflix", "default_budget": 15.00},
            {"name": "Prime", "default_budget": 15.00},
            {"name": "YouTube", "default_budget": 15.00},
            {"name": "Spotify", "default_budget": 15.00},
            {"name": "Google", "default_budget": 20.00},
            {"name": "Learning", "default_budget": 50.00},
            {"name": "Apple", "default_budget": 20.00},
            {"name": "Bumble", "default_budget": 30.00},
            {"name": "JioCinema", "default_budget": 15.00},
            {"name": "Google Play", "default_budget": 20.00},
            {"name": "Xbox", "default_budget": 30.00},
            {"name": "PlayStation", "default_budget": 30.00},
            {"name": "Disney Plus", "default_budget": 15.00},
            {"name": "ZEE5", "default_budget": 15.00},
            {"name": "ChatGPT", "default_budget": 20.00},
            {"name": "Others", "default_budget": 30.00},
        ],
        "EMI": [
            {"name": "Electronics", "default_budget": 200.00},
            {"name": "House", "default_budget": 2000.00},
            {"name": "Vehicle", "default_budget": 800.00},
            {"name": "Education", "default_budget": 500.00},
            {"name": "Others", "default_budget": 100.00},
        ],
        "Credit Bill": [
            {"name": "Credit card", "default_budget": 300.00},
            {"name": "Simpl", "default_budget": 100.00},
            {"name": "Slice", "default_budget": 100.00},
            {"name": "Lazypay", "default_budget": 80.00},
            {"name": "Amazon Pay", "default_budget": 100.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Investment": [
            {"name": "Mutual Funds", "default_budget": 500.00},
            {"name": "Stocks", "default_budget": 300.00},
            {"name": "IPO", "default_budget": 200.00},
            {"name": "PPF", "default_budget": 200.00},
            {"name": "NPS", "default_budget": 150.00},
            {"name": "Fixed Deposit", "default_budget": 500.00},
            {"name": "Recurring Deposit", "default_budget": 200.00},
            {"name": "Assets", "default_budget": 1000.00},
            {"name": "Crypto", "default_budget": 100.00},
            {"name": "Gold", "default_budget": 200.00},
            {"name": "Others", "default_budget": 100.00},
        ],
        "Support": [
            {"name": "Parents", "default_budget": 500.00},
            {"name": "Spouse", "default_budget": 300.00},
            {"name": "Mom", "default_budget": 200.00},
            {"name": "Dad", "default_budget": 200.00},
            {"name": "Pocket Money", "default_budget": 100.00},
            {"name": "Others", "default_budget": 100.00},
        ],
        "Insurance": [
            {"name": "Health", "default_budget": 100.00},
            {"name": "Vehicle", "default_budget": 80.00},
            {"name": "Life", "default_budget": 150.00},
            {"name": "Electronics", "default_budget": 30.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Tax": [
            {"name": "Income Tax", "default_budget": 300.00},
            {"name": "GST", "default_budget": 100.00},
            {"name": "Property Tax", "default_budget": 150.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Top-up": [
            {"name": "UPI Lite", "default_budget": 20.00},
            {"name": "Paytm", "default_budget": 30.00},
            {"name": "Amazon", "default_budget": 50.00},
            {"name": "PhonePe", "default_budget": 30.00},
            {"name": "Others", "default_budget": 20.00},
        ],
        "Children": [
            {"name": "Nutrition", "default_budget": 100.00},
            {"name": "Necessities", "default_budget": 150.00},
            {"name": "Toys", "default_budget": 80.00},
            {"name": "Medical", "default_budget": 100.00},
            {"name": "Care", "default_budget": 120.00},
            {"name": "Tuition Fee", "default_budget": 200.00},
            {"name": "Classes Fee", "default_budget": 100.00},
            {"name": "School Fee", "default_budget": 300.00},
            {"name": "College Fee", "default_budget": 500.00},
            {"name": "Others", "default_budget": 50.00},
        ],
        "Misc.": [
            {"name": "Tip", "default_budget": 30.00},
            {"name": "Verification", "default_budget": 20.00},
            {"name": "Forex", "default_budget": 100.00},
            {"name": "Deposit", "default_budget": 200.00},
            {"name": "Gift Card", "default_budget": 100.00},
            {"name": "Others", "default_budget": 50.00},
        ],
    }
    
    # Add all parent categories first
    for parent in parent_categories:
        categories.append(parent)
    
    return categories, child_categories

@router.get("", response_model=List[CategoryResponse])
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all categories. Creates default categories if none exist."""
    categories = db.query(Category).all()
    
    # If no categories exist, create default ones
    if not categories:
        parent_categories, child_categories = get_default_categories()
        
        # Create parent categories first
        parent_id_map = {}
        for cat_data in parent_categories:
            category = Category(**cat_data)
            db.add(category)
            db.flush()  # Get the ID before committing
            parent_id_map[cat_data["name"]] = category.id
        
        # Create child categories with parent_id references
        for parent_name, children in child_categories.items():
            parent_id = parent_id_map.get(parent_name)
            if parent_id:
                for child_data in children:
                    child_category = Category(
                        name=child_data["name"],
                        parent_id=parent_id,
                        default_budget=child_data["default_budget"]
                    )
                    db.add(child_category)
        
        db.commit()
        categories = db.query(Category).all()
    
    return [{
        "id": cat.id,
        "name": cat.name,
        "description": cat.description,
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
        description=category.description,
        parent_id=category.parent_id,
        default_budget=category.default_budget
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return {
        "id": db_category.id,
        "name": db_category.name,
        "description": db_category.description,
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
        "description": category.description,
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
        "description": category.description,
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