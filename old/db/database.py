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
    # Ensure required DB driver is present and fail with a clear message if not
    try:
        # For PostgreSQL SQLAlchemy will import the DBAPI (psycopg2)
        if DATABASE_URL.startswith("postgres") or "postgres" in DATABASE_URL:
            try:
                import psycopg2  # noqa: F401
            except ImportError as e:
                raise ImportError(
                    "psycopg2 (psycopg2-binary) is required for PostgreSQL. "
                    "Install it with `pip install psycopg2-binary` or add it to requirements.txt"
                ) from e

        engine = create_engine(
            DATABASE_URL,
            echo=False
        )
    except Exception:
        # Re-raise to surface the original error to the caller/logs
        raise

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
