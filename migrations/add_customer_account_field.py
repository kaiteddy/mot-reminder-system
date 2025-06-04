#!/usr/bin/env python3
"""
Migration script to add account field to customers table
This field will store external customer account IDs for linking with job sheets
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from app import create_app

def run_migration():
    """Add account field to customers table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if the column already exists
            result = db.engine.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='customers' AND column_name='account'
            """)
            
            if result.fetchone():
                print("✓ Account column already exists in customers table")
                return True
            
            # Add the account column
            db.engine.execute("""
                ALTER TABLE customers 
                ADD COLUMN account VARCHAR(100)
            """)
            
            print("✓ Successfully added account column to customers table")
            return True
            
        except Exception as e:
            print(f"✗ Error adding account column: {e}")
            return False

if __name__ == "__main__":
    print("Adding account field to customers table...")
    success = run_migration()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
