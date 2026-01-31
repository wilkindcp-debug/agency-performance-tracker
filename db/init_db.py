"""
Database initialization script.
Creates all tables defined in models.py.

Usage:
    python -m db.init_db
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine, Base
from db.models import (
    Agency, AgencyManager, KPI, AgencyKPI,
    MonthlyTarget, MonthlyResult, MonthlyReview, ActionItem
)


def init_database():
    """
    Initialize the database by creating all tables.
    """
    print("Initializing database...")
    print(f"Database URL: {engine.url}")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")
    print("\nTables created:")
    for table in Base.metadata.tables.keys():
        print(f"  - {table}")


if __name__ == "__main__":
    init_database()
