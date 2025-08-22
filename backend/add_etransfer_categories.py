#!/usr/bin/env python3
"""
Add new e-transfer categories
"""

from app.database import get_db
from app.models import Category

def add_etransfer_categories():
    db = next(get_db())
    
    # Check if categories already exist
    existing_categories = db.query(Category).filter(
        Category.name.in_(['Interac E-Transfer', 'Interac E-Transfer Self'])
    ).all()
    
    if existing_categories:
        print("E-Transfer categories already exist:")
        for cat in existing_categories:
            print(f"  - {cat.name} (ID: {cat.id})")
        return
    
    # Add new categories
    new_categories = [
        {
            'name': 'Interac E-Transfer',
            'description': 'Money transfers to/from others via Interac e-Transfer',
            'default_budget': 0.0  # No budget limit for transfers
        },
        {
            'name': 'Interac E-Transfer Self',
            'description': 'Money transfers between your own accounts',
            'default_budget': 0.0  # No budget limit for self-transfers
        }
    ]
    
    added_categories = []
    for cat_data in new_categories:
        category = Category(
            name=cat_data['name'],
            description=cat_data['description'],
            default_budget=cat_data['default_budget']
        )
        db.add(category)
        added_categories.append(category)
    
    try:
        db.commit()
        print("✅ Successfully added new e-transfer categories:")
        for category in added_categories:
            db.refresh(category)  # Get the assigned ID
            print(f"  - {category.name} (ID: {category.id})")
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding categories: {e}")

if __name__ == "__main__":
    add_etransfer_categories()