from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.orm import Agency, AgencyManager, AgencyKPI, KPI

class AgencyServiceError(Exception):
    pass

def create_agency(
    db: Session,
    name: str,
    city: str,
    manager_name: str,
    manager_email: Optional[str] = None,
    manager_phone: Optional[str] = None,
    kpi_ids: Optional[List[int]] = None
) -> Agency:
    existing = db.query(Agency).filter(Agency.name == name).first()
    if existing:
        raise AgencyServiceError(f"Agency with name '{name}' already exists")

    agency = Agency(
        name=name,
        city=city,
        active=True
    )
    db.add(agency)
    db.flush()

    manager = AgencyManager(
        agency_id=agency.id,
        full_name=manager_name,
        email=manager_email,
        phone=manager_phone,
        start_date=date.today(),
        active=True
    )
    db.add(manager)

    if kpi_ids:
        for kpi_id in kpi_ids:
            agency_kpi = AgencyKPI(
                agency_id=agency.id,
                kpi_id=kpi_id,
                active=True
            )
            db.add(agency_kpi)

    db.commit()
    db.refresh(agency)
    return agency

def list_agencies(db: Session, active_only: bool = True) -> List[Dict[str, Any]]:
    query = db.query(Agency)
    if active_only:
        query = query.filter(Agency.active == True)

    agencies = query.order_by(Agency.name).all()
    result = []

    for agency in agencies:
        active_manager = db.query(AgencyManager).filter(
            AgencyManager.agency_id == agency.id,
            AgencyManager.active == True
        ).first()

        assigned_kpis = db.query(KPI).join(AgencyKPI).filter(
            AgencyKPI.agency_id == agency.id,
            AgencyKPI.active == True
        ).all()

        result.append({
            "id": agency.id,
            "name": agency.name,
            "city": agency.city,
            "active": agency.active,
            "created_at": agency.created_at,
            "manager": {
                "id": active_manager.id if active_manager else None,
                "full_name": active_manager.full_name if active_manager else None,
                "email": active_manager.email if active_manager else None,
                "phone": active_manager.phone if active_manager else None,
                "start_date": active_manager.start_date if active_manager else None,
                "end_date": active_manager.end_date if active_manager else None,
                "active": active_manager.active if active_manager else None,
            } if active_manager else None,
            "kpis": [{"id": k.id, "code": k.code, "label": k.label} for k in assigned_kpis]
        })

    return result

def get_agency_detail(db: Session, agency_id: int) -> Optional[Dict[str, Any]]:
    agency = db.query(Agency).filter(Agency.id == agency_id).first()
    if not agency:
        return None

    managers = db.query(AgencyManager).filter(
        AgencyManager.agency_id == agency_id
    ).order_by(AgencyManager.start_date.desc()).all()

    active_manager = next((m for m in managers if m.active), None)

    assigned_kpis = db.query(KPI).join(AgencyKPI).filter(
        AgencyKPI.agency_id == agency_id,
        AgencyKPI.active == True
    ).all()

    return {
        "id": agency.id,
        "name": agency.name,
        "city": agency.city,
        "active": agency.active,
        "created_at": agency.created_at,
        "active_manager": {
            "id": active_manager.id,
            "full_name": active_manager.full_name,
            "email": active_manager.email,
            "phone": active_manager.phone,
            "start_date": active_manager.start_date,
            "end_date": active_manager.end_date,
            "active": active_manager.active,
        } if active_manager else None,
        "manager_history": [
            {
                "id": m.id,
                "full_name": m.full_name,
                "email": m.email,
                "phone": m.phone,
                "start_date": m.start_date,
                "end_date": m.end_date,
                "active": m.active
            } for m in managers
        ],
        "kpis": [{"id": k.id, "code": k.code, "label": k.label, "unit": k.unit} for k in assigned_kpis]
    }

def get_agency_kpis(db: Session, agency_id: int) -> List[KPI]:
    return db.query(KPI).join(AgencyKPI).filter(
        AgencyKPI.agency_id == agency_id,
        AgencyKPI.active == True
    ).order_by(KPI.code).all()

def update_agency_kpis(db: Session, agency_id: int, kpi_ids: List[int]) -> None:
    current = db.query(AgencyKPI).filter(
        AgencyKPI.agency_id == agency_id
    ).all()

    current_kpi_ids = {ak.kpi_id for ak in current}
    new_kpi_ids = set(kpi_ids)

    for ak in current:
        if ak.kpi_id not in new_kpi_ids:
            ak.active = False
        else:
            ak.active = True

    for kpi_id in new_kpi_ids - current_kpi_ids:
        agency_kpi = AgencyKPI(
            agency_id=agency_id,
            kpi_id=kpi_id,
            active=True
        )
        db.add(agency_kpi)

    db.commit()

def toggle_agency_active(db: Session, agency_id: int, active: bool) -> None:
    agency = db.query(Agency).filter(Agency.id == agency_id).first()
    if agency:
        agency.active = active
        db.commit()
