"""
Database configuration module.
Configures SQLAlchemy engine, session factory, and base class.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment variable, default to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agency_tracker.db")

# Configure engine based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite with multiple threads
        echo=False  # Set to True for SQL debugging
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency function that creates a new database session for each request.
    Ensures proper cleanup after use.

    Usage:
        db = get_db()
        try:
            # use db
        finally:
            db.close()

    Or with context manager pattern in services.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
