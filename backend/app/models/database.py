from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    if DATABASE_URL.startswith("postgres") or "postgres" in DATABASE_URL:
        try:
            import psycopg2
        except ImportError as e:
            raise ImportError(
                "psycopg2 (psycopg2-binary) is required for PostgreSQL. "
                "Install it with `pip install psycopg2-binary`"
            ) from e

    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
