import os
import sys
from alembic import command
from alembic.config import Config

def run_catatan_migration():
    alembic_cfg = Config("migrations/alembic.ini")
    try:
        print("Running migration to add catatan column...")
        command.upgrade(alembic_cfg, "add_catatan_column")
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error running migration: {e}")
        return False
    return True

if __name__ == "__main__":
    os.environ['FLASK_APP'] = 'run.py'
    success = run_catatan_migration()
    if success:
        print("Database updated successfully with catatan column!")
    else:
        print("Failed to update database.")
        sys.exit(1) 