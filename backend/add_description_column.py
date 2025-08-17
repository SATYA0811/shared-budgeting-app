#!/usr/bin/env python3
"""
Database migration script to add description column to categories table.
This will add the missing description column that's causing 500 errors.
"""

import sqlite3
import os

def add_description_column():
    """Add description column to categories table."""
    db_path = "budgeting.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if description column already exists
        cursor.execute("PRAGMA table_info(categories)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'description' in columns:
            print("Description column already exists in categories table")
            return True
        
        # Add the description column
        print("Adding description column to categories table...")
        cursor.execute("ALTER TABLE categories ADD COLUMN description TEXT")
        
        # Commit the changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(categories)")
        columns_after = [column[1] for column in cursor.fetchall()]
        
        if 'description' in columns_after:
            print("✅ Successfully added description column to categories table!")
            print(f"Categories table now has columns: {', '.join(columns_after)}")
            return True
        else:
            print("❌ Failed to add description column")
            return False
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Adding description column to categories table...")
    success = add_description_column()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("The categories API should now work properly.")
    else:
        print("\n❌ Migration failed!")