import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import engine
from sqlalchemy import text

def run_migration():
    print("Starting migration: Add onboarding fields to users table")

    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT onboarding_completed FROM users LIMIT 1"))
            print("Column 'onboarding_completed' already exists")
        except:
            print("Adding 'onboarding_completed' column...")
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0 NOT NULL
            """))
            conn.commit()
            print("Column 'onboarding_completed' added")

        try:
            conn.execute(text("SELECT last_login_at FROM users LIMIT 1"))
            print("Column 'last_login_at' already exists")
        except:
            print("Adding 'last_login_at' column...")
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN last_login_at DATETIME NULL
            """))
            conn.commit()
            print("Column 'last_login_at' added")

    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
