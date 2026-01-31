"""
Script to initialize default KPIs.
Idempotent: will not create duplicates if run multiple times.

Usage:
    python -m scripts.init_kpis
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import KPI


# Default KPIs to seed
DEFAULT_KPIS = [
    {
        "code": "CS",
        "label": "Capital Services",
        "unit": "trx"
    },
    {
        "code": "RIA",
        "label": "RIA (Remesas Internacionales)",
        "unit": "units"
    },
    {
        "code": "MG",
        "label": "MoneyGram",
        "unit": "units"
    },
    {
        "code": "CORNERS",
        "label": "Corners (Puntos de Venta)",
        "unit": "units"
    },
]


def seed_kpis():
    """
    Seed the database with default KPIs.
    Idempotent: skips KPIs that already exist (by code).
    """
    db = SessionLocal()
    try:
        print("Seeding KPIs...")
        created_count = 0
        skipped_count = 0

        for kpi_data in DEFAULT_KPIS:
            # Check if KPI already exists
            existing = db.query(KPI).filter(KPI.code == kpi_data["code"]).first()

            if existing:
                print(f"  [SKIP] KPI '{kpi_data['code']}' already exists (id={existing.id})")
                skipped_count += 1
            else:
                # Create new KPI
                new_kpi = KPI(
                    code=kpi_data["code"],
                    label=kpi_data["label"],
                    unit=kpi_data["unit"],
                    active=True
                )
                db.add(new_kpi)
                print(f"  [CREATE] KPI '{kpi_data['code']}' created")
                created_count += 1

        db.commit()
        print(f"\nDone! Created: {created_count}, Skipped: {skipped_count}")

    except Exception as e:
        db.rollback()
        print(f"Error seeding KPIs: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_kpis()
