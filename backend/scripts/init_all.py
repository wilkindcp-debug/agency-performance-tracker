import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import engine, Base, SessionLocal
from app.services.auth_service import ensure_admin_exists
from app.services.kpi_service import seed_kpis
from app.services.country_service import seed_countries

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        print("Seeding KPIs...")
        seed_kpis(db)

        print("Seeding countries...")
        seed_countries(db)

        print("Ensuring admin user exists...")
        ensure_admin_exists(db)

        print("Database initialization complete.")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
