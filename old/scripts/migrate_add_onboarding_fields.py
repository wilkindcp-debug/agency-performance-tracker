"""
Migration script to add onboarding fields to users table.
Run this script once after updating the code to add the new columns.

Usage:
    python scripts/migrate_add_onboarding_fields.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlalchemy import text


def run_migration():
    """Add onboarding_completed and last_login_at columns to users table."""
    print("🚀 Starting migration: Add onboarding fields to users table")

    with engine.connect() as conn:
        # Check current columns
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
        """))
        existing_cols = [row[0] for row in result]

        # Add onboarding_completed if not exists
        if 'onboarding_completed' not in existing_cols:
            print("  → Adding 'onboarding_completed' column...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE
            """))
            print("    ✅ Column 'onboarding_completed' added")
        else:
            print("  → Column 'onboarding_completed' already exists")

        # Add last_login_at if not exists
        if 'last_login_at' not in existing_cols:
            print("  → Adding 'last_login_at' column...")
            conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN last_login_at TIMESTAMP NULL
            """))
            print("    ✅ Column 'last_login_at' added")
        else:
            print("  → Column 'last_login_at' already exists")

        conn.commit()

    print("\n🎉 Migration completed successfully!")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        sys.exit(1)
