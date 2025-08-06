#!/usr/bin/env python3
"""
Script untuk menjalankan migration secara manual
"""
import os
import sys
from alembic import command
from alembic.config import Config

def run_migration():
    # Set up Alembic configuration
    alembic_cfg = Config("migrations/alembic.ini")
    
    try:
        # Run the migration
        print("Running migration to add guru_id column...")
        command.upgrade(alembic_cfg, "add_guru_id_penilaian")
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error running migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Set environment variable
    os.environ['FLASK_APP'] = 'run.py'
    
    # Run migration
    success = run_migration()
    
    if success:
        print("Database updated successfully!")
    else:
        print("Failed to update database.")
        sys.exit(1) 