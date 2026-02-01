from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.orm import KPI

def list_kpis(db: Session, active_only: bool = True) -> List[KPI]:
    query = db.query(KPI)
    if active_only:
        query = query.filter(KPI.active == True)
    return query.order_by(KPI.code).all()

def get_kpi_by_id(db: Session, kpi_id: int) -> Optional[KPI]:
    return db.query(KPI).filter(KPI.id == kpi_id).first()

def get_kpi_by_code(db: Session, code: str) -> Optional[KPI]:
    return db.query(KPI).filter(KPI.code == code).first()

def get_kpis_dict(db: Session) -> dict:
    kpis = list_kpis(db, active_only=True)
    return {kpi.id: kpi for kpi in kpis}

def seed_kpis(db: Session) -> None:
    from app.utils.constants import DEFAULT_KPIS

    for kpi_data in DEFAULT_KPIS:
        existing = db.query(KPI).filter(KPI.code == kpi_data["code"]).first()
        if not existing:
            kpi = KPI(
                code=kpi_data["code"],
                label=kpi_data["label"],
                unit=kpi_data["unit"],
                active=True
            )
            db.add(kpi)

    db.commit()
