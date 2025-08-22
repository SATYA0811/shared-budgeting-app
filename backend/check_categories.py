#!/usr/bin/env python3
"""
Check current categories in database
"""

from app.database import get_db
from app.models import Category
from sqlalchemy.orm import Session

def check_categories():
    db = next(get_db())
    categories = db.query(Category).all()

    print('📊 Current Categories:')
    print('=' * 40)
    for cat in categories:
        print(f'{cat.id:2d}. {cat.name} (Budget: ${cat.default_budget or 0})')
    
    print(f'\nTotal categories: {len(categories)}')

if __name__ == "__main__":
    check_categories()